"""v3.7.0 (M2) scoring of the KW / UCB tuning sweep on selection seeds 0-2 at 30 s (tags m2tune-<cell>-<method>).

  ../../venv/bin/python m2_tune_analysis.py [--results results] [--out FILE]

Selection rule fixed before the runs: per method setting, mean alpha-1 GC over S2 and S4; settings that are floor-feasible
(5 % slack) on both cells compete; the highest wins. References (BEB, static oracles) are the 30 s runs with tags m2tune-<cell>-beb/static.
"""
import argparse

import numpy as np

import gc_analysis as G

CELLS = {"s2": ("20,40", "", 10.0, [20, 40]), "s4": ("10,10,10", "1-3", 10.0, [10, 10, 10])}
KW = ["kw-0.2-0.1", "kw-0.7-0.1", "kw-0.7-0.03", "kw-0.7-0.01"]
UCB = ["ucb-0.1", "ucb-0.3", "ucb-1"]


def runs_for(results, cell):
    topo, hid, off, _ = CELLS[cell]
    runs = {}
    for ref in ("beb", "static"):
        for k, v in G.load_runs(results, topo, hid, "", off, [0, 1, 2], tag_prefix="m2tune-%s-%s" % (cell, ref)).items():
            runs[k] = v
    for m in KW + UCB:
        r = G.load_runs(results, topo, hid, "", off, [0, 1, 2], tag_prefix="m2tune-%s-%s" % (cell, m))
        for _, v in r.items():
            runs[m] = v
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    out, score = ["# M2 tuning sweep (selection seeds 0-2, 30 s)\n"], {}
    for cell, (_, _, _, counts) in CELLS.items():
        runs = runs_for(a.results, cell)
        for alpha in (0, 1, 2):
            rows, info = G.cell_table(runs, counts, alpha, 0.05)
            out.append("## %s alpha %d: oracle %s, U gap %.3f (BEB SD %.3f)%s\n" % (cell, alpha, info["oracle"], info["gap"], info["ub_sd"], ", DEGENERATE" if info["degenerate"] else ""))
            out.append("| method | n | agg | min-AP | GC | floor |\n|---|---|---|---|---|---|")
            for r in rows:
                if r["method"].startswith(("kw", "ucb")):
                    gc = "%.2f ± %.2f" % (r["gc"], r["gc_hw"]) if "gc" in r else "n/a (U %.1f)" % r["umean"]
                    out.append("| %s | %d | %.1f | %.2f | %s | %s |" % (r["method"], r["n"], r["agg"], r["min_ap"], gc, "ok" if r["feasible"] else "**infeasible**"))
                    if alpha == 1:
                        score.setdefault(r["method"], {})[cell] = (r.get("gc", float("nan")), r["feasible"])
            out.append("")
    out.append("## Selection (mean alpha-1 GC over S2 and S4, floor-feasible on both)\n\n| setting | GC S2 | GC S4 | mean | feasible both |\n|---|---|---|---|---|")
    pick = {}
    for fam, names in (("kw", KW), ("ucb", UCB)):
        best = None
        for m in names:
            s = score.get(m, {})
            if len(s) < 2:
                continue
            mean = float(np.mean([s[c][0] for c in CELLS]))
            ok = all(s[c][1] for c in CELLS)
            out.append("| %s | %.2f | %.2f | %.2f | %s |" % (m, s["s2"][0], s["s4"][0], mean, "yes" if ok else "no"))
            if ok and (best is None or mean > best[1]):
                best = (m, mean)
        pick[fam] = best
    out.append("\nWinner kw: %s; winner ucb: %s" % (pick["kw"], pick["ucb"]))
    txt = "\n".join(out)
    print(txt)
    if a.out:
        open(a.out, "w").write(txt)


if __name__ == "__main__":
    main()
