"""Summarise wave U2 against the U1 BEB reference. Per cell and alpha in {0,1,4}: U_alpha (gc_analysis.utility, 10 STAs per AP) of BEB (U1, seeds 0-2),
the best exact static grid point that meets the fair floors (floor = min(BEB_i, fair share of the BEB total), 5 % slack), and kwdirect at that alpha.
Share = (U - U_BEB) / (U_static - U_BEB); only meaningful where U_static > U_BEB. Means over seeds 0-2 of the second-half throughput (n=3, no CIs).
Usage: apdir_u2_analyse.py U1_BUNDLES U2_BUNDLES OUT.md"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
import gc_analysis as gc  # noqa: E402

u1, u2, out = sys.argv[1:4]
beb = collections.defaultdict(list)
for f in glob.glob(os.path.join(u1, "u1-*-beb-s*", "run", "summary.json")):
    s = json.load(open(f))
    beb[re.match(r"u1-(\w+?)-beb", s["job"]).group(1)].append(s["thr_half2"])
runs = collections.defaultdict(list)
for f in glob.glob(os.path.join(u2, "u2-*", "run", "summary.json")):
    s = json.load(open(f))
    assert s["check"] == "PASS", f
    m = re.match(r"u2-(\w+?)-(.+)-s(\d+)$", s["job"])
    runs[(m.group(1), m.group(2))].append(s["thr_half2"])


def mean(rows):
    return [sum(r[i] for r in rows) / len(rows) for i in range(len(rows[0]))]


lines = ["# Wave U2 summary (seeds 0-2, exact static 30 s, kwdirect 60 s, second-half throughput, Mbps)", ""]
for cell in sorted(beb):
    b = mean(beb[cell])
    counts = [10] * len(b)
    fl = gc.floors(b, counts)
    stat = {m: mean(r) for (c, m), r in runs.items() if c == cell and m.startswith("f1-")}
    lines += ["## Cell %s  (BEB %s, floors %s)" % (cell, " / ".join("%.1f" % x for x in b), " / ".join("%.1f" % x for x in fl)), "",
              "| alpha | method | per-AP | U | share | feasible |", "|---|---|---|---|---|---|"]
    for al in (0, 1, 4):
        ub = gc.utility(b, counts, al)
        feas = {m: x for m, x in stat.items() if gc.feasible(x, fl, 0.05)}
        best = max(feas, key=lambda m: gc.utility(feas[m], counts, al)) if feas else None
        us = gc.utility(feas[best], counts, al) if best else None
        lines.append("| %d | beb | %s | %.2f | - | yes |" % (al, " / ".join("%.1f" % x for x in b), ub))
        if best:
            lines.append("| %d | %s | %s | %.2f | 1.00 | yes |" % (al, best, " / ".join("%.1f" % x for x in feas[best]), us))
        k = runs.get((cell, "kwdirect-a%d" % al))
        if k:
            x = mean(k)
            uk = gc.utility(x, counts, al)
            share = (uk - ub) / (us - ub) if best and us > ub + 1e-9 else float("nan")
            lines.append("| %d | kwdirect | %s | %.2f | %.2f | %s |" % (al, " / ".join("%.1f" % v for v in x), uk, share, "yes" if gc.feasible(x, fl, 0.05) else "NO"))
    lines.append("")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
