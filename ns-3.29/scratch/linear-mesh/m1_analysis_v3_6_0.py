"""v3.6.0 (M1) analysis of the selection-seed grids (python seeds 0-2, tags m1-<cell>-<method>).

  ../../venv/bin/python m1_analysis_v3_6_0.py --batch ../../../docs/figures/v3.6.0-grids [--cells s4,s5a,s8p3,s2] [--s7 --s7load X] [--out report.md]

Per cell and alpha in {0,1,2}: feasible static oracle (gc_analysis.cell_table, 5 % floor slack), top statics, BEB.
Gates: per-AP idle slots / retry rate (policy window, mean over seeds, seed SD). IdleSense convergence from trace.csv.
S7: DELAY lines of the job logs (batch dir, <id>.log); cell delay = worst AP p99 (decision); oracle = lowest p99 static
that delivers >= 99 % of the offered load; GC_D on ln p99.
"""
import argparse
import csv
import glob
import json
import math
import os

import numpy as np

import gc_analysis as G

CELLS = {  # cell -> (topology, hidden, apLoads, offeredLoad)
    "s2": ("20,40", "", "", 10.0),
    "s4": ("10,10,10", "1-3", "", 10.0),
    "s5a": ("10,10,10", "1-3", "150,150,1", 150.0),
    "s8p3": ("10,10,10", "1-3", "", 10.0),
}
SEEDS = [0, 1, 2]


def trace_means(run_dir, cols=("idle", "retry", "loss")):
    rows = list(csv.DictReader(open(os.path.join(run_dir, "trace.csv"))))
    aps = sorted({int(r["ap"]) for r in rows})
    return {c: [float(np.mean([float(r[c]) for r in rows if int(r["ap"]) == a][300:])) for a in aps] for c in cols}


def load_cell(results, cell, tag_prefix=None):
    topo, hid, loads, off = CELLS[cell]
    runs = G.load_runs(results, topo, hid, loads, off, SEEDS, tag_prefix=tag_prefix or "m1-%s-" % cell)
    if cell == "s8p3":  # S4 shape and load with the schedule: keep only runs that have it
        for k in list(runs):
            for sd in list(runs[k]):
                if not json.load(open(os.path.join(runs[k][sd]["run_dir"], "config.json"))).get("staSchedule"):
                    del runs[k][sd]
    return runs


def cell_counts(cell):
    return [int(x) for x in CELLS[cell][0].split(",")]


def fmt(v):
    return "%.2f" % v


def report_cell(results, cell, out):
    runs = load_cell(results, cell)
    if "beb" not in runs:
        out.append("## %s: no BEB runs yet\n" % cell)
        return None
    counts = cell_counts(cell)
    out.append("## %s (%s, hidden %s, loads %s, load %s)\n" % ((cell,) + CELLS[cell]))
    oracles = {}
    for alpha in (0, 1, 2):
        rows, info = G.cell_table(runs, counts, alpha, floor_tol=0.05)
        oracles[alpha] = info["oracle"]
        out.append("alpha %d: oracle `%s`, U gap over BEB %.3f (BEB U SD %.3f), degenerate: %s, floors %s\n" % (
            alpha, info["oracle"], info["gap"], info["ub_sd"], info["degenerate"], [fmt(x) for x in info["floors"]]))
        top = sorted([r for r in rows if r["method"] != "beb"], key=lambda r: -r["umean"])[:6]
        out.append("| method | n | agg | min AP | feasible | U | GC |\n|---|---|---|---|---|---|---|")
        for r in [x for x in rows if x["method"] == "beb"] + top:
            gc = ("%.2f ± %.2f" % (r["gc"], r["gc_hw"])) if "gc" in r else "n/a"
            out.append("| %s | %d | %s | %s | %s | %.2f | %s |" % (r["method"], r["n"], fmt(r["agg"]), fmt(r["min_ap"]), r["feasible"], r["umean"], gc))
        out.append("")
    # per-AP throughput of BEB and the alpha-1 oracle, with idle / retry (gate evidence)
    out.append("| run | per-AP Mbps | idle slots per AP (SD over seeds) | retry rate per AP |\n|---|---|---|---|")
    for key in ["beb"] + sorted({o for o in oracles.values() if o}):
        by = runs[key]
        thr = np.mean([[by[s]["thr_policy"][a] for a in by[s]["aps"]] for s in by], axis=0)
        tm = [trace_means(by[s]["run_dir"]) for s in by]
        idle = np.array([t["idle"] for t in tm]); ret = np.array([t["retry"] for t in tm])
        out.append("| %s | %s | %s | %s |" % (key, ", ".join(fmt(x) for x in thr),
                   ", ".join("%.2f (%.2f)" % (m, s) for m, s in zip(idle.mean(0), idle.std(0, ddof=1) if len(idle) > 1 else idle.mean(0) * 0)),
                   ", ".join("%.3f" % x for x in ret.mean(0))))
    out.append("")
    return oracles


