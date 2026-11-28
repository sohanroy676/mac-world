"""Wave U4 learned (per-scenario RAFA, wide CW 4-1024, downlink-aware obs) vs the C1 methods on the SAME seeds: alpha 1 seeds 103-110, alpha 0 and 4 seeds 103-104.
All training seeds are reported (no selection). Usage: apdir_u4_learned_analyse.py U4L_BUNDLES C1A C1B OUT.md"""
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

l_root, c1a, c1b, out = sys.argv[1:5]
SEEDS = {1: range(103, 111), 0: range(103, 105), 4: range(103, 105)}
c1 = {}
for root in (c1a, c1b):
    for f in glob.glob(os.path.join(root, "c1-*", "run", "summary.json")):
        s = json.load(open(f))
        if s["check"] == "PASS":
            m = re.match(r"c1-(\w+?)-(.+)-s(\d+)$", s["job"])
            c1[(m.group(1), m.group(2), int(m.group(3)))] = s["thr_half2"]
lr = {}
for f in glob.glob(os.path.join(l_root, "u4-*", "eval-a*-s*", "summary.json")):
    s = json.load(open(f))
    m = re.match(r".*/u4-(\w+?)-rafa-t(\d+)/eval-a(\d)-s(\d+)/", f)
    if s["check"] == "PASS":
        lr[(m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)))] = s["thr_half2"]


def mean(rows):
    return [sum(r[i] for r in rows) / len(rows) for i in range(len(rows[0]))]


lines = ["# Wave U4: learned per-scenario RAFA vs C1 methods on the same seeds", "",
         "RAFA: `--mode shared --obs rafa --reward fair --alphaInput`, 6 episodes x 15 s, floor lambda 1, CW range 4-1024, `--rafaDlObs`. 4 training seeds (2000-2003) per cell, "
         "none selected. alpha 1: seeds 103-110; alpha 0 and 4: seeds 103-104. share = (U - U_BEB) / (U_static - U_BEB), U_BEB and U_static on the same seeds. "
         "Floors: BEB-based fair floors, 5 % slack.", ""]
for cell in ("u3", "d3", "b3", "m3", "d4", "b4"):
    counts = [int(c) for c in u2.CELLS[cell][0].split(",")]
    oracle = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "results", "uplink-downlink-oracle-points-v4.2.0.json")))[cell]
    for al in (1, 0, 4):
        seeds = SEEDS[al]
        beb = mean([c1[(cell, "beb", s)] for s in seeds])
        fl = gc.floors(beb, counts)
        ub = gc.utility(beb, counts, al)
        st = mean([c1[(cell, "f1-a%d" % al, s)] for s in seeds])
        us = gc.utility(st, counts, al)
        kw = mean([c1[(cell, "kwdirect-a%d" % al, s)] for s in seeds])
        lines += ["## %s alpha %d (seeds %d-%d)" % (cell, al, seeds[0], seeds[-1]), "", "| method | n | per-AP | U | share | feasible |", "|---|---|---|---|---|---|"]

        def row(name, x, n):
            u = gc.utility(x, counts, al)
            sh = "%.2f" % ((u - ub) / (us - ub)) if al != 4 else "-"
            lines.append("| %s | %d | %s | %.2f | %s | %s |" % (name, n, " / ".join("%.1f" % v for v in x), u, sh, "yes" if gc.feasible(x, fl, 0.05) else "NO"))
        row("BEB", beb, len(seeds))
        row("static %s" % oracle[str(al)], st, len(seeds))
        row("kwdirect", kw, len(seeds))
        shares = []
        for ts in range(2000, 2004):
            rows = [lr[(cell, ts, al, s)] for s in seeds if (cell, ts, al, s) in lr]
            if len(rows) == len(seeds):
                x = mean(rows)
                row("RAFA t%d" % ts, x, len(rows))
                shares.append(gc.utility(x, counts, al))
        if shares and al != 4:
            lines.append("| RAFA mean of training seeds | %d | | %.2f | %.2f | |" % (len(shares), sum(shares) / len(shares), (sum(shares) / len(shares) - ub) / (us - ub)))
        lines.append("")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
