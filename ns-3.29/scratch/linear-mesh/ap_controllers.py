"""v3.7.0 (M2) model-free per-AP CW controllers used as baselines. No ns-3 / torch dependency.

KW  : distributed asynchronous Kiefer-Wolfowitz search on y = log(lam / (1 - lam)), lam = 2 / (CW + 1)
      (Gawlowicz, Walrand, Wolisz, arXiv 2102.05149, Algorithms 1-2; text read 2026-11-03). Each AP probes y + e*delta for
      tau, then y - e*delta for tau (e = +-1 random), g = (U+ - U-) / (2 e delta), y <- Pi(y + eta * g) onto
      [A + delta, B - delta] (A, B = y at CW 1024 and 16). Utility U = sum over audible BSSs j of n_j * ln(max(eps, x_j / n_j)).
      Deviations from the paper (labelled, not hidden):
        * AP level: the AP sets its BSS's CW (as OSCAR does); the paper has one CW per station.
        * Audible set comes from the hearing graph (--apHidden pairs), not from overheard frames; the per-BSS goodput is
          read from the trainer's rx counters. This is neighbour information, so it breaks ADR-0002 isolation by design.
        * The paper writes y - eta * g with a maximised utility; we ascend (+ eta * g). Inference: the minus sign belongs to a
          minimisation form of Algorithm 1 (not stated in the text).
        * U is weighted by BSS station count n_j and has the plan's eps = 0.01 Mbps; the paper sums ln of station throughputs.
        * Window tau = 200 ms and (delta, eta) = (0.2, 0.1) are the paper's values; CW range 16..1024 here (paper 15..1023).
        * Stations read CW as 2^k - 1 (cw.cc ECW = floor(log2(CW+1))), so probes smaller than an octave are invisible to
          them; the tuning sweep includes larger delta for that reason.
UCB : UCB1 over the CW exponents 4..10 (one arm per exponent), one pull per window of tau; reward = the AP's own goodput
      per STA normalised like the trainer reward (0..1). Our construction, not from a paper.
Both are driven by observe(recs) once per env step and expose cw_exponents() -> real action a in [0, 6] (CW = 2^(4+a)).
"""
import math

import numpy as np

PAYLOAD_BITS = (1500 - 20 - 8 - 8) * 8  # same as multi_ap.PAYLOAD_BITS (not imported: keeps this module dependency-free)
EPS_MBPS = 0.01
CW_MIN, CW_MAX = 16, 1024


def y_of_cw(cw):
    lam = 2.0 / (cw + 1.0)
    return math.log(lam / (1.0 - lam))


def cw_of_y(y):
    lam = 1.0 / (1.0 + math.exp(-y))
    return 2.0 / lam - 1.0


Y_LO, Y_HI = y_of_cw(CW_MAX), y_of_cw(CW_MIN)


def audible_sets(n_aps, hidden_pairs):
    """hidden_pairs: iterable of 1-based (a, b) AP pairs that cannot hear each other. Returns per-AP lists of 0-based BSS
    indices the AP can hear, itself included."""
    hid = {frozenset((a - 1, b - 1)) for a, b in hidden_pairs}
    return [[j for j in range(n_aps) if j == i or frozenset((i, j)) not in hid] for i in range(n_aps)]


def parse_hidden(arg):
    """'1-3,2-4' -> [(1, 3), (2, 4)]; '' -> []."""
    return [tuple(int(v) for v in p.split("-")) for p in arg.split(",") if p]


class _Window:
    """Accumulates per-AP rx counts over tau seconds of env steps."""

    def __init__(self, n_aps, steps):
        self.steps, self.k, self.rx = steps, 0, np.zeros(n_aps)

    def add(self, rx):
        self.rx += rx
        self.k += 1
        return self.k >= self.steps

    def take(self, step_time):
        mbps = self.rx * PAYLOAD_BITS / (self.k * step_time * 1e6)
        self.k, self.rx = 0, np.zeros_like(self.rx)
        return mbps


