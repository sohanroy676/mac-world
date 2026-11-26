#!/usr/bin/env python3
"""Stage-1 selection for the report cells: reads the stage-1 summaries (rs1-*) and writes SEL.json for `rep_batch.py s2`.

  rep_select.py stage1/summaries.jsonl SEL.json
Per cell (seeds 0-2, 60 s, scored on the second half = thr_half2):
  floors      = gc_analysis.floors(BEB mean per AP, STAs per AP), the --floors argument of kwdirect (as in Wave 3a)
  common_a0   = common static CW (grid 16..1024) with the highest station-weighted alpha 0 utility among the floor-feasible points (x_i >= 0.95 floor_i), else the highest
  common_a1   = the same for alpha 1
  model       = static CW per AP from the Patras et al. (TMC 2011) rule, CW = 2/tau - 1 with tau = (1/n) sqrt(2 Te / Tc), n = STAs of the AP's own BSS,
                Te = 9 us (slot), Tc = 242 us (measured, Wave 0)
  prop        = common_a1 x n_i / mean(n), rounded
Nothing here uses the evaluation seeds 400-409."""
import json
import math
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "ns-3.29/scratch/linear-mesh")
import gc_analysis as g

cells = json.load(open(".github/waves/rep/cells.json"))
runs = defaultdict(lambda: defaultdict(dict))  # cell -> key -> seed -> thr
for line in open(sys.argv[1]):
    r = json.loads(line)
    m = re.match(r"rs1-(\w+?)-(beb|cw\d+)-s(\d+)$", r["job"])
    if m and r.get("check") == "PASS":
        runs[m.group(1)][m.group(2)][int(m.group(3))] = r["thr_half2"]
sel, miss = {}, []
for cell, c in cells.items():
    if c.get("partial"):
        continue
    cnt = c["counts"]
    beb = runs[cell]["beb"]
    if len(beb) < 3:
        miss.append((cell, "beb", len(beb)))
        continue
    bm = np.mean([beb[s] for s in sorted(beb)], axis=0).tolist()
    fl = g.floors(bm, cnt)
    out = {"floors": ",".join("%.2f" % f for f in fl), "beb_mean": [round(x, 2) for x in bm]}
    for al in (0, 1):
        best = None
        for key, d in runs[cell].items():
            if key == "beb":
                continue
            if len(d) < 3:
                miss.append((cell, key, len(d)))
                continue
            thr = np.mean([d[s] for s in sorted(d)], axis=0).tolist()
            ok = g.feasible(thr, fl, 0.05)
            u = np.mean([g.utility(d[s], cnt, al) for s in d])
            if best is None or (ok, u) > (best[0], best[1]):
                best = (ok, u, int(key[2:]), thr)
        out["common_a%d" % al] = best[2]
        out["common_a%d_feasible" % al] = bool(best[0])
    k = math.sqrt(2 * 9e-6 / 242e-6)
    out["model"] = ",".join(str(max(4, int(round(2 * n / k - 1)))) for n in cnt)
    mean_n = sum(cnt) / len(cnt)
    out["prop"] = ",".join(str(max(4, int(round(out["common_a1"] * n / mean_n)))) for n in cnt)
    sel[cell] = out
json.dump(sel, open(sys.argv[2], "w"), indent=1)
print(len(sel), "cells selected; missing/short:", miss[:10])
