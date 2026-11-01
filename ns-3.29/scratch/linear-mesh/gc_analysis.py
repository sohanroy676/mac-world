"""v3.5.0 (M0) analysis for the v4 plan: station-weighted alpha-fair utility, fair-floor feasibility, gap closed (GC).

  ../../venv/bin/python gc_analysis.py --topo 10,10,10 --hidden 1-3 --seeds 100-107 [--load 150] [--results results]

Scans <results>/*/config.json (run dirs, as written by OSCAR_multi_ap_train.py), keeps the runs of ONE scenario
(apStaCounts, apHidden, apLoads, offeredLoad) at the given eval seeds, and groups them by method key
(config tag, else mode; static runs by "static:<apCws>"). No scipy: the t distribution is computed here.

Definitions (docs/planning/mac-world-v4-plan.html, section Scoring and Statistics):
  u_alpha(x): alpha 0 -> x, alpha 1 -> ln x, else x^(1-alpha)/(1-alpha); per-station throughput floored at EPS Mbps.
  U_alpha = sum_i n_i * u_alpha(max(EPS, x_i / n_i))              (n_i = stations of AP i, x_i = policy-window Mbps)
  floor_i = min(BEB_i, BEB aggregate * n_i / sum n)               (BEB means over the same seeds); feasible = x_i >= 0.95 floor_i
                                                                  (5 % slack, plan revision 6; --floorTol 0 = strict)
  GC      = (U - U_BEB) / (U_oracle - U_BEB)                      (oracle = best FEASIBLE static setting for that alpha)
  a cell is degenerate when U_oracle - U_BEB < 3 SD of BEB's U over seeds; it is then reported as raw U (not GC).
  GC_D    = same on ln p99 delay, lower is better (oracle = lowest p99 static setting delivering >= 99 % of the load).
"""
import argparse
import csv
import glob
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

from summarize_run import summarize

EPS = 0.01  # Mbps per station inside u_alpha
MARGIN = 0.05  # non-inferiority margin in GC units (Claim 1)


def u_alpha(x, alpha):
    if alpha == 0:
        return x
    if alpha == 1:
        return math.log(x)
    return x ** (1 - alpha) / (1 - alpha)


def utility(thr, counts, alpha):
    """U_alpha = sum_i n_i u_alpha(max(EPS, x_i / n_i)); thr and counts are per-AP lists."""
    return float(sum(n * u_alpha(max(EPS, x / n), alpha) for x, n in zip(thr, counts)))


def floors(beb_thr, counts):
    tot, n = sum(beb_thr), sum(counts)
    return [min(b, tot * c / n) for b, c in zip(beb_thr, counts)]


def feasible(thr, fl, tol=0.0):
    """tol = relative slack: x_i >= floor_i * (1 - tol). The plan's definition is tol = 0."""
    return all(t >= f * (1 - tol) for t, f in zip(thr, fl))


def gc_delay(p99, p99_beb, p99_oracle):
    """GC_D on ln p99 (lower is better)."""
    return (math.log(p99_beb) - math.log(p99)) / (math.log(p99_beb) - math.log(p99_oracle))


