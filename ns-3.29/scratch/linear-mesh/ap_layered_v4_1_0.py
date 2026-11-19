"""v4.1.0 (max-CW plan, Track B): layered online CW controllers. No ns-3 / torch dependency.

  L1  DACw     per-AP PI loop (the DAC of ap_controllers.py, Patras et al. 2011) that drives the AP's collision signal to a
               TARGET p_i and writes the AP's CW; the CW range is the wide one (--cwLo/--cwHi, default 4..32767).
  L2  KWPlus   writes L1's targets: p_i = p0 * 2^(-theta_i), theta_i = c + o_i (common level + per-AP offsets).
               Simultaneous-perturbation (SPSA) ascent on the station-weighted alpha-fair utility of the per-AP goodput,
               one window `tau` per probe; offsets are shrunk towards 0 at every update; a guard compares the utility after
               the step with the best seen and reverts the step (and halves the step size) when it is worse by more than
               `tol` (relative).
  L3  Coordinated   (only after Gate S, which passed on S4 at alpha 1): a max-weight coordinator picks, every `period` steps,
               the maximal set of BSSs that do not hear each other with the largest sum of weights n_i / max(x_i, eps)
               (proportional-fair weights on an EMA of the per-AP goodput); BSSs outside the set are muted at CW `mute`.

Phase 1 additions (2026-11-19): floor guard (L2 subtracts mu * sum_i max(0, 1 - x_i / floor_i) from its utility; L3 keeps per-AP
virtual queues q_i that grow by (floor_i - x_i) / floor_i per decision while AP i is under its floor and add beta * q_i to its
weight, so the schedule duty-cycles towards the APs that are short); QCsma (local variant: an AP is active iff its weight is the
largest among the APs it hears); PageHinkley change detector (resets the L2 step and the L3 queues); KWDirect (L2 writes the CW
itself, no L1).
Cascade = L1 + L2, Coordinated = L1 + L2 + L3. Both expose observe(recs) once per env step and cw_exponents() -> a with
CW = 2^(4 + a) (a in [-2, 11] for CW 4..32767), the convention of ap_controllers.py. Neighbour information: L2 uses the
goodput of every BSS (as KW does in ap_controllers.py) and L3 uses the hearing graph; this breaks ADR-0002 isolation
by design and is reported as such (class A online, shared information level "network goodput").
Labelled deviations from the paper DAC: AP-level counters (see ap_controllers.DAC); the integrator and the output are
clamped to [cw_lo, cw_hi] instead of [16, 1024]; the target p_i is an input.
"""
import itertools
import math

import numpy as np

from ap_controllers import PAYLOAD_BITS, dac_gains, dac_pcol

EPS_MBPS = 0.01


def u_alpha(x, alpha):
    if alpha == 1:
        return math.log(x)
    if alpha == 0:
        return x
    return x ** (1.0 - alpha) / (1.0 - alpha)


def utility(mbps, counts, alpha):
    """Station-weighted alpha-fair utility, the same as gc_analysis.utility."""
    return float(sum(n * u_alpha(max(EPS_MBPS, x / n), alpha) for x, n in zip(mbps, counts)))


class PageHinkley:
    """Two-sided Page-Hinkley test on a scalar stream, one per stream, normalised by a running mean. A change is signalled when the
    cumulative drift from the running mean exceeds `lam` (relative to the mean) beyond a tolerance `delta` (relative)."""

    def __init__(self, n, delta=0.05, lam=3.0, warm=50):
        self.n, self.delta, self.lam, self.warm = n, delta, lam, warm
        self.reset()

    def reset(self):
        self.k = 0
        self.mean = np.zeros(self.n)
        self.up = np.zeros(self.n)
        self.dn = np.zeros(self.n)

    def update(self, v):
        """v: array of length n. Returns True when any stream changed (and resets)."""
        v = np.asarray(v, dtype=np.float64)
        self.k += 1
        self.mean += (v - self.mean) / self.k
        if self.k <= self.warm:
            return False
        scale = np.maximum(self.mean, 1e-9)
        d = (v - self.mean) / scale
        self.up = np.maximum(0.0, self.up + d - self.delta)
        self.dn = np.maximum(0.0, self.dn - d - self.delta)
        if (self.up > self.lam).any() or (self.dn > self.lam).any():
            self.reset()
            return True
        return False