class KW:
    def __init__(self, counts, hidden_pairs, step_time=0.01, tau=0.2, delta=0.2, eta=0.1, cw0=16, seed=0):
        self.n, self.counts = len(counts), np.asarray(counts, dtype=np.float64)
        self.aud = audible_sets(self.n, hidden_pairs)
        self.step_time, self.delta, self.eta = step_time, delta, eta
        self.tau_steps = max(1, int(round(tau / step_time)))
        rng = np.random.RandomState(seed)
        self.rng = rng
        self.y = np.full(self.n, y_of_cw(cw0))
        self.eps = rng.choice([-1, 1], size=self.n)
        self.phase = rng.randint(0, self.tau_steps, size=self.n)  # uncoordinated start: p_i in [0, tau)
        self.stage = np.zeros(self.n, dtype=int)  # 0 = probe +, 1 = probe -
        self.u_plus = np.zeros(self.n)
        self.age = np.zeros(self.n, dtype=int)  # steps since this AP's current probe window began (after its phase offset)
        self.t = 0
        self.cw = np.array([cw_of_y(v) for v in self.y])
        self.sum_rx = np.zeros((self.n, self.n))  # [i, j] = rx of BSS j accumulated in AP i's current window
        self.updates = 0

    def _utility(self, i, sum_rx_row):
        x = sum_rx_row * PAYLOAD_BITS / (self.tau_steps * self.step_time * 1e6)
        j = self.aud[i]
        return float(sum(self.counts[b] * math.log(max(EPS_MBPS, x[b] / self.counts[b])) for b in j))

    def observe(self, recs):
        """Call once per env step with parse_ap_info output; advances every AP's probe schedule."""
        rx = np.array([r["rx"] for r in recs], dtype=np.float64)
        self.t += 1
        for i in range(self.n):
            if self.t <= self.phase[i]:  # waiting for this AP's random phase offset; CW stays at the start value
                continue
            self.sum_rx[i] += rx
            self.age[i] += 1
            if self.age[i] < self.tau_steps:
                continue
            u = self._utility(i, self.sum_rx[i])
            self.sum_rx[i] = 0.0
            self.age[i] = 0
            if self.stage[i] == 0:
                self.u_plus[i] = u
                self.stage[i] = 1
            else:
                g = (self.u_plus[i] - u) / (2.0 * self.eps[i] * self.delta)
                lo, hi = Y_LO + self.delta, Y_HI - self.delta
                self.y[i] = min(hi, max(lo, self.y[i] + self.eta * g))
                self.eps[i] = self.rng.choice([-1, 1])
                self.stage[i] = 0
                self.updates += 1
            sign = 1.0 if self.stage[i] == 0 else -1.0
            self.cw[i] = cw_of_y(self.y[i] + sign * self.eps[i] * self.delta)
        self.cw = np.clip(self.cw, CW_MIN, CW_MAX)

    def cw_exponents(self):
        return np.clip(np.log2(self.cw) - 4.0, 0.0, 6.0).astype(np.float32)


class UCB:
    def __init__(self, counts, norm_loads, step_time=0.01, tau=0.2, c=0.3, seed=0):
        self.n, self.counts = len(counts), np.asarray(counts, dtype=np.float64)
        self.norm = np.asarray(norm_loads, dtype=np.float64)
        self.step_time, self.c = step_time, c
        self.win = _Window(self.n, max(1, int(round(tau / step_time))))
        self.rng = np.random.RandomState(seed)
        self.arms = list(range(4, 11))
        self.pulls = np.zeros((self.n, 7))
        self.mean = np.zeros((self.n, 7))
        self.cur = np.zeros(self.n, dtype=int)  # arm index per AP; the first 7 windows try each arm once in random order
        self.order = [self.rng.permutation(7) for _ in range(self.n)]
        self.t = 0
        self.cur[:] = [o[0] for o in self.order]

    def observe(self, recs):
        if not self.win.add(np.array([r["rx"] for r in recs], dtype=np.float64)):
            return
        mbps = self.win.take(self.step_time)
        reward = np.clip(mbps / (self.norm * self.counts), 0.0, 1.0)
        self.t += 1
        for i in range(self.n):
            a = self.cur[i]
            self.pulls[i, a] += 1
            self.mean[i, a] += (reward[i] - self.mean[i, a]) / self.pulls[i, a]
            if self.t < 7:
                self.cur[i] = self.order[i][self.t]
            else:
                bonus = self.c * np.sqrt(2.0 * math.log(self.t) / self.pulls[i])
                self.cur[i] = int(np.argmax(self.mean[i] + bonus))

    def cw_exponents(self):
        return np.array([self.arms[a] - 4 for a in self.cur], dtype=np.float32)


