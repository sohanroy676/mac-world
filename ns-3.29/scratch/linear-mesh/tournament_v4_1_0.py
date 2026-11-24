#!/usr/bin/env python3
"""v4.1.0 tournament table (seeds 300-309, 60 s): per cell and alpha, ceiling share of every method.

share_seed = (U - U_BEB) / (U_ceiling - U_BEB), BEB paired per seed; an infeasible seed (any AP below floor x 0.95) counts as share 0.
Ceilings are the validated values on seeds 200-209 (ceilings-v4.1.0.md), not rerun here. Methods: Wave 3a jobs `w3a-<cell>-<method>-s<seed>`
and the Wave 2l learner evals (`w2l-<cell>-<learner>-t<train seed>-a<trained alpha>-h<half>`, command eval<seed>).
Usage: tournament_v4_1_0.py w3a/summaries.jsonl w2l/summaries.jsonl [...]
"""
import json
import re
import sys
from collections import defaultdict

import numpy as np

import gc_analysis as g

METRIC = "thr_half2"  # plan: 60 s runs are scored on 30-60 s
CNT = {"s2": [20, 40], "s4": [10, 10, 10], "s5a": [10, 10, 10]}
FLR = {"s2": [9.3, 17.19], "s4": [24.44, 1.31, 24.44], "s5a": [15.03, 11.25, 10.0]}
CEIL = {("s2", 0): 39.72, ("s2", 1): -24.83, ("s2", 4): -69.27, ("s4", 0): 77.28, ("s4", 1): 21.39, ("s4", 4): -1.54,
        ("s5a", 0): 49.98, ("s5a", 1): 13.28, ("s5a", 4): -4.24}
runs = defaultdict(lambda: defaultdict(dict))  # cell -> method -> seed -> thr
for f in sys.argv[1:]:
    for line in open(f):
        r = json.loads(line)
        m = re.match(r"w3a-(s\w+?)-(.+)-s(\d+)$", r["job"])
        if m:
            runs[m.group(1)][m.group(2)][int(m.group(3))] = r[METRIC]
            continue
        m = re.match(r"w2l-(s\w+?)-(rafa|global|pf)-t(\d+)-a(\d+)-h\d$", r["job"])
        if m and r["name"].startswith("eval"):
            c, lr, t, a = m.groups()
            runs[c]["L-%s-t%s-a%s" % (lr, t, a)][int(r["name"][4:])] = r[METRIC]
out = {}
SH = {}
for cell in ("s2", "s4", "s5a"):
    for al in (0, 1, 4):
        ucl = CEIL[(cell, al)]
        beb = runs[cell]["beb"]
        ub = {s: g.utility(t, CNT[cell], al) for s, t in beb.items()}
        print("\n## %s alpha %d (ceiling U %.2f, BEB mean U %.2f, n=%d)" % (cell, al, ucl, np.mean(list(ub.values())), len(ub)))
        print("| method | share mean | sd | feasible | U mean |")
        print("|---|---|---|---|---|")
        for m, d in sorted(runs[cell].items()):
            if m.startswith("kwdirect-a") and m != "kwdirect-a%d" % al or m.startswith("f1-a") and m != "f1-a%d" % al \
                    or m.startswith("f2-a") and m != "f2-a%d" % al or m.startswith("coord-a") and m != "coord-a%d" % al:
                continue
            if m.startswith("L-") and not (m.endswith("-a1") or m.endswith("-a%d" % al)):
                continue
            sh, fe, us, shs = [], 0, [], {}
            for s, t in d.items():
                if s not in ub or ucl - ub[s] <= 0:
                    continue
                u = g.utility(t, CNT[cell], al)
                ok = g.feasible(t, FLR[cell], 0.05)
                fe += ok
                us.append(u)
                sh.append((u - ub[s]) / (ucl - ub[s]) if ok else 0.0)
                shs[s] = sh[-1]
            if not sh:
                continue
            SH[(cell, al, m)] = shs
            out[(cell, al, m)] = (np.mean(sh), np.std(sh, ddof=1) if len(sh) > 1 else 0.0, fe, len(sh))
            print("| %s | %.3f | %.3f | %d/%d | %.2f |" % (m, np.mean(sh), out[(cell, al, m)][1], fe, len(sh), np.mean(us)))
