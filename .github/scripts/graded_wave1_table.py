"""Table for graded wave 1: python3 graded_wave1_table.py <bundle_dir> > table.md. Mean over seeds of thr_policy (Mbps per AP), total, Jain over APs, sum ln thr."""
import glob, json, math, sys, collections
rows = collections.defaultdict(list)
for f in sorted(glob.glob(sys.argv[1] + "/*/*/summary.json")):
    s = json.load(open(f))
    if s["check"] != "PASS":
        print("CHECK FAIL", f, file=sys.stderr)
    c = s["cfg"]
    m = c["mode"] + (":" + c["apCws"] if c["apCws"] else "")
    rows[(c["apHidden"], m)].append(s["thr_policy"])
print("| cell | method | n | AP1 | AP2 | AP3 | total | Jain | sum ln | min AP |\n|---|---|---|---|---|---|---|---|---|---|")
for (cell, m), v in sorted(rows.items()):
    n = len(v)
    mean = [sum(x[i] for x in v) / n for i in range(3)]
    t = sum(mean)
    jain = t * t / (3 * sum(x * x for x in mean))
    ln = sum(math.log(max(x, 1e-3)) for x in mean)
    print("| %s | %s | %d | %.2f | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f |" % (cell, m, n, *mean, t, jain, ln, min(mean)))
