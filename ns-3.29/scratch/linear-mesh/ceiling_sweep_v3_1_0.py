"""v3.1.0: static CW sweep (ceiling) through OSCAR_multi_ap_train.py --mode static.
  run:   ../../venv/bin/python ceiling_sweep_v3_1_0.py run --grid pilot --seeds 0 --benchDir results/ceiling-v3.1.0 [--lanes 1]
  table: ../../venv/bin/python ceiling_sweep_v3_1_0.py table --benchDir results/ceiling-v3.1.0 --out docs/figures/v3.1.0 \
             --refs results/screen2-beb/manifest.csv results/screen2-global/manifest.csv
Static runs use the same trace.csv and policy window (steps >= 300) as BEB/Global, so they pair by seed with them.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import threading
import time

import numpy as np

DIAG = [32, 64, 128, 256, 384, 512, 768, 1023]
OFF = [32, 128, 512, 1023]
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
T2, T6 = "20,40", "10,10,10,10,10,10"
T3 = "10,10,10"  # v3.4.0 chain: run with --extraArgs "--apHidden 1-3" in its own --benchDir
DIAG3 = [64, 128, 256, 512, 768, 1023]
EDGE3, MID3 = [256, 512, 1023], [64, 128, 256]
FIELDS = ["topo", "cws", "seed", "run_dir", "result", "returncode", "seconds"]


def grid(name):
    """List of (topo, cws tuple)."""
    d2 = [(T2, (c, c)) for c in DIAG]
    off = [(T2, (a, b)) for a in OFF for b in OFF if a != b]
    d1 = [(T2, (64, 512)), (T2, (512, 64))]
    d6 = [(T6, (c,) * 6) for c in DIAG]
    if name == "pilot":
        return d2 + d1
    if name == "full2":
        return d2 + off + d1
    if name == "diag6":
        return d6
    if name == "chain3":  # common CW on the diagonal plus edge APs (1, 3) higher than the middle AP
        return [(T3, (c, c, c)) for c in DIAG3] + [(T3, (e, m, e)) for e in EDGE3 for m in MID3 if e != m]
    if name == "custom":  # --cws "512,128,512[;c1,c2,c3...]" on --topo
        return [(CLI_TOPO, tuple(int(c) for c in one.split(","))) for one in CLI_CWS.split(";")]
    if name == "all":
        return d2 + off + d1 + d6
    raise SystemExit("unknown grid " + name)


def ci(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return float(x.mean()), float("nan")
    return float(x.mean()), T95[len(x) - 1] * float(x.std(ddof=1)) / np.sqrt(len(x))


def fmt(x, d=2):
    m, h = ci(x)
    return "%.*f ± %.*f" % (d, m, d, h) if np.isfinite(h) else "%.*f (n=1)" % (d, m)


def pf_util(rs, seeds):
    """Per seed: sum over APs of log(policy-window Mbps); a starved AP is floored at 0.01 Mbps."""
    return [sum(np.log(max(0.01, rs[s]["thr_policy"][ap])) for ap in rs[s]["aps"]) for s in seeds]


def min_ap(rs, seeds):
    return [min(rs[s]["thr_policy"][ap] for ap in rs[s]["aps"]) for s in seeds]


def gate_chain3(by_cw):
    """v3.4.0 gate: best asymmetric (edge != middle) minus best common CW, paired by seed, for PF utility and min-AP."""
    common = {k: v for k, v in by_cw.items() if len(set(k.split(","))) == 1}
    asym = {k: v for k, v in by_cw.items() if len(set(k.split(","))) > 1}
    md = ["### Gate: best asymmetric vs best common CW (paired by seed)", ""]
    if not common or not asym:
        return md + ["n/a (need both common and asymmetric runs)", ""]
    for name, metric in (("PF utility", pf_util), ("min-AP Mbps", min_ap)):
        bc = max(common, key=lambda k: np.mean(metric(common[k], sorted(common[k]))))
        ba = max(asym, key=lambda k: np.mean(metric(asym[k], sorted(asym[k]))))
        ss = sorted(set(common[bc]) & set(asym[ba]))
        pc = dict(zip(sorted(common[bc]), metric(common[bc], sorted(common[bc]))))
        pa = dict(zip(sorted(asym[ba]), metric(asym[ba], sorted(asym[ba]))))
        d = [pa[x] - pc[x] for x in ss]
        md.append("- %s: best common cw=%s, best asymmetric cw=%s, difference %s (n=%d seeds)" % (name, bc, ba, fmt(d), len(ss)))
    md.append("")
    return md


def run(a):
    os.makedirs(a.benchDir, exist_ok=True)
    manifest = os.path.join(a.benchDir, "manifest.csv")
    done = set()
    if os.path.exists(manifest):
        done = {(r["topo"], r["cws"], int(r["seed"])) for r in csv.DictReader(open(manifest)) if r["result"] == "PASS"}
    else:
        with open(manifest, "w", newline="") as f:
            csv.DictWriter(f, FIELDS).writeheader()
    lock = threading.Lock()
    failed = []

    queue = [(seed, t, c) for seed in a.seeds for t, c in grid(a.grid) if (t, ",".join(map(str, c)), seed) not in done]
    print("%d jobs to run, %d already PASS, %d lane(s)" % (len(queue), len(done), a.lanes), flush=True)
    start_lock = threading.Lock()
    total = len(queue)

    def worker():
        while not failed:
            with start_lock:
                if not queue:
                    return
                seed, topo, cws = queue.pop(0)
                time.sleep(3)  # run dirs are stamped per second: stagger starts
            key = ",".join(map(str, cws))
            log = os.path.join(a.benchDir, "%s-cw%s-s%d.log" % (topo, key.replace(",", "_"), seed))
            cmd = [sys.executable, "OSCAR_multi_ap_train.py", "--apStaCounts", topo, "--mode", "static", "--apCws", key,
                   "--seed", str(seed), "--simTime", str(a.simTime), "--stepTime", "0.01", "--tag", "cw" + key.replace(",", "-")]
            cmd += a.extraArgs.split()
            if not a.no_check:
                cmd.append("--check")
            t0 = time.time()
            with open(log, "w") as lf:
                rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT).returncode
            text = open(log).read()
            m = re.search(r"out: (results/multi-ap-\S+)", text)
            ok = rc == 0 and "CHECK FAIL" not in text and (a.no_check or "RESULT: PASS" in text)
            row = dict(topo=topo, cws=key, seed=seed, run_dir=m.group(1) if m else "", result="PASS" if ok else "FAIL",
                       returncode=rc, seconds=int(time.time() - t0))
            with lock:
                with open(manifest, "a", newline="") as f:
                    csv.DictWriter(f, FIELDS).writerow(row)
                print("seed %d %s cw=%s -> %s (%d s) %s | %d left" % (seed, topo, key, row["result"], row["seconds"], row["run_dir"], len(queue)), flush=True)
            if not ok:
                failed.append(log)
                return

    threads = [threading.Thread(target=worker) for _ in range(a.lanes)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    if failed:
        sys.exit("job failed; see " + failed[0])
    print("batch complete")


def load_ref(paths, summarize):
    """(topo, mode) -> {seed: summary} from BEB/Global manifests (PASS rows)."""
    out = {}
    for p in paths:
        for r in csv.DictReader(open(p)):
            if r["result"] == "PASS":
                out.setdefault((r["topo"], r["mode"]), {})[int(r["seed"])] = summarize(r["run_dir"])
    return out


def table(a):
    from summarize_run import summarize
    S = lambda d: summarize(d, 0.01, 300)
    runs = {}  # (topo, cws) -> {seed: summary}
    for r in csv.DictReader(open(os.path.join(a.benchDir, "manifest.csv"))):
        if r["result"] == "PASS":
            runs.setdefault((r["topo"], r["cws"]), {})[int(r["seed"])] = S(r["run_dir"])
    refs = load_ref(a.refs, S)
    os.makedirs(a.out, exist_ok=True)
    md = ["# v3.1.0 static CW sweep tables", "",
          "Policy window = steps >= 300 (3 s of 15 s); mean ± 95% CI (Student t) over seeds; Mbps. Paired = same ns-3 seed.", ""]
    rows = []
    for topo in (T2, T6, T3):
        keys = sorted([k for k in runs if k[0] == topo], key=lambda k: [int(c) for c in k[1].split(",")])
        if not keys:
            continue
        md += ["## %s" % topo, ""]
        for mode in ("beb", "global"):
            if (topo, mode) in refs:
                v = [s["tot_policy"] for s in refs[(topo, mode)].values()]
                md.append("- %s reference (n=%d): %s" % (mode, len(v), fmt(v)))
        pfh, pfd = (" PF utility | min-AP |", "---|---|") if a.pf else ("", "")
        md += ["", "| CW per AP | n | aggregate | per-AP | Jain | phy loss |%s vs BEB (paired) | vs Global (paired) |" % pfh, "|---|---|---|---|---|---|%s---|---|" % pfd]
        for k in keys:
            rs = runs[k]
            seeds = sorted(rs)
            tot = [rs[s]["tot_policy"] for s in seeds]
            aps = sorted(rs[seeds[0]]["aps"])
            per = " / ".join("%.2f" % np.mean([rs[s]["thr_policy"][ap] for s in seeds]) for ap in aps)
            cells = []
            for mode in ("beb", "global"):
                ref = refs.get((topo, mode), {})
                ss = [s for s in seeds if s in ref]
                if ss:
                    d = [rs[s]["tot_policy"] - ref[s]["tot_policy"] for s in ss]
                    cells.append(fmt(d) if len(ss) == 1 else "%s (n=%d)" % (fmt(d), len(ss)))
                else:
                    cells.append("n/a")
            pfc = " %s | %s |" % (fmt(pf_util(rs, seeds)), fmt(min_ap(rs, seeds))) if a.pf else ""
            md.append("| %s | %d | %s | %s | %.2f | %.3f |%s %s | %s |" % (
                k[1], len(seeds), fmt(tot), per, np.mean([rs[s]["jain_policy"] for s in seeds]),
                np.mean([rs[s]["loss_policy"] for s in seeds]), pfc, cells[0], cells[1]))
            rows.append([topo, k[1], len(seeds), "%.4f" % np.mean(tot)])
        md.append("")
        best = max(keys, key=lambda k: np.mean([s["tot_policy"] for s in runs[k].values()]))
        md.append("Best by mean aggregate: cw=%s (%s)." % (best[1], fmt([s["tot_policy"] for s in runs[best].values()])))
        md.append("")
        if a.pf and topo == T3:
            md += gate_chain3({k[1]: runs[k] for k in keys})
    # D1 payoff matrix at 20,40 (per-AP throughput)
    pay = {k[1]: v for k, v in runs.items() if k[0] == T2 and k[1] in ("64,64", "64,512", "512,64", "512,512")}
    if len(pay) == 4:
        md += ["## D1 payoff matrix (20,40; rows = AP1 CW, cols = AP2 CW; cell = AP1 / AP2 Mbps, mean over seeds)", "",
               "| AP1 \\ AP2 | 64 | 512 |", "|---|---|---|"]
        for r in (64, 512):
            cs = []
            for c in (64, 512):
                rs = pay["%d,%d" % (r, c)]
                cs.append("%.2f / %.2f" % (np.mean([s["thr_policy"][s["aps"][0]] for s in rs.values()]), np.mean([s["thr_policy"][s["aps"][1]] for s in rs.values()])))
            md.append("| %d | %s | %s |" % (r, cs[0], cs[1]))
        md.append("")
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(md))
    with open(os.path.join(a.out, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["topo", "cws", "n", "aggregate_mbps_mean"])
        w.writerows(rows)
    print("\n".join(md))


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
r = sub.add_parser("run")
r.add_argument("--grid", choices=["pilot", "full2", "diag6", "chain3", "custom", "all"], required=True)
r.add_argument("--topo", default="", help="topology for --grid custom, e.g. 10,10,10")
r.add_argument("--cws", default="", help="for --grid custom: ';'-separated per-AP CW lists, e.g. 512,128,512")
r.add_argument("--extraArgs", default="", help="extra trainer args for every job, e.g. '--apHidden 1-3'")
r.add_argument("--seeds", nargs="+", type=int, default=[0])
r.add_argument("--lanes", type=int, default=1)
r.add_argument("--simTime", type=float, default=15)
r.add_argument("--benchDir", default="results/ceiling-v3.1.0")
r.add_argument("--no-check", action="store_true")
t = sub.add_parser("table")
t.add_argument("--benchDir", default="results/ceiling-v3.1.0")
t.add_argument("--out", default="../../../docs/figures/v3.1.0")
t.add_argument("--refs", nargs="+", default=[])
t.add_argument("--pf", action="store_true", help="add PF utility (sum log per-AP Mbps) and min-AP columns, and the v3.4.0 gate comparison for 10,10,10")
args = p.parse_args()
CLI_TOPO, CLI_CWS = getattr(args, "topo", ""), getattr(args, "cws", "")
assert args.cmd != "run" or args.grid != "custom" or (CLI_TOPO and CLI_CWS), "--grid custom needs --topo and --cws"
run(args) if args.cmd == "run" else table(args)
