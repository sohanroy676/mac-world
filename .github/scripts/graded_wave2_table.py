"""Table for graded wave 2: python3 graded_wave2_table.py <bundle_dir>. Learners: mean over eval seeds 105-109 per training seed, then range over training seeds. Refs and grid: mean over seeds."""
import glob, json, math, sys, collections
rows = collections.defaultdict(lambda: collections.defaultdict(list))
for f in sorted(glob.glob(sys.argv[1] + "/*/*/summary.json")):
    s = json.load(open(f))
    assert s["check"] == "PASS", f
    c = s["cfg"]
    if s["name"] == "train":
        continue
    mode = {"shared": "rafa"}.get(c["mode"], c["mode"]) + (":" + c["apCws"] if c["apCws"] else "")
    seeds = "eval105-109" if c["seed"] >= 105 else "grid100-102"
    t = s["job"].rsplit("-", 1)[-1] if s["job"].count("-t") and mode in ("rafa", "global") else ""
    rows[(c["apHidden"], seeds, mode)][t].append(s["thr_policy"])
def stats(v):
    n = len(v); m = [sum(x[i] for x in v) / n for i in range(3)]; tot = sum(m)
    return m, tot, tot * tot / (3 * sum(x * x for x in m)), sum(math.log(max(x, 1e-3)) for x in m)
print("| cell | seeds | method | runs | AP1 | AP2 | AP3 | total | Jain | sum ln (per train seed) |\n|---|---|---|---|---|---|---|---|---|---|")
for (cell, seeds, mode), by in sorted(rows.items()):
    allv = [x for v in by.values() for x in v]
    m, tot, j, ln = stats(allv)
    per = ", ".join("%.2f" % stats(v)[3] for t, v in sorted(by.items())) if "" not in by else "%.2f" % ln
    print("| %s | %s | %s | %d | %.2f | %.2f | %.2f | %.2f | %.3f | %s |" % (cell, seeds, mode, len(allv), *m, tot, j, per))