def ctx_bucket(active):
    """UCBCtx context: 0 for no active STA, else 1 + floor(log2(active)) capped at 6 (1, 2-3, 4-7, 8-15, 16-31, 32+)."""
    a = int(round(active))
    return 0 if a <= 0 else min(6, 1 + int(math.log2(a)))


class UCBCtx:
    """v3.8.0 (M2b) contextual UCB per AP: UCB1 statistics are kept per (context, arm); the context is the AP's number of
    active STAs (STAs whose data frames the AP decoded) averaged over the window that just ended, in log2 buckets
    (ctx_bucket). Same arms (CW exponents 4..10), window tau and reward as UCB. Motivation: the Wi-Fi MAB study (plan
    section on rivals) found context helps; the active-STA count as the context key is the plan's choice, not from a paper.
    Needs cw.cc --extraTraces (the `active` field). Our construction, not from a paper."""

    def __init__(self, counts, norm_loads, step_time=0.01, tau=0.2, c=0.3, seed=0):
        self.n, self.counts = len(counts), np.asarray(counts, dtype=np.float64)
        self.norm = np.asarray(norm_loads, dtype=np.float64)
        self.step_time, self.c = step_time, c
        self.steps = max(1, int(round(tau / step_time)))
        self.k, self.rx, self.act = 0, np.zeros(self.n), np.zeros(self.n)
        self.rng = np.random.RandomState(seed)
        self.arms = list(range(4, 11))
        self.pulls = np.zeros((self.n, 7, 7))  # [ap, context, arm]
        self.mean = np.zeros((self.n, 7, 7))
        self.ctx = np.zeros(self.n, dtype=int)  # context the current arm was chosen in (0 before the first window)
        self.cur = self.rng.randint(0, 7, size=self.n)
        self.t_ctx = np.zeros((self.n, 7))  # pulls per context

    def observe(self, recs):
        self.rx += np.array([r["rx"] for r in recs], dtype=np.float64)
        self.act += np.array([r["active"] for r in recs], dtype=np.float64)
        self.k += 1
        if self.k < self.steps:
            return
        mbps = self.rx * PAYLOAD_BITS / (self.k * self.step_time * 1e6)
        reward = np.clip(mbps / (self.norm * self.counts), 0.0, 1.0)
        new_ctx = [ctx_bucket(a / self.k) for a in self.act]
        self.k, self.rx, self.act = 0, np.zeros(self.n), np.zeros(self.n)
        for i in range(self.n):
            c0, a = self.ctx[i], self.cur[i]
            self.pulls[i, c0, a] += 1
            self.t_ctx[i, c0] += 1
            self.mean[i, c0, a] += (reward[i] - self.mean[i, c0, a]) / self.pulls[i, c0, a]
            c1 = new_ctx[i]
            untried = np.flatnonzero(self.pulls[i, c1] == 0)
            if len(untried):  # try every arm once in this context first, in random order
                self.cur[i] = int(self.rng.choice(untried))
            else:
                bonus = self.c * np.sqrt(2.0 * math.log(max(2.0, self.t_ctx[i, c1])) / self.pulls[i, c1])
                self.cur[i] = int(np.argmax(self.mean[i, c1] + bonus))
            self.ctx[i] = c1

    def cw_exponents(self):
        return np.array([self.arms[a] - 4 for a in self.cur], dtype=np.float32)


def dac_gains(p_col, m=6):
    """Patras, Banchs, Serrano, Azcorra, IEEE TMC 10(6) 2011, Eq. 47-49 (typeset PDF read 2026-11-11):
    Kp = 0.4 * Ku, Ku = 2 / (p^2 (1 + p sum_{k=0..m} (2p)^k)), Ki = Kp / (0.85 Ti) with Ti = 2. m = max backoff stage (16..1024 -> 6)."""
    d = p_col ** 2 * (1.0 + p_col * sum((2.0 * p_col) ** k for k in range(m + 1)))
    ku = 2.0 / d
    kp = 0.4 * ku
    return kp, kp / (0.85 * 2.0)