def gates(results, out):
    """G0a: at the S2 one-domain oracle both APs see nearly the same idle slots, stable over seeds.
    G0b: in S4 the edge APs and the middle AP differ in idle slots or retry rate by > 3 pooled seed SD (BEB and oracle)."""
    out.append("## Gates (proposed definitions; recorded as decisions)\n")
    r2 = load_cell(results, "s2")
    for key in sorted(r2):
        if key in ("beb", "idlesense") or key.startswith("static:"):
            by = r2[key]
            idle = np.array([trace_means(by[s]["run_dir"])["idle"] for s in by])
            m, sd = idle.mean(0), (idle.std(0, ddof=1) if len(idle) > 1 else idle.mean(0) * 0)
            ok = abs(m[0] - m[1]) <= 0.10 * m.mean() and all(sd <= 0.10 * m)
            out.append("G0a %s: idle %s SD %s -> %s" % (key, [fmt(x) for x in m], [fmt(x) for x in sd], "PASS" if ok else "FAIL"))
    r4 = load_cell(results, "s4")
    for key in sorted(r4):
        if key == "beb" or key in ("static:256-128-256",) or key.startswith("static:256,128") or key == "idlesense":
            by = r4[key]
            tm = [trace_means(by[s]["run_dir"]) for s in by]
            for c in ("idle", "retry"):
                a = np.array([t[c] for t in tm])
                edge, mid = (a[:, 0] + a[:, 2]) / 2, a[:, 1]
                pooled = math.sqrt((edge.var(ddof=1) + mid.var(ddof=1)) / 2) if len(a) > 1 else float("nan")
                z = abs(edge.mean() - mid.mean()) / pooled if pooled and pooled > 0 else float("inf")
                out.append("G0b %s %s: edge %.3f vs middle %.3f, |diff|/pooled SD = %.1f -> %s" % (key, c, edge.mean(), mid.mean(), z, "PASS" if z > 3 else "FAIL"))
    out.append("")


