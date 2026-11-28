"""Wave 3 summary (seeds 0-2, 30 s, second-half throughput): per graded cell, BEB vs the exact static grid. Oracle per alpha in {0,1} = grid point with the highest
U_alpha (gc_analysis.utility, 10 STAs per AP) that meets the fair floors (min(BEB_i, total/3), 5 % slack). Writes the oracle points as JSON.
Usage: graded_w3_analyse.py BUNDLES OUT.md OUT_ORACLE.json"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
import gc_analysis as gc  # noqa: E402

root, out, out_json = sys.argv[1:4]
runs = collections.defaultdict(list)
for f in glob.glob(os.path.join(root, "g3-*", "run", "summary.json")):
    s = json.load(open(f))
    assert s["check"] == "PASS", f
    m = re.match(r"g3-(\w+?)-(.+)-s(\d+)$", s["job"])
    runs[(m.group(1), m.group(2))].append(s["thr_half2"])


def mean(rows):
    return [sum(r[i] for r in rows) / len(rows) for i in range(3)]


counts = [10, 10, 10]
lines = ["# Wave 3 summary (seeds 0-2, exact static 30 s, second-half throughput, Mbps)", ""]
oracle = {}
for cell in sorted({c for c, _ in runs}):
    b = mean(runs[(cell, "beb")])
    fl = gc.floors(b, counts)
    stat = {m: mean(r) for (c, m), r in runs.items() if c == cell and m.startswith("f1-")}
    feas = {m: x for m, x in stat.items() if gc.feasible(x, fl, 0.05)}
    lines += ["## Cell %s (BEB %s, floors %s; %d of %d grid points feasible)" % (cell, " / ".join("%.1f" % x for x in b), " / ".join("%.1f" % x for x in fl), len(feas), len(stat)), "",
              "| alpha | method | per-AP | sum | U | gain over BEB |", "|---|---|---|---|---|---|"]
    oracle[cell] = {}
    for al in (0, 1):
        ub = gc.utility(b, counts, al)
        best = max(feas, key=lambda m: gc.utility(feas[m], counts, al))
        top3 = sorted(feas, key=lambda m: -gc.utility(feas[m], counts, al))[:3]
        oracle[cell][str(al)] = best[3:]
        lines.append("| %d | beb | %s | %.1f | %.2f | - |" % (al, " / ".join("%.1f" % x for x in b), sum(b), ub))
        for m in top3:
            x = feas[m]
            lines.append("| %d | %s | %s | %.1f | %.2f | %+.2f |" % (al, m, " / ".join("%.1f" % v for v in x), sum(x), gc.utility(x, counts, al), gc.utility(x, counts, al) - ub))
    uni = [m for m in feas if len(set(m[3:].split("-"))) == 1]
    lines += ["", "Uniform grid points that are feasible: %s" % (", ".join(sorted(uni)) or "none"), ""]
open(out, "w").write("\n".join(lines))
json.dump(oracle, open(out_json, "w"), indent=1)
print("\n".join(lines))
print(oracle)
