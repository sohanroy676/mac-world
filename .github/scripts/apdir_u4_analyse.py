"""Wave U4 pilot summary: kwdirect guard variants on d3/d4 (seeds 0-2). Reference U_BEB and U_static (best feasible exact static, U2) are the seed 0-2 values
printed in uplink-downlink-u3-v4.2.0.md. Usage: apdir_u4_analyse.py PILOT_BUNDLES OUT.md"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
import gc_analysis as gc  # noqa: E402

REF = {("d3", 0): (73.12, 77.05), ("d3", 1): (17.92, 22.28), ("d4", 0): (80.80, 86.06), ("d4", 1): (25.94, 29.07)}
FLOORS = {"d3": [24.37, 5.21, 24.37], "d4": [20.20, 13.69, 13.71, 20.20]}
root, out = sys.argv[1:3]
d = collections.defaultdict(list)
for f in glob.glob(os.path.join(root, "u4-*", "run", "summary.json")):
    s = json.load(open(f))
    if s["check"] != "PASS":
        continue
    m = re.match(r"u4-(\w+?)-(kw|kwlong)-(\w+)-a(\d)-s(\d+)$", s["job"])
    log = open(os.path.join(os.path.dirname(os.path.dirname(f)), "run.log")).read() if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(f)), "run.log")) else ""
    l2 = re.findall(r"kwdirect L2: updates (\d+) reverts (\d+) eta (\S+)", log)
    d[(m.group(1), m.group(2), m.group(3), int(m.group(4)))].append((s["thr_half2"], l2[-1] if l2 else None))
lines = ["# Wave U4 pilot: kwdirect guard variants on downlink (seeds 0-2, second-half throughput)", "",
         "Variant = (lyEtaMin, lyBestDecay); base = (0, 0) = the v4.1.0 behaviour. share = (U - U_BEB) / (U_static - U_BEB). Floors checked at 5 % slack.", ""]
for cell in ("d3", "d4"):
    for al in (0, 1):
        ub, us = REF[(cell, al)]
        counts = [10] * len(FLOORS[cell])
        lines += ["## %s alpha %d (U_BEB %.2f, U_static %.2f)" % (cell, al, ub, us), "", "| run | variant | n | per-AP | U | share | feasible | L2 updates/reverts/eta |", "|---|---|---|---|---|---|---|---|"]
        for (c, kind, var, a), rows in sorted(d.items()):
            if c != cell or a != al:
                continue
            x = [sum(r[0][i] for r in rows) / len(rows) for i in range(len(rows[0][0]))]
            u = gc.utility(x, counts, al)
            l2 = [r[1] for r in rows if r[1]]
            l2s = "; ".join("%s/%s/%s" % t for t in l2)
            lines.append("| %s | %s | %d | %s | %.2f | %.2f | %s | %s |" % (kind, var, len(rows), " / ".join("%.1f" % v for v in x), u, (u - ub) / (us - ub),
                                                                           "yes" if gc.feasible(x, FLOORS[cell], 0.05) else "NO", l2s))
        lines.append("")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
