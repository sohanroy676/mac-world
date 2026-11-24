#!/usr/bin/env python3
"""v4.1.0 confirmation table (Wave 4a: seeds 103-122, 300 s, scored on the second half of the run, thr_half2).

share_seed = (U - U_BEB) / (U_ceiling - U_BEB), BEB paired per seed, infeasible seed (any AP below floor x 0.95) = share 0.
Ceilings are the validated values on seeds 200-209 (ceilings-v4.1.0.md).
Methods: kwdirect (exact CW every 10 ms), kwdirect-gatec (100 ms updates, 2^k-1), static F1, DAC514, coord (S4 alpha 1), and the best frozen learner per cell.
Tests: (a) kwdirect and kwdirect-gatec vs every other family, paired per seed, one-sided non-inferiority margin 0.05, intersection-union over the 9 cell-alpha
pairs, Holm over families; (b) Gate C cost = kwdirect-gatec minus kwdirect per cell-alpha.
Usage: confirm_v4_1_0.py [--prefix w4a] summaries.jsonl [...]
"""
import json
import re
import sys
from collections import defaultdict

import numpy as np

import gc_analysis as g

args = sys.argv[1:]
PREFIX = "w4a"
if args and args[0] == "--prefix":
    PREFIX, args = args[1], args[2:]
METRIC = "thr_half2"
CNT = {"s2": [20, 40], "s4": [10, 10, 10], "s5a": [10, 10, 10]}
FLR = {"s2": [9.3, 17.19], "s4": [24.44, 1.31, 24.44], "s5a": [15.03, 11.25, 10.0]}
CEIL = {("s2", 0): 39.72, ("s2", 1): -24.83, ("s2", 4): -69.27, ("s4", 0): 77.28, ("s4", 1): 21.39, ("s4", 4): -1.54,
        ("s5a", 0): 49.98, ("s5a", 1): 13.28, ("s5a", 4): -4.24}
runs = defaultdict(lambda: defaultdict(dict))
for f in args:
    for line in open(f):
        r = json.loads(line)
        m = re.match(PREFIX + r"-(s\w+?)-(.+)-s(\d+)$", r["job"])
        if m and r.get(METRIC):
            c, meth, s = m.groups()
            meth = re.sub(r"^L-(\w+)-t\d+$", r"L-\1", meth)
            runs[c][meth][int(s)] = r[METRIC]
SH, FE = {}, {}
FAMS = ["kwdirect", "kwdirect-gatec", "f1", "dac514", "coord", "L-global", "L-pf", "L-rafa"]
for cell in ("s2", "s4", "s5a"):
    for al in (0, 1, 4):
        ucl = CEIL[(cell, al)]
        beb = runs[cell]["beb"]
        ub = {s: g.utility(t, CNT[cell], al) for s, t in beb.items()}
        for fam in FAMS:
            key = {"kwdirect": "kwdirect-a%d" % al, "kwdirect-gatec": "kwdirect-gatec-a%d" % al, "f1": "f1-a%d" % al, "coord": "coord-a%d" % al}.get(fam, fam)
            d = runs[cell].get(key)
            if not d:
                continue
            sh = {}
            fe = 0
            for s, t in d.items():
                if s in ub and ucl - ub[s] > 0:
                    ok = g.feasible(t, FLR[cell], 0.05)
                    fe += ok
                    sh[s] = (g.utility(t, CNT[cell], al) - ub[s]) / (ucl - ub[s]) if ok else 0.0
            SH[(cell, al, fam)] = sh
            FE[(cell, al, fam)] = (fe, len(sh))
print("## Share of the validated ceiling, mean (sd), feasible seeds, n seeds")
print("| family | " + " | ".join("%s a%d" % (c, a) for c in ("s2", "s4", "s5a") for a in (0, 1, 4)) + " | worst |")
print("|---|" + "---|" * 10)
for fam in FAMS:
    cells_, means = [], []
    for c in ("s2", "s4", "s5a"):
        for a in (0, 1, 4):
            v = SH.get((c, a, fam))
            if v:
                x = list(v.values())
                means.append(np.mean(x))
                cells_.append("%.2f (%.2f) %d/%d" % (np.mean(x), np.std(x, ddof=1), FE[(c, a, fam)][0], FE[(c, a, fam)][1]))
            else:
                cells_.append("-")
    print("| %s | %s | %s |" % (fam, " | ".join(cells_), "%.2f" % min(means) if len(means) == 9 else "n/a (%d cells)" % len(means)))


def test(target):
    print("\n## Paired tests: %s minus each family (share units, margin %.2f); IU = intersection-union non-inferiority over all 9 cell-alpha pairs" % (target, g.MARGIN))
    print("| family | min cell diff | IU p non-inferior (Holm) | cells better (p<0.05) | cells worse (p<0.05) |")
    print("|---|---|---|---|---|")
    rows = []
    for fam in FAMS:
        if fam == target:
            continue
        dd, b, w = [], 0, 0
        for c in ("s2", "s4", "s5a"):
            for a in (0, 1, 4):
                t, o = SH.get((c, a, target)), SH.get((c, a, fam))
                if not t or not o:
                    continue
                seeds = sorted(set(t) & set(o))
                d = [t[s] - o[s] for s in seeds]
                dd.append(d)
                mean, hw, p2 = g.paired_t(d)
                if p2 < 0.05:
                    b += mean > 0
                    w += mean < 0
        if len(dd) == 9:
            rows.append((fam, min(np.mean(x) for x in dd), g.intersection_union_p(dd), b, w))
    hp = g.holm([r[2] for r in rows]) if rows else []
    for (fam, mn, iu, b, w), h in zip(rows, hp):
        print("| %s | %.3f | %.4f (%.4f) | %d | %d |" % (fam, mn, iu, h, b, w))


test("kwdirect")
test("kwdirect-gatec")
print("\n## Gate C cost: kwdirect-gatec minus kwdirect, per cell-alpha (share units, mean, 95%% half-width, non-inferiority p for margin %.2f)" % g.MARGIN)
for c in ("s2", "s4", "s5a"):
    for a in (0, 1, 4):
        t, o = SH.get((c, a, "kwdirect-gatec")), SH.get((c, a, "kwdirect"))
        if t and o:
            seeds = sorted(set(t) & set(o))
            d = [t[s] - o[s] for s in seeds]
            mean, hw, p2 = g.paired_t(d)
            print("- %s a%d: %.3f +- %.3f, p_noninf %.4f (n=%d)" % (c, a, mean, hw, g.noninferior_p(d), len(d)))
