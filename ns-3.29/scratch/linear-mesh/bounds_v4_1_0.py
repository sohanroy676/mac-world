"""v4.1.0 (max-CW plan, Track A): time-sharing bounds on the station-weighted alpha-fair utility of one cell.

  python bounds_v4_1_0.py --topo 10,10,10 --hidden 1-3 --caps 71.6 [--loads 150,150,1 | --load 10] [--floors 3.1,0.4,3.1]
  python bounds_v4_1_0.py --selftest

Model (docs/design/measurement-modes-v4.1.0.md, section Bounds). BSSs are the nodes of a conflict graph: two BSSs
conflict unless the pair is in --hidden (cw.cc --apHidden isolates the whole BSS pair). A schedule gives each
independent set S of the graph a time share theta_S >= 0, sum theta_S = 1. BSS i then carries

  x_i <= c_i * sum_{S contains i} theta_S      (c_i = --caps, Mbps the BSS carries while it is active)
  x_i <= d_i = n_i * load_i                    (offered load)
  x_i >= (1 - floorTol) * floor_i              (only with --floors: the fair floor of gc_analysis.py)

and the bound is max U_alpha(x), U_alpha as in gc_analysis.utility. What the result means depends on c_i:
  * c_i = payload / (AIFS + T_data + SIFS + T_ack), frame exchanges back to back with no backoff and no collision:
    "scheduled-access bound". It bounds every CW policy as long as two conflicting BSSs never both succeed at once
    (no capture) and every success costs at least that time. ASSUMPTION, stated with the result.
  * c_i = best measured throughput of BSS i alone (isolated single-BSS static search): "independent-set reference".
    It is what perfect coordination between BSSs would give if each BSS still contends internally. It is a reference,
    NOT an upper bound: a policy can beat it when concurrent contention is cheaper than the model assumes.

Analysis-only script: needs numpy and scipy (not part of the run image). alpha 0 is a linear program; other alphas are
solved with SLSQP from several starts and the best feasible point is kept.
"""
import argparse
import itertools
import sys

import numpy as np

EPS = 0.01  # Mbps per station inside u_alpha, as gc_analysis.EPS


def u_alpha(x, alpha):
    if alpha == 0:
        return x
    if alpha == 1:
        return np.log(x)
    return x ** (1 - alpha) / (1 - alpha)


def utility(x, counts, alpha):
    return float(sum(n * u_alpha(max(EPS, xi / n), alpha) for xi, n in zip(x, counts)))


def parse_hidden(txt, n):
    pairs = set()
    for tok in filter(None, txt.split(",")):
        a, b = (int(v) - 1 for v in tok.split("-"))
        assert 0 <= a < n and 0 <= b < n and a != b, "--hidden: 1-based AP pairs like 1-3"
        pairs.add((min(a, b), max(a, b)))
    return pairs


def maximal_independent_sets(n, hidden):
    """Sets of BSSs that can be active together: every pair inside a set is hidden from each other."""
    ok = lambda s: all((a, b) in hidden for a, b in itertools.combinations(s, 2))
    sets = [frozenset(s) for r in range(1, n + 1) for s in itertools.combinations(range(n), r) if ok(s)]
    return [s for s in sets if not any(s < t for t in sets)]


def solve(counts, hidden, caps, demand, alpha, floors=None, floor_tol=0.05):
    """Returns (U, x, shares) or None when the floors cannot be met. shares = {tuple(set): theta}."""
    from scipy.optimize import linprog, minimize

    n = len(counts)
    sets = maximal_independent_sets(n, hidden)
    k = len(sets)
    A = np.array([[1.0 if i in s else 0.0 for s in sets] for i in range(n)])  # n x k membership
    lo = np.array([(1 - floor_tol) * f for f in floors]) if floors else np.zeros(n)
    hi = np.array(demand, dtype=float)
    if np.any(lo > hi + 1e-12):
        return None
    # variables z = [theta (k), x (n)];  x_i - c_i (A theta)_i <= 0;  sum theta = 1
    A_ub = np.hstack([-(np.array(caps)[:, None] * A), np.eye(n)])
    b_ub = np.zeros(n)
    A_eq = np.hstack([np.ones((1, k)), np.zeros((1, n))])
    bounds = [(0.0, 1.0)] * k + list(zip(lo, hi))
    lp = linprog(-np.concatenate([np.zeros(k), np.ones(n)]), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[1.0], bounds=bounds, method="highs")
    if lp.status != 0:
        return None
    best = lp.x
    if alpha != 0:
        cn = np.array(counts, dtype=float)

        def neg_u(z):
            return -float(np.sum(cn * u_alpha(np.maximum(EPS, z[k:] / cn), alpha)))

        cons = [{"type": "ineq", "fun": lambda z: b_ub - A_ub @ z, "jac": lambda z: -A_ub},
                {"type": "eq", "fun": lambda z: A_eq @ z - 1.0, "jac": lambda z: A_eq}]
        starts = [lp.x]
        for theta in list(np.eye(k)) + [np.full(k, 1.0 / k)]:  # each set alone, and equal shares
            x0 = np.clip(0.999 * np.array(caps) * (A @ theta), lo, hi)
            starts.append(np.concatenate([theta, x0]))
        best_val = None
        for z0 in starts:
            r = minimize(neg_u, z0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 500, "ftol": 1e-12})
            z = r.x
            feas = np.all(A_ub @ z <= 1e-7) and abs(z[:k].sum() - 1) <= 1e-7 and np.all(z[k:] >= lo - 1e-7) and np.all(z[k:] <= hi + 1e-7)
            if feas and (best_val is None or -neg_u(z) > best_val):
                best_val, best = -neg_u(z), z
        if best_val is None:
            return None
    x = best[k:]
    return utility(x, counts, alpha), x, {tuple(sorted(i + 1 for i in s)): float(t) for s, t in zip(sets, best[:k])}