# ---- Student t without scipy (regularised incomplete beta, Numerical Recipes continued fraction) ----
def _betacf(a, b, x):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def _betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T > t) for Student t with df degrees of freedom."""
    p = 0.5 * _betainc(df / 2.0, 0.5, df / (df + t * t))
    return p if t > 0 else 1.0 - p


def t_crit95(df):
    lo, hi = 0.0, 100.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if 2 * t_sf(mid, df) > 0.05:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def paired_t(d, mu0=0.0):
    """(mean, 95 % half-width, two-sided p for H0 mean = mu0). d = per-seed differences."""
    d = np.asarray(d, dtype=float)
    n = len(d)
    if n < 2:
        return float(d.mean()), float("nan"), float("nan")
    m, sd = float(d.mean()), float(d.std(ddof=1))
    if sd == 0:
        return m, 0.0, 0.0 if m != mu0 else 1.0
    t = (m - mu0) / (sd / math.sqrt(n))
    return m, t_crit95(n - 1) * sd / math.sqrt(n), 2 * t_sf(abs(t), n - 1)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (same order as input)."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, run = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = run
    return adj


def noninferior_p(d, margin=MARGIN):
    """One-sided paired t p-value for H0: mean(d) <= -margin (reject = non-inferior)."""
    d = np.asarray(d, dtype=float)
    n = len(d)
    m, sd = float(d.mean()), float(d.std(ddof=1)) if n > 1 else float("nan")
    if n < 2:
        return float("nan")
    if sd == 0:
        return 0.0 if m > -margin else 1.0
    return t_sf((m + margin) / (sd / math.sqrt(n)), n - 1)


def intersection_union_p(diffs_by_cell, margin=MARGIN):
    """Claim 1: non-inferior in EVERY cell -> the p-value is the max of the per-cell one-sided p-values."""
    return max(noninferior_p(d, margin) for d in diffs_by_cell)


# ---- loading ----
def parse_seeds(txt):
    out = []
    for part in txt.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def method_key(cfg):
    if cfg.get("mode") == "static":
        return "static:" + cfg["apCws"]
    return cfg.get("tag") or cfg["mode"]


def load_runs(results, topo, hidden, loads, offered, seeds, tags=None):
    """{method: {seed: summary}} for one scenario. Duplicate (method, seed): the lexicographically last run dir wins."""
    runs = defaultdict(dict)
    for cfgp in sorted(glob.glob(os.path.join(results, "*", "config.json"))):
        try:
            cfg = json.load(open(cfgp))
        except ValueError:
            continue
        if cfg.get("apStaCounts") != topo or (cfg.get("apHidden") or "") != hidden or (cfg.get("apLoads") or "") != loads:
            continue
        if abs(float(cfg.get("offeredLoad", 150)) - offered) > 1e-9 or cfg.get("seed") not in seeds:
            continue
        if cfg["mode"] in ("independent", "global", "shared", "central") and not cfg.get("eval"):
            continue  # training runs are not evaluation runs
        key = method_key(cfg)
        if tags and key not in tags and not key.startswith("static:") and key != "beb":
            continue
        d = os.path.dirname(cfgp)
        if not os.path.exists(os.path.join(d, "trace.csv")):
            continue
        runs[key][cfg["seed"]] = dict(summarize(d, 0.01, 300), run_dir=d)
    return runs


def cell_table(runs, counts, alpha, floor_tol=0.0):
    """Rows for one alpha: per method n, aggregate, U, GC (paired by seed), floor feasibility. Returns (rows, info)."""
    beb = runs.get("beb")
    if not beb:
        raise SystemExit("no BEB runs for this scenario")
    seeds = sorted(beb)
    thr = lambda s: [s["thr_policy"][a] for a in s["aps"]]
    ub = {sd: utility(thr(beb[sd]), counts, alpha) for sd in seeds}
    beb_mean_thr = [float(np.mean([thr(beb[sd])[i] for sd in seeds])) for i in range(len(counts))]
    fl = floors(beb_mean_thr, counts)
    ub_mean, ub_sd = float(np.mean(list(ub.values()))), float(np.std(list(ub.values()), ddof=1)) if len(seeds) > 1 else 0.0
    stats = {}
    for m, bys in runs.items():
        ss = [sd for sd in seeds if sd in bys]
        if not ss:
            continue
        u = {sd: utility(thr(bys[sd]), counts, alpha) for sd in ss}
        mt = [float(np.mean([thr(bys[sd])[i] for sd in ss])) for i in range(len(counts))]
        stats[m] = dict(seeds=ss, u=u, thr=mt, agg=sum(mt), feasible=feasible(mt, fl, floor_tol), umean=float(np.mean(list(u.values()))))
    cands = [m for m in stats if m.startswith("static:") and stats[m]["feasible"] and len(stats[m]["seeds"]) == len(seeds)]
    oracle = max(cands, key=lambda m: stats[m]["umean"]) if cands else None
    gap = stats[oracle]["umean"] - ub_mean if oracle else float("nan")
    degenerate = (oracle is None) or gap < 3 * ub_sd or gap <= 0
    rows = []
    for m in sorted(stats, key=lambda k: (not k == "beb", k)):
        s = stats[m]
        row = dict(method=m, n=len(s["seeds"]), agg=s["agg"], min_ap=min(s["thr"]), feasible=s["feasible"], umean=s["umean"])
        if not degenerate:
            d = [(s["u"][sd] - ub[sd]) / gap for sd in s["seeds"]]
            row["gc"], row["gc_hw"], row["diffs"] = float(np.mean(d)), paired_t(d)[1], d
        rows.append(row)
    return rows, dict(oracle=oracle, gap=gap, ub_sd=ub_sd, degenerate=degenerate, floors=fl, beb_thr=beb_mean_thr, seeds=seeds)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topo", required=True)
    ap.add_argument("--hidden", default="", help="apHidden value, e.g. 1-3 (default none)")
    ap.add_argument("--loads", default="", help="apLoads value (default none)")
    ap.add_argument("--load", type=float, default=150.0, help="offeredLoad per STA")
    ap.add_argument("--seeds", default="100-107")
    ap.add_argument("--results", default="results")
    ap.add_argument("--floorTol", type=float, default=0.05, help="relative slack on the fair floor: x_i >= (1 - tol) floor_i. 0.05 = plan revision 6 (decided 2026-11-01: with tol 0 the S4 static oracle is itself infeasible, 2.9 %% short on the edge APs); 0 = rev 5 strict")
    ap.add_argument("--alphas", default="0,1,2")
    ap.add_argument("--methods", default="", help="comma-separated method keys to show besides beb and the statics (default all)")
    ap.add_argument("--out", default="", help="write the markdown here too")
    a = ap.parse_args()
    counts = [int(c) for c in a.topo.split(",")]
    seeds = parse_seeds(a.seeds)
    runs = load_runs(a.results, a.topo, a.hidden, a.loads, a.load, seeds, set(a.methods.split(",")) if a.methods else None)
    md = ["## GC table: %s%s%s, load %g, seeds %s" % (a.topo, " hidden " + a.hidden if a.hidden else "", " loads " + a.loads if a.loads else "", a.load, a.seeds), ""]
    for alpha in [float(x) for x in a.alphas.split(",")]:
        rows, info = cell_table(runs, counts, int(alpha) if alpha == int(alpha) else alpha, a.floorTol)
        md += ["### alpha = %g" % alpha, "",
               "BEB per-AP Mbps %s; floors %s; oracle = %s; U gap %.3f (BEB SD %.3f)%s" % (
                   np.round(info["beb_thr"], 2).tolist(), np.round(info["floors"], 2).tolist(), info["oracle"], info["gap"], info["ub_sd"],
                   "; **degenerate cell, raw U only**" if info["degenerate"] else ""), "",
               "| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |", "|---|---|---|---|---|---|---|"]
        for r in rows:
            gc = "%.3f ± %.3f" % (r["gc"], r["gc_hw"]) if "gc" in r else "n/a"
            md.append("| %s | %d | %.2f | %.2f | %.3f | %s | %s |" % (r["method"], r["n"], r["agg"], r["min_ap"], r["umean"], gc, "ok" if r["feasible"] else "**infeasible**"))
        md.append("")
    text = "\n".join(md)
    print(text)
    if a.out:
        open(a.out, "w").write(text + "\n")


if __name__ == "__main__":
    sys.exit(main())