TOP = {("s2", "global"): 2003, ("s2", "pf"): 2006, ("s2", "rafa"): 2011, ("s4", "global"): 2008, ("s4", "pf"): 2003, ("s4", "rafa"): 2001,
       ("s5a", "global"): 2001, ("s5a", "pf"): 2007, ("s5a", "rafa"): 2007}  # best training seed per cell from Wave 2k (selected on seeds 0-2)


def fam(cell, al, f):
    if f in ("beb", "blade", "dac514", "idlesense", "kw", "ucbctx"):
        return f
    if f == "kwdirect":
        return "kwdirect-a%d" % al
    if f == "static-F1":
        return "f1-a%d" % al
    if f == "static-F2":
        return "f2-a%d" % al
    lr = f.split(":")[1]
    if f.startswith("global") or f.startswith("pf") or f.startswith("rafa-a1"):
        return "L-%s-t%d-a1" % (f.split("-")[0].split(":")[0], TOP[(cell, f.split("-")[0])])
    return "L-rafa-t%d-a%d" % (TOP[(cell, "rafa")], al if al in (0, 4) and (cell, "rafa") else 1)


FAMS = ["kwdirect", "static-F1", "static-F2", "blade", "dac514", "idlesense", "kw", "ucbctx", "global", "pf", "rafa-a1", "rafa-alphamatched"]


def key(cell, al, f):
    if f in ("global", "pf"):
        return "L-%s-t%d-a1" % (f, TOP[(cell, f)])
    if f == "rafa-a1":
        return "L-rafa-t%d-a1" % TOP[(cell, "rafa")]
    if f == "rafa-alphamatched":
        return "L-rafa-t%d-a%d" % (TOP[(cell, "rafa")], al)
    return fam(cell, al, f)


print("\n## Worst cell per method family (mean share over seeds 300-309; best training seed of Wave 2k for learners)")
print("| family | " + " | ".join("%s a%d" % (c, a) for c in ("s2", "s4", "s5a") for a in (0, 1, 4)) + " | worst |")
print("|---|" + "---|" * 10)
for f in FAMS:
    row = []
    for c in ("s2", "s4", "s5a"):
        for a in (0, 1, 4):
            v = out.get((c, a, key(c, a, f)))
            row.append(v[0] if v else None)
    have = [x for x in row if x is not None]
    print("| %s | " % f + " | ".join("%.2f" % x if x is not None else "-" for x in row) + " | %s |" % ("%.2f" % min(have) if len(have) == 9 else "n/a (%d cells)" % len(have)))

print("\n## Paired tests: kwdirect (per-alpha setting) minus each family, share units, seeds 300-309, margin %.2f" % g.MARGIN)
print("Non-inferiority (kwdirect not worse by more than the margin) must hold in all 9 cell-alpha pairs: intersection-union p (Holm over families).")
print("| family | min cell diff | IU p non-inferior | cells where kwdirect is better (paired t, p<0.05) | cells where family is better |")
print("|---|---|---|---|---|")
rows = []
for f in [x for x in FAMS if x not in ("kwdirect",)]:
    dd, better, worse, ok9 = {}, 0, 0, True
    for c in ("s2", "s4", "s5a"):
        for a in (0, 1, 4):
            t, o = SH.get((c, a, key(c, a, "kwdirect"))), SH.get((c, a, key(c, a, f)))
            if not t or not o:
                ok9 = False
                continue
            seeds = sorted(set(t) & set(o))
            d = [t[x] - o[x] for x in seeds]
            dd[(c, a)] = d
            mean, hw, p2 = g.paired_t(d)
            if p2 < 0.05:
                better += mean > 0
                worse += mean < 0
    if not ok9:
        continue
    iu = g.intersection_union_p(list(dd.values()))
    rows.append((f, min(np.mean(v) for v in dd.values()), iu, better, worse))
hp = g.holm([r[2] for r in rows])
for (f, mn, iu, b, w), h in zip(rows, hp):
    print("| %s | %.3f | %.4f (Holm %.4f) | %d | %d |" % (f, mn, iu, h, b, w))