def dac_pcol(te, tc):
    """Eq. 20: p_col = 1 - exp(-sqrt(2 Te / Tc))."""
    return 1.0 - math.exp(-math.sqrt(2.0 * te / tc))


class DAC:
    """v3.8.0 (M2b) Patras et al. DAC, one PI controller per AP (TMC 2011, Sec. 3, Eq. 2-5, 23, 25, 47-49).
    Error e = 2 p_others - p_own - p_col; CWmin(k) = Kp e(k) + S(k), S(k+1) = S(k) + Ki e(k) (C_PI(z) = Kp + Ki/(z-1));
    CW limited to [16, 1024]; update once per beacon interval (0.1 s), deferred while the window holds fewer than 20 samples.
    p_own = F / (F + T) (Eq. 4) and p_others = R / (R + S) (Eq. 5) are read from cw.cc --extraTraces:
    F = failed data attempts in the BSS (`txfail`), T = `rx`, retry share = `retry` per step weighted by `rx`.
    Deviations (labelled): (1) AP level: the paper runs one controller per station on that station's own counters; here one
    controller per BSS uses BSS-aggregate counters, so p_own and p_others are both BSS-wide and the fairness term is about zero;
    (2) the integrator is clamped to [16, 1024] (anti-windup; the paper clamps the output); (3) start CW = cw0 (not stated in
    the paper); (4) Te / Tc come from the HE 20 MHz MCS 11 timing computed in docs/results/m2b-specs-v4.0.0.md (inference),
    not from the paper's 802.11g values."""

    def __init__(self, n_aps, step_time=0.01, beacon=0.1, te=9e-6, tc=257e-6, cw0=16.0, p_col=0.0, min_samples=20):
        self.n = n_aps
        self.p_col = p_col if p_col > 0 else dac_pcol(te, tc)
        self.kp, self.ki = dac_gains(self.p_col)
        self.steps = max(1, int(round(beacon / step_time)))
        self.min_samples = min_samples
        self.s = np.full(n_aps, float(cw0))
        self.cw = np.full(n_aps, float(cw0))
        self.k = 0
        self.t_ok = np.zeros(n_aps)   # successes T (= S + R frames)
        self.fail = np.zeros(n_aps)   # failed attempts F
        self.retry = np.zeros(n_aps)  # frames with the retry bit set R
        self.updates = 0

    def observe(self, recs):
        for i, r in enumerate(recs):
            self.t_ok[i] += r["rx"]
            self.fail[i] += r["txfail"]
            self.retry[i] += r["retry"] * r["rx"]
        self.k += 1
        if self.k < self.steps:
            return
        self.k = 0
        for i in range(self.n):
            samples_own, samples_oth = self.fail[i] + self.t_ok[i], self.t_ok[i]
            if samples_own < self.min_samples or samples_oth < self.min_samples:
                continue  # deferred: keep accumulating until the next beacon
            p_own = self.fail[i] / samples_own
            p_oth = self.retry[i] / samples_oth
            e = 2.0 * p_oth - p_own - self.p_col
            self.cw[i] = min(CW_MAX, max(CW_MIN, self.kp * e + self.s[i]))
            self.s[i] = min(CW_MAX, max(CW_MIN, self.s[i] + self.ki * e))
            self.t_ok[i] = self.fail[i] = self.retry[i] = 0.0
            self.updates += 1

    def cw_exponents(self):
        return np.clip(np.log2(self.cw) - 4.0, 0.0, 6.0).astype(np.float32)


def model_static_cw(n_stas, te=9e-6, tc=257e-6):
    """Patras Eq. 18 with tau ~ 2 / (CW + 1): tau_opt = (1/n) sqrt(2 Te / Tc), CW = 2 / tau_opt - 1, clipped to [16, 1024].
    n = the AP's own number of STAs (local n, plan decision), Te / Tc as in DAC."""
    tau = (1.0 / n_stas) * math.sqrt(2.0 * te / tc)
    return float(min(CW_MAX, max(CW_MIN, 2.0 / tau - 1.0)))
