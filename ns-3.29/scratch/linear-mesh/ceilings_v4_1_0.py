"""v4.1.0 (max-CW plan, Wave 1): validated ceilings, Gate S and bounds from the wave summaries.

  python ceilings_v4_1_0.py --cells ../../../.github/waves/cells.json --summaries w1.jsonl w1v.jsonl --out ceilings.md

For every cell and alpha in 0, 1, 4: the best validated point of each family (F1 exact static, F2 static CWmin, F3 schedule
where the cell has one) on the fresh seeds 200-209 (60 s runs, scored on seconds 30-60 = "thr_half2"), its floor
feasibility against BEB on the same seeds, and the ceiling = the best feasible family. Gate S (S4): F3 beats the best
static family by more than 3 seed SDs of that family's utility AND by at least 0.05 of the BEB-to-F1 gap, and is feasible.
Bounds: bounds_v4_1_0.py with c_i = 51.82 Mbps (scheduled-access capacity, measured frame times) and with the floors.
Summaries are the JSON lines of .github/scripts/run_job.py. Analysis only: numpy and scipy.
"""
import argparse
import json
import math
import sys

import numpy as np

import bounds_v4_1_0 as B
import cw_search_v4_1_0 as S
from gc_analysis import feasible, floors, utility

CAP = 51.82  # Mbps, docs/design/measurement-modes-v4.1.0.md section 4
SEEDS = list(range(200, 210))
ALPHAS = (0, 1, 4)
FAMS = {"s2": ("f1", "f2"), "s4": ("f1", "f2", "f3"), "s5a": ("f1",), "s8p3": ("f1",)}
FLOOR_TOL = 0.05


def cell_info(cell):
    a = cell["args"]
    val = lambda flag, d: a[a.index(flag) + 1] if flag in a else d
    counts = [int(c) for c in val("--apStaCounts", "20,40").split(",")]
    loads = [float(v) for v in val("--apLoads", "").split(",")] if val("--apLoads", "") else [float(val("--offeredLoad", 150))] * len(counts)
    return counts, val("--apHidden", ""), loads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--summaries", nargs="+", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    cells = json.load(open(args.cells))
    lines = []
    out = lines.append
    out("| cell | alpha | BEB | best F1 | best F2 | best F3 | ceiling | gap closed | bound | ceiling / bound |")
    out("|---|---|---|---|---|---|---|---|---|---|")
    detail = []
    gate = []
    # the loader reads one file: concatenate
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for f in args.summaries:
        tmp.write(open(f).read())
    tmp.close()
    for name, fams in FAMS.items():
        cell = cells[name]
        counts, hidden, loads = cell_info(cell)
        cell["counts"] = counts
        per = {}
        for fam in fams:
            pts, beb = S.load(tmp.name, cell, fam, set(SEEDS), 60.0, "thr_half2")
            per[fam] = (pts, beb)
        beb = per[fams[0]][1]
        # BEB runs live with the first family of the cell (the others were built with --noBeb)
        for fam in fams:
            if not per[fam][1]:
                per[fam] = (per[fam][0], beb)
        seeds = sorted(beb)
        if len(seeds) < len(SEEDS):
            out("| %s | - | only %d of %d BEB seeds in the summaries | | | | | | | |" % (name, len(seeds), len(SEEDS)))
            continue
        fl = floors([float(np.mean([beb[s][i] for s in seeds])) for i in range(len(counts))], counts)
        demand = [n * l for n, l in zip(counts, loads)]
        for alpha in ALPHAS:
            ub = [utility(beb[s], counts, alpha) for s in seeds]
            best = {}
            for fam in fams:
                pts = per[fam][0]
                rows = []
                for k, v in pts.items():
                    if any(s not in v["thr"] for s in seeds):
                        continue
                    us = [utility(v["thr"][s], counts, alpha) for s in seeds]
                    mt = [float(np.mean([v["thr"][s][i] for s in seeds])) for i in range(len(counts))]
                    rows.append((float(np.mean(us)), us, v["p"], mt, feasible(mt, fl, FLOOR_TOL)))
                rows = [r for r in rows if r[4]]
                if rows:
                    best[fam] = max(rows, key=lambda r: r[0])
            if not best:
                out("| %s | %g | %.2f | no feasible validated point | | | | | | |" % (name, alpha, np.mean(ub)))
                continue
            fam_c = max(best, key=lambda f: best[f][0])
            u_c = best[fam_c][0]
            g1 = best["f1"][0] if "f1" in best else None
            gap = (u_c - np.mean(ub)) / (g1 - np.mean(ub)) if g1 is not None and g1 != np.mean(ub) else float("nan")
            r = B.solve(counts, B.parse_hidden(hidden, len(counts)), [CAP] * len(counts), demand, float(alpha), fl, FLOOR_TOL)
            ubd = r[0] if r else float("nan")
            cellf = lambda f: "%.2f (%s)" % (best[f][0], "/".join(str(c) for c in best[f][2]["cws"])) if f in best else "-"
            out("| %s | %g | %.2f | %s | %s | %s | %s %.2f | %.2f | %.2f | %s |" % (
                name, alpha, np.mean(ub), cellf("f1"), cellf("f2"), cellf("f3"), fam_c, u_c, gap, ubd,
                "%.2f" % ((u_c - np.mean(ub)) / (ubd - np.mean(ub))) if r else "-"))
            if name == "s4" and "f3" in best:
                stat = max((f for f in ("f1", "f2") if f in best), key=lambda f: best[f][0])
                sd = float(np.std(best[stat][1], ddof=1))
                diff = best["f3"][0] - best[stat][0]
                need_gap = 0.05 * (best["f1"][0] - np.mean(ub)) if "f1" in best else float("nan")
                gate.append((alpha, diff, sd, need_gap, diff > 3 * sd and diff >= need_gap))
    out("")
    out("Gate S (S4, schedule vs best static family, feasible points only): alpha | F3 - static | seed SD of static | 0.05 of BEB-to-F1 gap | pass")
    for g in gate:
        out("- alpha %g: %+.3f | %.3f | %.3f | %s" % (g[0], g[1], g[2], g[3], "PASS" if g[4] else "no"))
    os.unlink(tmp.name)
    txt = "\n".join(lines)
    print(txt)
    if args.out:
        open(args.out, "w").write(txt + "\n")


if __name__ == "__main__":
    sys.exit(main())