def selftest():
    """Known answers. Chain 1-2-3 with 1 and 3 hidden, equal BSSs, unlimited demand, capacity 1."""
    counts, hidden, caps, dem = [10, 10, 10], {(0, 2)}, [1.0] * 3, [1e9] * 3
    u, x, sh = solve(counts, hidden, caps, dem, 1)
    assert np.allclose(x, [2 / 3, 1 / 3, 2 / 3], atol=1e-4), x  # proportional fairness: time shares 2:1:2
    u, x, sh = solve(counts, hidden, caps, dem, 0)
    assert np.allclose(x, [1, 0, 1], atol=1e-6), x  # sum throughput: the middle BSS gets nothing
    u, x, sh = solve(counts, hidden, caps, dem, 0, floors=[0.2, 0.2, 0.2], floor_tol=0.0)
    assert np.allclose(x, [0.8, 0.2, 0.8], atol=1e-6), x  # with a floor the middle BSS gets exactly its floor
    u, x, sh = solve(counts, hidden, caps, dem, 2)
    t = 1 / (1 + 2 ** -0.5)  # alpha 2: maximise -(2/t + 1/(1-t)) -> t = sqrt2 / (1 + sqrt2)
    assert np.allclose(x, [t, 1 - t, t], atol=1e-4), (x, t)
    u, x, sh = solve([20, 40], set(), [90.0, 90.0], [1e9] * 2, 1)  # capacity 90: per-station rates stay above EPS
    assert np.allclose(x, [30, 60], atol=1e-2), x  # one domain: station-weighted shares 20:40
    u, x, sh = solve(counts, hidden, caps, [1e9, 1e9, 0.1], 1)
    assert np.allclose(x, [0.5, 0.5, 0.1], atol=1e-3), x  # BSS 3 demand-limited: BSS 1 and 2 share the time equally
    print("selftest: PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--topo", default="")
    ap.add_argument("--hidden", default="")
    ap.add_argument("--caps", default="", help="Mbps a BSS carries while active: one value, or one per AP")
    ap.add_argument("--loads", default="", help="per-STA offered load in Mbps per AP (cw.cc --apLoads)")
    ap.add_argument("--load", type=float, default=150.0, help="per-STA offered load in Mbps (cw.cc --offeredLoad)")
    ap.add_argument("--floors", default="", help="per-AP fair floors in Mbps (gc_analysis.floors of the BEB means); empty = no floor")
    ap.add_argument("--floorTol", type=float, default=0.05)
    ap.add_argument("--alphas", default="0,1,4")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    counts = [int(c) for c in args.topo.split(",")]
    n = len(counts)
    caps = [float(c) for c in args.caps.split(",")]
    caps = caps * n if len(caps) == 1 else caps
    loads = [float(v) for v in args.loads.split(",")] if args.loads else [args.load] * n
    assert len(caps) == n and len(loads) == n, "--caps/--loads: one value or one per AP"
    floors = [float(v) for v in args.floors.split(",")] if args.floors else None
    demand = [c * l for c, l in zip(counts, loads)]
    hidden = parse_hidden(args.hidden, n)
    print("topo %s hidden %s caps %s demand %s floors %s (tol %g)" % (args.topo, args.hidden or "-", caps, demand, floors or "-", args.floorTol))
    print("| alpha | U bound | x per AP (Mbps) | time shares |\n|---|---|---|---|")
    for a in (float(v) for v in args.alphas.split(",")):
        r = solve(counts, hidden, caps, demand, a, floors, args.floorTol)
        if r is None:
            print("| %g | infeasible | - | - |" % a)
            continue
        u, x, sh = r
        print("| %g | %.4f | %s | %s |" % (a, u, ", ".join("%.3f" % v for v in x),
                                          "; ".join("%s: %.3f" % ("+".join(map(str, s)), t) for s, t in sh.items() if t > 1e-6)))


if __name__ == "__main__":
    sys.exit(main())
