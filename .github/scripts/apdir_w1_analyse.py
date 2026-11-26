"""Summarise wave U1 (apdir_w1_batch.py output) from fetched bundles: per cell and method, mean over seeds of per-AP throughput (second half),
sum, min-AP and proportional-fairness score (sum of ln thr). Best static point per cell by PF and by min-AP.
Usage: apdir_w1_analyse.py BUNDLE_DIR OUT.md"""
import collections
import glob
import json
import math
import os
import re
import sys

root, out = sys.argv[1:3]
data = collections.defaultdict(list)
for f in glob.glob(os.path.join(root, "u1-*", "run", "summary.json")):
    s = json.load(open(f))
    assert s["check"] == "PASS", f
    m = re.match(r"u1-(\w+?)-(.+)-s(\d+)$", s["job"])
    data[(m.group(1), m.group(2))].append(s["thr_half2"])


def stats(rows):
    n = len(rows[0])
    mean = [sum(r[i] for r in rows) / len(rows) for i in range(n)]
    return mean, sum(mean), min(mean), sum(math.log(max(x, 1e-3)) for x in mean), len(rows)


lines = ["# Wave U1 summary (seeds 0-2, 30 s, throughput over the second half, Mbps)", ""]
for cell in sorted({c for c, _ in data}):
    lines += ["## Cell %s" % cell, "", "| method | per-AP | sum | min-AP | PF | n |", "|---|---|---|---|---|---|"]
    rows = {m: stats(r) for (c, m), r in data.items() if c == cell}
    fixed = [m for m in rows if not m.startswith("static")]
    stat = [m for m in rows if m.startswith("static")]
    best_pf = max(stat, key=lambda m: rows[m][3])
    best_min = max(stat, key=lambda m: rows[m][2])
    for m in sorted(fixed) + [best_pf] + ([best_min] if best_min != best_pf else []):
        mean, s, mn, pf, n = rows[m]
        tag = m + (" (best PF)" if m == best_pf else "") + (" (best min-AP)" if m == best_min and m != best_pf else "")
        lines.append("| %s | %s | %.1f | %.2f | %.2f | %d |" % (tag, " / ".join("%.1f" % x for x in mean), s, mn, pf, n))
    lines.append("")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