def independent_sets(n, hidden_pairs):
    """Maximal sets of BSSs that can be active together (every pair hidden from each other). hidden_pairs: 1-based."""
    hid = {frozenset((a - 1, b - 1)) for a, b in hidden_pairs}
    ok = lambda s: all(frozenset(p) in hid for p in itertools.combinations(s, 2))
    sets = [frozenset(s) for r in range(1, n + 1) for s in itertools.combinations(range(n), r) if ok(s)]
    return [s for s in sets if not any(s < t for t in sets)]


class DACw:
    """L1: one PI loop per AP towards a per-AP target collision signal p_target[i] (set by L2)."""

    def __init__(self, n_aps, step_time=0.01, beacon=0.1, te=9e-6, tc=242e-6, cw0=64.0, cw_lo=4.0, cw_hi=32767.0, min_samples=20):
        self.n, self.cw_lo, self.cw_hi, self.min_samples = n_aps, float(cw_lo), float(cw_hi), min_samples
        self.p0 = dac_pcol(te, tc)
        self.p_target = np.full(n_aps, self.p0)
        self.steps = max(1, int(round(beacon / step_time)))
        self.s = np.full(n_aps, float(cw0))
        self.cw = np.full(n_aps, float(cw0))
        self.k = 0
        self.t_ok = np.zeros(n_aps)
        self.fail = np.zeros(n_aps)
        self.retry = np.zeros(n_aps)
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
            own, oth = self.fail[i] + self.t_ok[i], self.t_ok[i]
            if own < self.min_samples or oth < self.min_samples:
                continue
            p_own, p_oth = self.fail[i] / own, self.retry[i] / oth
            kp, ki = dac_gains(float(self.p_target[i]))
            e = 2.0 * p_oth - p_own - self.p_target[i]
            self.cw[i] = min(self.cw_hi, max(self.cw_lo, kp * e + self.s[i]))
            self.s[i] = min(self.cw_hi, max(self.cw_lo, self.s[i] + ki * e))
            self.t_ok[i] = self.fail[i] = self.retry[i] = 0.0
            self.updates += 1


class KWPlus:
    """L2: SPSA on theta = c + o with shrinkage and an accept/revert guard. See the module docstring."""

    def __init__(self, counts, step_time=0.01, tau=0.3, alpha=1.0, delta=0.35, eta=0.25, shrink=0.05, tol=0.02,
                 theta_lim=4.0, step_cap=0.5, seed=0, floors=None, floor_mu=20.0):
        self.floors = None if floors is None else np.asarray(floors, dtype=np.float64)
        self.mu = floor_mu
        self.n, self.counts = len(counts), np.asarray(counts, dtype=np.float64)
        self.tau_steps = max(1, int(round(tau / step_time)))
        self.step_time, self.alpha, self.delta, self.eta = step_time, alpha, delta, eta
        self.shrink, self.tol, self.lim, self.cap = shrink, tol, theta_lim, step_cap
        self.rng = np.random.RandomState(seed)
        self.c, self.o = 0.0, np.zeros(self.n)           # common level, offsets
        self.rx = np.zeros(self.n)
        self.k = 0
        self.stage = "base"                                # base -> plus -> minus -> (update) -> check -> base ...
        self.dir = self._draw()                            # +-1 per coordinate: [common, offsets...]
        self.u_plus = 0.0
        self.best_u, self.best = None, (0.0, np.zeros(self.n))
        self.prev = (0.0, np.zeros(self.n))
        self.updates = self.reverts = 0

    def restart(self, eta):
        """Change detector hook: forget the best seen and the offsets, restore the step size."""
        self.o[:] = 0.0
        self.best_u, self.best = None, (self.c, self.o.copy())
        self.eta = eta
        self.stage = "base"
        self.k = 0
        self.rx[:] = 0.0

    def _draw(self):
        return self.rng.choice([-1.0, 1.0], size=self.n + 1)

    def theta(self):
        """Per-AP log2 multiplier on the target collision probability, including the current probe."""
        t = self.c + self.o
        if self.stage == "plus":
            t = t + self.delta * (self.dir[0] + self.dir[1:])
        elif self.stage == "minus":
            t = t - self.delta * (self.dir[0] + self.dir[1:])
        return np.clip(t, -self.lim, self.lim)

    def observe(self, recs):
        self.rx += np.array([r["rx"] for r in recs], dtype=np.float64)
        self.k += 1
        if self.k < self.tau_steps:
            return
        mbps = self.rx * PAYLOAD_BITS / (self.k * self.step_time * 1e6)
        self.rx[:] = 0.0
        self.k = 0
        u = utility(mbps, self.counts, self.alpha)
        if self.floors is not None:                          # floor guard: relative shortfall below the floor, summed over the APs
            u -= self.mu * float(np.maximum(0.0, 1.0 - mbps / self.floors).sum())
        if self.stage == "base":
            if self.best_u is None:
                self.best_u, self.best = u, (self.c, self.o.copy())
            self.stage = "plus"
        elif self.stage == "plus":
            self.u_plus = u
            self.stage = "minus"
        elif self.stage == "minus":
            g = (self.u_plus - u) / (2.0 * self.delta)     # directional derivative along dir; SPSA gradient = g * dir
            self.prev = (self.c, self.o.copy())
            step = np.clip(self.eta * g * self.dir, -self.cap, self.cap)
            self.c = float(np.clip(self.c + step[0], -self.lim, self.lim))
            self.o = np.clip(self.o + step[1:], -self.lim, self.lim) * (1.0 - self.shrink)
            self.dir = self._draw()
            self.updates += 1
            self.stage = "check"
        else:                                               # check: utility after the step vs the best so far
            scale = max(1.0, abs(self.best_u))
            if u < self.best_u - self.tol * scale:
                self.c, self.o = self.best[0], self.best[1].copy()
                self.eta *= 0.5
                self.reverts += 1
            else:
                if u > self.best_u:
                    self.best_u, self.best = u, (self.c, self.o.copy())
            self.stage = "plus"


