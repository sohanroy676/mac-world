import json, sys, numpy as np, collections
sys.path.insert(0, ".")
import cw_search_v4_1_0 as S
from gc_analysis import utility, floors, feasible
cells = json.load(open("../../../.github/waves/cells.json"))
SEEDS = set(range(200, 210)); TS = {0, 1, 2, 3}
rows = collections.defaultdict(dict)
for l in open("/tmp/w2t.jsonl"):
    r = json.loads(l); c = r["cfg"]
    if r["check"] != "PASS": continue
    rows[(c["mode"], c["apHidden"] and "s4" or "s2", c["lyEta"], c["lyDelta"])][c["seed"]] = r["thr_half2"]
for cell_name in ("s2", "s4"):
    cell = cells[cell_name]; counts = [int(x) for x in cell["args"][1].split(",")]
    cell["counts"] = counts
    pts, beb = S.load("/tmp/w1v.jsonl", cell, "f1", SEEDS, 60.0, "thr_half2")
    fl = floors([float(np.mean([beb[s][i] for s in sorted(beb)])) for i in range(len(counts))], counts)
    for alpha in (1,):
        ub = np.mean([utility(beb[s], counts, alpha) for s in beb])
        f1 = [ (np.mean([utility(v["thr"][s], counts, alpha) for s in SEEDS]), v["p"]["cws"]) for v in pts.values() if all(s in v["thr"] for s in SEEDS)]
        u1, p1 = max(f1, key=lambda t: t[0])
        print("== %s alpha %g BEB %.3f best F1 %.3f %s (seeds 0-3, 60 s)" % (cell_name, alpha, ub, u1, p1))
        for (mode, cn, eta, delta), d in sorted(rows.items()):
            if cn != cell_name or len(d) < 4: continue
            us = [utility(d[s], counts, alpha) for s in sorted(d)]
            mt = [float(np.mean([d[s][i] for s in d])) for i in range(len(counts))]
            print("%-8s eta %.2f delta %.2f U %.3f +-%.3f gap closed %.2f feasible %s thr %s" % (mode, eta, delta, np.mean(us), np.std(us, ddof=1), (np.mean(us)-ub)/(u1-ub), feasible(mt, fl, 0.05), [round(t,1) for t in mt]))
