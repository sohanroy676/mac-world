"""Rank the wave-U3 kwdirect settings (eta, delta, tau) per cell and alpha by U_alpha of the seed-mean second-half throughput, among settings that meet the
BEB-based fair floors (5 % slack), and compare with the U2 default kwdirect and the U2 best exact static point.
Usage: apdir_u3_analyse.py U1_BUNDLES U2_BUNDLES U3_BUNDLES OUT.md"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
import gc_analysis as gc  # noqa: E402

u1, u2, u3, out = sys.argv[1:5]


def load(root, prefix):
    d = collections.defaultdict(list)
    for f in glob.glob(os.path.join(root, prefix + "-*", "run", "summary.json")):
        s = json.load(open(f))
        if s["check"] != "PASS":
            continue
        m = re.match(r"%s-(\w+?)-(.+)-s(\d+)$" % prefix, s["job"])
        d[(m.group(1), m.group(2))].append(s["thr_half2"])
    return d


def mean(rows):
    return [sum(r[i] for r in rows) / len(rows) for i in range(len(rows[0]))]


b1, r2, r3 = load(u1, "u1"), load(u2, "u2"), load(u3, "u3")
lines = ["# Wave U3 summary: kwdirect retune on downlink cells (seeds 0-2, 60 s, second-half throughput, Mbps)", ""]
for cell in ("d3", "d4"):
    beb = mean(b1[(cell, "beb")])
    counts = [10] * len(beb)
    fl = gc.floors(beb, counts)
    stat = {m: mean(r) for (c, m), r in r2.items() if c == cell and m.startswith("f1-") and len(r) == 3}
    for al in (0, 1):
        ub = gc.utility(beb, counts, al)
        feas = {m: x for m, x in stat.items() if gc.feasible(x, fl, 0.05)}
        best = max(feas, key=lambda m: gc.utility(feas[m], counts, al))
        us = gc.utility(feas[best], counts, al)
        dflt = mean(r2[(cell, "kwdirect-a%d" % al)])
        lines += ["## Cell %s alpha %d  (U_BEB %.2f, U_static %.2f at %s, U_kwdirect default %.2f)" % (cell, al, ub, us, best, gc.utility(dflt, counts, al)), "",
                  "| eta | delta | tau | n | per-AP | U | share | feasible |", "|---|---|---|---|---|---|---|---|"]
        rows = []
        for (c, m), r in r3.items():
            mm = re.match(r"kw-e(\S+)-d(\S+)-t(\S+)-a(\d)$", m)
            if c != cell or int(mm.group(4)) != al or len(r) < 3:
                continue
            x = mean(r)
            rows.append((gc.utility(x, counts, al), mm.group(1), mm.group(2), mm.group(3), len(r), x))
        rows.sort(reverse=True)
        for u, e, d, t, n, x in rows[:8]:
            lines.append("| %s | %s | %s | %d | %s | %.2f | %.2f | %s |" % (e, d, t, n, " / ".join("%.1f" % v for v in x), u, (u - ub) / (us - ub),
                                                                       "yes" if gc.feasible(x, fl, 0.05) else "NO"))
        lines += ["", "Settings with fewer than 3 seeds (missing or failed jobs): %d" % sum(1 for (c, m), r in r3.items() if c == cell and m.endswith("a%d" % al) and len(r) < 3), ""]
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