class Cascade:
    """L1 + L2."""

    def __init__(self, counts, step_time=0.01, beacon=0.1, te=9e-6, tc=242e-6, cw0=64.0, cw_lo=4.0, cw_hi=32767.0,
                 tau=0.3, alpha=1.0, delta=0.35, eta=0.25, shrink=0.05, tol=0.02, seed=0, floors=None, floor_mu=20.0, detect=False):
        self.n = len(counts)
        self.l1 = DACw(self.n, step_time, beacon, te, tc, cw0, cw_lo, cw_hi)
        self.l2 = KWPlus(counts, step_time, tau, alpha, delta, eta, shrink, tol, seed=seed, floors=floors, floor_mu=floor_mu)
        self.eta0 = eta
        self.det = PageHinkley(2 * self.n) if detect else None
        self.changes = 0
        self.cw_lo, self.cw_hi = cw_lo, cw_hi
        self.p_min, self.p_max = 0.005, 0.6

    def _detect(self, recs):
        """Page-Hinkley on per-AP goodput and active STAs; True on a change."""
        if self.det is None:
            return False
        v = [r["rx"] for r in recs] + [r.get("active", 0) for r in recs]
        if self.det.update(v):
            self.changes += 1
            self.l2.restart(self.eta0)
            return True
        return False

    def observe(self, recs):
        self._detect(recs)
        self.l2.observe(recs)
        self.l1.p_target = np.clip(self.l1.p0 * np.exp2(-self.l2.theta()), self.p_min, self.p_max)
        self.l1.observe(recs)

    def cw(self):
        return np.clip(self.l1.cw, self.cw_lo, self.cw_hi)

    def cw_exponents(self):
        return (np.log2(self.cw()) - 4.0).astype(np.float32)


