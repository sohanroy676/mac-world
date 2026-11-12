"""v3.8.0 M2c: apply the pre-registered selection rule (docs/results/m2c-preregistration-v4.0.0.md) to gc_analysis.py markdown output.
Usage: python3 m2c_select.py s2=gc_s2.md s4=gc_s4.md s5a=gc_s5a.md
Rule: per method (ccod, global, pf), cell and alpha, the strongest training seed = highest mean GC over seeds 100-102;
feasible seeds first, an infeasible seed only if none is feasible; cells with raw U only (degenerate) rank on U."""
import re
import sys

METHODS = {"ccod": "CCOD", "global": "Global", "pf": "PF learner"}
rows = []
for arg in sys.argv[1:]:
    cell, path = arg.split("=")
    alpha = None
    degenerate = False
    for line in open(path):
        m = re.match(r"### alpha = (\S+)", line)
        if m:
            alpha = m.group(1)
            degenerate = False
            continue
        if "degenerate cell" in line:
            degenerate = True
        m = re.match(r"\| (ccod|global|pf)t(\d) \| \d+ \| \S+ \| (\S+) \| (\S+) \| (\S+)(?: ± (\S+))? \| (\*\*infeasible\*\*|ok) \|", line)
        if m:
            fam, seed, mn, u, gc, ci, feas = m.groups()
            score = float(u) if degenerate or gc == "n/a" else float(gc)
            rows.append((cell, alpha, fam, int(seed), float(mn), float(u), gc, ci, feas == "ok", score, degenerate or gc == "n/a"))
print("| Cell | alpha | Method | Selected seed | Score (GC, or U when degenerate) | min-AP Mbps | Feasible | Other seeds (score, feasible) |")
print("|---|---|---|---|---|---|---|---|")
for cell in ("s2", "s4", "s5a"):
    for alpha in ("0", "1", "4"):
        for fam, name in METHODS.items():
            c = [r for r in rows if r[0] == cell and r[1] == alpha and r[2] == fam]
            if not c:
                continue
            feas = [r for r in c if r[8]]
            best = max(feas or c, key=lambda r: r[9])
            others = ", ".join("t%d %.3f %s" % (r[3], r[9], "ok" if r[8] else "INF") for r in sorted(c, key=lambda r: r[3]) if r is not best)
            print("| %s | %s | %s | t%d | %.3f%s | %.2f | %s | %s |" % (cell.upper(), alpha, name, best[3], best[9], " (U)" if best[10] else "", best[4], "yes" if best[8] else "NO (none feasible)" if not feas else "yes", others))