def idlesense_convergence(results, out):
    """Settled = from agent step 300 (3 s) every step's CW is within one exponent (factor 2) of the median CW of the last third of the run."""
    out.append("## IdleSense convergence (published rule, selection seeds)\n\n| cell | seed | AP | final median CW | first step within x2 and staying | settled by step 300 |\n|---|---|---|---|---|---|")
    for cell in ("s2", "s4"):
        for key, by in load_cell(results, cell).items():
            if key != "idlesense":
                continue
            for sd, r in sorted(by.items()):
                rows = list(csv.DictReader(open(os.path.join(r["run_dir"], "trace.csv"))))
                for ap in sorted({int(x["ap"]) for x in rows}):
                    cw = np.array([float(x["cw_set"]) for x in rows if int(x["ap"]) == ap])
                    med = float(np.median(cw[-len(cw) // 3:]))
                    ok = np.abs(np.log2(cw / med)) <= 1.0
                    bad = np.where(~ok)[0]
                    first = int(bad[-1] + 1) if len(bad) else 0
                    out.append("| %s | %d | %d | %.0f | %d | %s |" % (cell, sd, ap, med, first, "yes" if first <= 300 else "NO"))
    out.append("")


def delays(batch, results, load, out):
    """S7: worst-AP p99 per setting from the DELAY lines of the job logs; oracle = static with the lowest mean worst-AP p99
    among those that deliver >= 99 % on every AP. Delivered is judged against the largest packet count n seen for that AP
    and seed over all settings of the cell (inference: the config stores no offered packet count). GC_D on ln p99."""
    import re
    out.append("## S7 delay (p99 ms, worst AP; %s)\n" % load)
    for cell, counts in (("s7-s4", [10, 10, 10]), ("s7-s4b", [10, 10, 10]), ("s7-s2", [20, 40])):
        rows = {}
        for log in glob.glob(os.path.join(batch, "**", "%s-*.log" % cell), recursive=True):
            jid = os.path.basename(log)[:-4]
            m = re.match(r"%s-(.+)-s(\d)$" % re.escape(cell), jid)
            if not m:
                continue
            dl = re.findall(r"DELAY AP(\d+) n=(\d+) mean_ms=([\d.]+) p50_ms=([\d.]+) p99_ms=([\d.]+)", open(log).read())
            if dl:
                rows.setdefault(m.group(1), {})[int(m.group(2))] = [(int(n), float(p99)) for _, n, _, _, p99 in dl]
        if "beb" not in rows:
            continue
        maxn = {}
        for k in rows:
            for sd, v in rows[k].items():
                maxn[sd] = [max(a_, n) for a_, (n, _) in zip(maxn.get(sd, [0] * len(v)), v)]
        res = {}
        for k in sorted(rows):
            ok = all(n >= 0.99 * maxn[sd][i] for sd, v in rows[k].items() for i, (n, _) in enumerate(v))
            res[k] = (float(np.mean([max(p for _, p in rows[k][sd]) for sd in rows[k]])), ok, len(rows[k]))
        out.append("| %s method | worst-AP p99 ms (mean over seeds) | delivered >= 99 %% | seeds |\n|---|---|---|---|" % cell)
        for k, (v, ok, n) in sorted(res.items(), key=lambda kv: kv[1][0]):
            out.append("| %s | %.1f | %s | %d |" % (k, v, "yes" if ok else "NO", n))
        cand = {k: v for k, v in res.items() if k != "beb" and v[1] and v[2] == 3}
        if cand:
            o = min(cand, key=lambda k: cand[k][0])
            out.append("\nOracle (lowest p99, delivered >= 99 %%): **%s** p99 %.1f ms vs BEB %.1f ms (ln gap %.3f)\n" % (
                o, cand[o][0], res["beb"][0], math.log(res["beb"][0]) - math.log(cand[o][0])))
        else:
            out.append("\nNo static delivers >= 99 % on all APs: no oracle.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="../../../docs/figures/v3.6.0-grids")
    ap.add_argument("--results", default="results")
    ap.add_argument("--cells", default="s4,s5a,s8p3,s2")
    ap.add_argument("--s7load", default="", help="text for the S7 heading, e.g. 's7-s4 1.93 per STA; s7-s4b 1.93,1.0,1.93; s7-s2 0.37'")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    out = ["# M1 selection-seed analysis (python seeds 0-2)\n"]
    for c in a.cells.split(","):
        if c:
            report_cell(a.results, c, out)
    gates(a.results, out)
    idlesense_convergence(a.results, out)
    if a.s7load:
        delays(a.batch, a.results, a.s7load, out)
    txt = "\n".join(out)
    print(txt)
    if a.out:
        open(a.out, "w").write(txt)


if __name__ == "__main__":
    main()