class Coordinated(Cascade):
    """L1 + L2 + L3 (max-weight muting). `period` env steps per decision, `mute` = CW of a muted BSS."""

    def __init__(self, counts, hidden_pairs, period=20, mute=8192.0, ema=0.05, hold_all=3, beta=0.5, **kw):
        super().__init__(counts, **kw)
        fl = kw.get("floors")
        self.floors = None if fl is None else np.asarray(fl, dtype=np.float64)
        self.beta = beta
        self.q = np.zeros(self.n)                          # virtual queues: accumulated relative floor shortfall
        self.xp = np.zeros(self.n)                         # goodput of the current period, Mbps
        self.counts = np.asarray(counts, dtype=np.float64)
        self.sets = independent_sets(self.n, hidden_pairs)
        self.period, self.mute, self.ema = period, float(mute), ema
        self.x = np.full(self.n, 1.0)                      # EMA of per-AP goodput in Mbps (after the first window)
        self.t, self.active = 0, set(range(self.n))
        self.step_time = kw.get("step_time", 0.01)
        self.hold_all = hold_all                           # the first hold_all periods run unmuted (the EMA warms up)
        self.decisions = 0

    def observe(self, recs):
        rx = np.array([r["rx"] for r in recs], dtype=np.float64)
        super().observe(recs)
        mbps = rx * PAYLOAD_BITS / (self.step_time * 1e6)
        self.x = (1.0 - self.ema) * self.x + self.ema * mbps
        self.xp += mbps / self.period
        self.t += 1
        if self.det is not None and self.changes != getattr(self, "_seen", 0):
            self._seen = self.changes                      # L3 forgets its queues and warms up again after a change
            self.q[:] = 0.0
            self.decisions = 0
        if self.t % self.period:
            return
        if self.floors is not None:
            self.q = np.maximum(0.0, self.q + (self.floors - self.xp) / self.floors)
        self.xp[:] = 0.0
        self.decisions += 1
        if self.decisions <= self.hold_all or len(self.sets) < 2:
            self.active = set(range(self.n))
            return
        w = self._weights()
        best = max(self.sets, key=lambda s: (sum(w[i] for i in s), -len(s)))
        self.active = set(best)

    def _weights(self):
        """Marginal utility of one unit of service of BSS i: d/dx_i [n_i u(x_i / n_i)] = (x_i / n_i)^(-alpha); alpha 1 is the PF weight
        n_i / x_i. With floors, the virtual queues add beta * q_i in units of the mean weight."""
        w = (np.maximum(self.x, EPS_MBPS) / self.counts) ** (-self.l2.alpha)
        if self.floors is not None:
            w = w + self.beta * self.q * float(np.mean(w))
        return w

    def cw(self):
        cw = super().cw().copy()
        for i in range(self.n):
            if i not in self.active:
                cw[i] = min(self.cw_hi, self.mute)
        return cw


class QCsma:
    """Local variant of L3 (Q-CSMA style): every `period` steps each AP compares its own weight n_i / x_i (+ floor queue) with the
    weights of the BSSs it can hear and joins the active set in rounds when it is the largest of the undecided ones it hears (ties: the lower
    index), which gives a maximal independent set. L1 + L2 write the
    CW as in Coordinated. Information: own and audible-neighbour goodput only (class A online, neighbour-local)."""

    def __init__(self, counts, hidden_pairs, period=20, mute=8192.0, ema=0.05, hold_all=3, beta=0.5, **kw):
        from ap_controllers import audible_sets
        self.base = Coordinated(counts, hidden_pairs, period, mute, ema, hold_all, beta, **kw)
        self.aud = audible_sets(len(counts), hidden_pairs)
        self.n = len(counts)

    def observe(self, recs):
        b = self.base
        was = b.decisions
        b.observe(recs)
        if b.t % b.period or b.decisions <= b.hold_all or b.decisions == was:
            return
        w = b._weights()
        undecided, active = set(range(self.n)), set()
        while undecided:                                   # rounds of local maxima among the undecided (a maximal independent set)
            win = {i for i in undecided if all((w[i], -i) > (w[j], -j) for j in self.aud[i] if j != i and j in undecided)}
            active |= win
            undecided -= win | {j for i in win for j in self.aud[i]}
        b.active = active

    def cw(self):
        return self.base.cw()

    def cw_exponents(self):
        return self.base.cw_exponents()


class KWDirect:
    """KW+ direct: L2 (SPSA on theta = c + o with shrinkage, guard and floor guard) writes the CW itself, CW_i = cw0 * 2^theta_i,
    no L1. theta limit 8 covers CW 4..32767 from cw0 64 (log2 range -4..+9)."""

    def __init__(self, counts, step_time=0.01, tau=0.3, alpha=1.0, delta=0.35, eta=0.25, shrink=0.05, tol=0.02, cw0=64.0,
                 cw_lo=4.0, cw_hi=32767.0, seed=0, floors=None, floor_mu=20.0):
        self.l2 = KWPlus(counts, step_time, tau, alpha, delta, eta, shrink, tol, theta_lim=8.0, seed=seed, floors=floors, floor_mu=floor_mu)
        self.cw0, self.cw_lo, self.cw_hi = cw0, cw_lo, cw_hi

    def observe(self, recs):
        self.l2.observe(recs)

    def cw(self):
        return np.clip(self.cw0 * np.exp2(self.l2.theta()), self.cw_lo, self.cw_hi)

    def cw_exponents(self):
        return (np.log2(self.cw()) - 4.0).astype(np.float32)
