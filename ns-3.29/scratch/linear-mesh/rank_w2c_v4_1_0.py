"""Wave 2c ranking: share of the (validated BEB to ceiling) gap per cell, alpha and setting. Usage: rank_w2c_v4_1_0.py w2c.jsonl [w2b.jsonl]"""
import collections, json, sys
import numpy as np
sys.path.insert(0, ".")
from gc_analysis import feasible, utility
FLOORS = {"s2": [9.3, 17.19], "s4": [24.44, 1.31, 24.44], "s5a": [15.03, 11.25, 10.0]}
BEB = {("s2", 0): 27.90, ("s2", 1): -46.49, ("s2", 4): -218.41, ("s4", 0): 73.31, ("s4", 1): 4.65, ("s4", 4): -8995.95, ("s5a", 0): 45.09, ("s5a", 1): 9.86, ("s5a", 4): -5.93}
CEIL = {("s2", 0): 39.72, ("s2", 1): -24.83, ("s2", 4): -69.27, ("s4", 0): 77.28, ("s4", 1): 21.39, ("s4", 4): -1.54, ("s5a", 0): 49.98, ("s5a", 1): 13.28, ("s5a", 4): -4.24}
cells = json.load(open("../../../.github/waves/cells.json"))
def cell_of(c):
    for n, v in cells.items():
        a = v["args"]; g = lambda f, d: a[a.index(f) + 1] if f in a else d
        if c["apStaCounts"] == g("--apStaCounts", "20,40") and (c["apHidden"] or "") == g("--apHidden", "") and (c["apLoads"] or "") == g("--apLoads", "") \
           and abs(float(c["offeredLoad"]) - float(g("--offeredLoad", 150))) < 1e-9:
            return n
rows = collections.defaultdict(dict)
for f in sys.argv[1:]:
    for l in open(f):
        r = json.loads(l); c = r["cfg"]
        if r["check"] != "PASS" or c["mode"] == "beb": continue
        rows[(cell_of(c), c["lyAlpha"], c["mode"], c["lyEta"], c["lyDelta"], c["lyBeta"] if c["mode"] == "coord" else 0, c["lyTau"])][c["seed"]] = r["thr_half2"]
best = {}
for key, d in sorted(rows.items(), key=lambda kv: str(kv[0])):
    cell, alpha = key[0], key[1]
    if len(d) < 4 or (cell, int(alpha)) not in BEB: continue
    counts = [int(x) for x in cells[cell]["args"][1].split(",")]
    us = [utility(v, counts, alpha) for v in d.values()]
    mt = [float(np.mean([v[i] for v in d.values()])) for i in range(len(counts))]
    ok = feasible(mt, FLOORS[cell], 0.05)
    sh = (np.mean(us) - BEB[(cell, int(alpha))]) / (CEIL[(cell, int(alpha))] - BEB[(cell, int(alpha))])
    print("%s a%g %-8s e%.2f d%.2f b%.1f tau%.1f U %9.3f share %5.2f feasible %s" % (cell, alpha, key[2], key[3], key[4], key[5], key[6], np.mean(us), sh, ok))
    if ok and sh > best.get((cell, alpha, key[2]), (-9,))[0]:
        best[(cell, alpha, key[2])] = (sh, key[3:])
print("\nBest feasible share per cell, alpha, mode:")
for k, v in sorted(best.items()):
    print(k, "share %.2f at eta/delta/beta %s" % v)
