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
