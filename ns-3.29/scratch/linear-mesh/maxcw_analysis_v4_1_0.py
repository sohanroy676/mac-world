#!/usr/bin/env python3
"""v4.1.0 max-CW analysis: ceiling share per method in one cell, paired non-inferiority tests, Holm over rivals.

share_seed = (U_method - U_BEB) / (U_ceiling - U_BEB), U = station-weighted alpha-fair utility of per-AP throughput
(gc_analysis.utility). BEB is paired per seed (same seed). Feasible = every AP at >= floor x (1 - tol) (default tol 0.05).
Infeasible seeds count as share 0 for the test (a conservative rule, a decision, not a plan fact).
Tests: the --target method vs each other method, paired over seeds: (a) one-sided non-inferiority with margin 0.05 (share
units), (b) two-sided paired t. Holm correction across the rival set, for each family.

  maxcw_analysis_v4_1_0.py w2h/summaries.jsonl --counts 10,10,10 --alpha 0 --floors 24.44,1.31,24.44 \
      --beb w2h-s4-beb --ceiling-thr 38.1,12.0,38.1 --target w2h-s4-kwdirect-a0 [--metric thr_all] [--tol 0.05]
--ceiling-thr = per-AP throughput of the ceiling (best feasible static), or --ceiling-u = its utility directly.
Job names must end in -s<seed>; a method = the job name without that suffix.
"""
import argparse
import json
import re
from collections import defaultdict

import numpy as np

import gc_analysis as g

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--counts", required=True)
ap.add_argument("--alpha", type=float, required=True)
ap.add_argument("--floors", required=True)
ap.add_argument("--beb", required=True)
ap.add_argument("--target", default="")
ap.add_argument("--ceiling-thr", default="")
ap.add_argument("--ceiling-u", type=float, default=None)
ap.add_argument("--metric", default="thr_all", choices=["thr_all", "thr_half2", "thr_policy"])
ap.add_argument("--tol", type=float, default=0.05)
ap.add_argument("--margin", type=float, default=g.MARGIN)
a = ap.parse_args()
counts = [int(x) for x in a.counts.split(",")]
floors = [float(x) for x in a.floors.split(",")]
if a.ceiling_u is not None:
    ucl = a.ceiling_u
else:
    ucl = g.utility([float(x) for x in a.ceiling_thr.split(",")], counts, a.alpha)

runs = defaultdict(dict)  # method -> seed -> thr
for f in a.files:
    for line in open(f):
        r = json.loads(line)
        m = re.match(r"(.*)-s(\d+)$", r["job"])
        if m and r.get(a.metric):
            runs[m.group(1)][int(m.group(2))] = r[a.metric]
beb = runs[a.beb]
ub = {s: g.utility(t, counts, a.alpha) for s, t in beb.items()}
gap = {s: ucl - u for s, u in ub.items()}
share, feas = {}, {}
for m, d in runs.items():
    sh, fe = {}, 0
    for s, t in d.items():
        if s not in ub or gap[s] <= 0:
            continue
        ok = g.feasible(t, floors, a.tol)
        fe += ok
        sh[s] = (g.utility(t, counts, a.alpha) - ub[s]) / gap[s] if ok else 0.0
    share[m] = sh
    feas[m] = (fe, len(d))
print("cell U(BEB) mean %.3f, ceiling U %.3f, metric %s, tol %.2f" % (np.mean(list(ub.values())), ucl, a.metric, a.tol))
print("%-34s %5s %8s %8s" % ("method", "feas", "share", "sd"))
for m in sorted(share, key=lambda m: -np.mean(list(share[m].values())) if share[m] else 0):
    v = list(share[m].values())
    print("%-34s %2d/%-2d %8.3f %8.3f" % (m, feas[m][0], feas[m][1], np.mean(v) if v else float("nan"), np.std(v, ddof=1) if len(v) > 1 else float("nan")))
if a.target and a.target in share:
    riv = [m for m in share if m not in (a.target, a.beb) and share[m]]
    rows = []
    for m in riv:
        seeds = sorted(set(share[a.target]) & set(share[m]))
        d = [share[a.target][s] - share[m][s] for s in seeds]
        mean, hw, p2 = g.paired_t(d)
        rows.append((m, len(d), mean, hw, g.noninferior_p(d, a.margin), p2))
    hn = g.holm([r[4] for r in rows])
    h2 = g.holm([r[5] for r in rows])
    print("\ntarget %s minus rival (share units, paired), margin %.2f" % (a.target, a.margin))
    print("%-34s %3s %8s %7s %9s %9s" % ("rival", "n", "diff", "+-95%", "p_noninf", "p_2sided"))
    for (m, n, mean, hw, pn, p2), x, y in zip(rows, hn, h2):
        print("%-34s %3d %8.3f %7.3f %9.4f %9.4f   (Holm %.4f / %.4f)" % (m, n, mean, hw, pn, p2, x, y))
