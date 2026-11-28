"""Wave 4 (held-out seeds 103-122, 60 s, second-half throughput). Per cell and alpha in {0,1}: mean per-AP throughput, mean U_alpha, seeds meeting the
wave-3 floors (5 % slack), share = (U - U_BEB) / (U_oracle - U_BEB) on means, paired t of U_method - U_BEB (gc_analysis.paired_t). Learners (RAFA, Global; 3 train
seeds x eval seeds 103-107) are compared on seeds 103-107 only, each train seed a row plus pooled. Usage: graded_w4_analyse.py BUNDLES_A BUNDLES_B OUT.md"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gc_analysis as gc  # noqa: E402
import graded_w4_batch as w4  # noqa: E402

a_root, b_root, out = sys.argv[1:4]
runs = collections.defaultdict(dict)
for f in glob.glob(os.path.join(a_root, "g4-*", "run", "summary.json")):
    s = json.load(open(f))
    assert s["check"] == "PASS", f
    m = re.match(r"g4-(\w+?)-(.+)-s(\d+)$", s["job"])
    runs[(m.group(1), m.group(2))][int(m.group(3))] = s["thr_half2"]
for f in glob.glob(os.path.join(b_root, "g4-*", "*", "summary.json")):
    s = json.load(open(f))
    if s["name"] == "train":
        continue
    assert s["check"] == "PASS", f
    m = re.match(r"g4-(\w+?)-(rafa|global)-t(\d)$", s["job"])
    runs[(m.group(1), "%s-t%s" % (m.group(2), m.group(3)))][int(s["cfg"]["seed"])] = s["thr_half2"]
counts = [10, 10, 10]
lines = ["# Wave 4 (held-out seeds 103-122, 60 s, second-half throughput, Mbps)", ""]
for cell in sorted({c for c, _ in runs}):
    fl = [float(x) for x in w4.FLOORS[cell].split(",")]
    beb = runs[(cell, "beb")]
    for al in (0, 1):
        ub = {s: gc.utility(beb[s], counts, al) for s in beb}
        orc = runs[(cell, "f1-a%d" % al)]
        mean_ub = sum(ub[s] for s in orc) / len(orc)
        mean_uo = sum(gc.utility(orc[s], counts, al) for s in orc) / len(orc)
        methods = ["beb", "idlesense", "dac514", "f1-a%d" % al, "kwdirect-a%d" % al] + ["%s-t%d" % (k, t) for k in ("rafa", "global") for t in range(3)]
        lines += ["## Cell %s alpha %d" % (cell, al), "", "| method | n | per-AP | mean U | floors met | share | U-U_BEB (p) |", "|---|---|---|---|---|---|---|"]
        for m in methods:
            r = runs.get((cell, m))
            if not r:
                continue
            seeds = sorted(set(r) & set(beb))
            us = [gc.utility(r[s], counts, al) for s in seeds]
            mean_u = sum(us) / len(us)
            ref = [gc.utility(beb[s], counts, al) for s in seeds]
            per = [sum(r[s][i] for s in seeds) / len(seeds) for i in range(3)]
            met = sum(gc.feasible(r[s], fl, 0.05) for s in seeds)
            mub = sum(ref) / len(ref)
            uo_s = [gc.utility(orc[s], counts, al) for s in seeds if s in orc]
            share = "-" if m == "beb" or len(uo_s) != len(seeds) or sum(uo_s) / len(uo_s) <= mub else "%.2f" % ((mean_u - mub) / (sum(uo_s) / len(uo_s) - mub))
            dp = "-" if m == "beb" else "%.2f +/- %.2f (p %.3g)" % gc.paired_t([u - b for u, b in zip(us, ref)])
            lines.append("| %s | %d | %s | %.2f | %d/%d | %s | %s |" % (m, len(seeds), " / ".join("%.1f" % x for x in per), mean_u, met, len(seeds), share, dp))
        lines.append("")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
