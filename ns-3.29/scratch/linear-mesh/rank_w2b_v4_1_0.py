"""Wave 2b ranking: BEB references (seeds 0-3, 60 s) vs floor-guarded controllers. Usage: rank_w2b_v4_1_0.py w2b.jsonl"""
import collections, json, sys
import numpy as np
sys.path.insert(0, ".")
from gc_analysis import feasible, utility
FLOORS = {"s2": [9.3, 17.19], "s4": [24.44, 1.31, 24.44], "s5a": [15.03, 11.25, 10.0]}
cells = json.load(open("../../../.github/waves/cells.json"))
def cell_of(c):
    for n, v in cells.items():
        a = v["args"]; g = lambda f, d: a[a.index(f) + 1] if f in a else d
        if c["apStaCounts"] == g("--apStaCounts", "20,40") and (c["apHidden"] or "") == g("--apHidden", "") and (c["apLoads"] or "") == g("--apLoads", "") \
           and abs(float(c["offeredLoad"]) - float(g("--offeredLoad", 150))) < 1e-9 and (c["staSchedule"] or "") == g("--staSchedule", ""):
            return n
rows = collections.defaultdict(dict)
for l in open(sys.argv[1]):
    r = json.loads(l); c = r["cfg"]
    if r["check"] != "PASS": continue
    key = (cell_of(c), c["mode"], c["lyEta"] if c["mode"] != "beb" else 0, c["lyDelta"] if c["mode"] != "beb" else 0, c["lyBeta"] if c["mode"] in ("coord", "qcsma") else 0)
    rows[key][c["seed"]] = r["thr_half2"]
for cell in ("s2", "s4", "s5a", "s7a", "s7b", "s8p3"):
    counts = [int(x) for x in cells[cell]["args"][1].split(",")]
    beb = rows.get((cell, "beb", 0, 0, 0))
    if not beb: continue
    ub = np.mean([utility(v, counts, 1) for v in beb.values()])
    bm = [float(np.mean([v[i] for v in beb.values()])) for i in range(len(counts))]
    print("== %s BEB U %.3f thr %s" % (cell, ub, [round(x, 1) for x in bm]))
    for key, d in sorted(rows.items(), key=lambda kv: str(kv[0])):
        if key[0] != cell or key[1] == "beb" or len(d) < 4: continue
        us = [utility(v, counts, 1) for v in d.values()]
        mt = [float(np.mean([v[i] for v in d.values()])) for i in range(len(counts))]
        fl = FLOORS.get(cell)
        print("  %-8s eta %.2f delta %.2f beta %.1f  U %.3f +-%.3f feasible %s thr %s" % (key[1], key[2], key[3], key[4], np.mean(us), np.std(us, ddof=1), feasible(mt, fl, 0.05) if fl else "-", [round(t, 1) for t in mt]))
