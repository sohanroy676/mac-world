"""Confirmation wave C1 (seeds 103-122, 60 s, second-half throughput). Per cell and alpha: mean per-AP throughput, mean U_alpha, seeds meeting the
U2 floors (5 % slack), share = (U - U_BEB) / (U_oracle - U_BEB) on means, and the paired t-test of U_method - U_BEB over seeds
(gc_analysis.paired_t: mean, 95 % half-width, two-sided p for H0 mean difference = 0). Alpha 4 is reported by U only: BEB's near-zero middle AP makes
U_BEB huge-negative and shares meaningless. Usage: apdir_c1_analyse.py BUNDLES OUT.md [BUNDLES2 ...]"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gc_analysis as gc  # noqa: E402
import apdir_u2_batch as u2  # noqa: E402

out = sys.argv[2]
runs = collections.defaultdict(dict)
for root in [sys.argv[1]] + sys.argv[3:]:
    for f in glob.glob(os.path.join(root, "c1-*", "run", "summary.json")):
        s = json.load(open(f))
        if s["check"] != "PASS":
            continue
        m = re.match(r"c1-(\w+?)-(.+)-s(\d+)$", s["job"])
        runs[(m.group(1), m.group(2))][int(m.group(3))] = s["thr_half2"]
lines = ["# Confirmation wave C1 (seeds 103-122, 60 s)", ""]
for cell in sorted({c for c, _ in runs}):
    counts = [10] * len(next(iter(runs[(cell, "beb")].values())))
    fl = [float(x) for x in u2.FLOORS[cell].split(",")]
    beb = runs[(cell, "beb")]
    for al in (0, 1, 4):
        methods = ["beb", "idlesense", "dac514", "f1-a%d" % al, "kwdirect-a%d" % al]
        rows = {m: runs.get((cell, m)) for m in methods if runs.get((cell, m))}
        ub = {s: gc.utility(beb[s], counts, al) for s in beb}
        mean_ub = sum(ub.values()) / len(ub)
        uo = rows.get("f1-a%d" % al)
        mean_uo = sum(gc.utility(v, counts, al) for v in uo.values()) / len(uo) if uo else None
        lines += ["## Cell %s alpha %d" % (cell, al), "", "| method | n | per-AP | mean U | floors met | share | U-U_BEB (p) |", "|---|---|---|---|---|---|---|"]
        for m, r in rows.items():
            seeds = sorted(set(r) & set(beb))
            us = [gc.utility(r[s], counts, al) for s in seeds]
            mean_u = sum(us) / len(us)
            per = [sum(r[s][i] for s in seeds) / len(seeds) for i in range(len(counts))]
            met = sum(gc.feasible(r[s], fl, 0.05) for s in seeds)
            share = "-" if al == 4 or m == "beb" or mean_uo is None or mean_uo <= mean_ub else "%.2f" % ((mean_u - mean_ub) / (mean_uo - mean_ub))
            if m == "beb":
                dp = "-"
            else:
                mean_d, hw, pv = gc.paired_t([u - ub[s] for u, s in zip(us, seeds)])
                dp = "%.2f +/- %.2f (p %.3g)" % (mean_d, hw, pv)
            lines.append("| %s | %d | %s | %.2f | %d/%d | %s | %s |" % (m, len(seeds), " / ".join("%.1f" % x for x in per), mean_u, met, len(seeds), share, dp))
        lines.append("")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
