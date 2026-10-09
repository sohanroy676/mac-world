"""v0.9.0: summarize a multi-AP trainer run (trace.csv) as a markdown table.
Usage: ../../venv/bin/python summarize_run.py results/multi-ap-<ts> [--stepTime 0.01] [--warmup 300]
v1.1.0: the metric computation is `summarize()` so aggregate_bench.py can reuse it (same policy window for every mode).
"""
import argparse
import csv
import os

import numpy as np

from multi_ap import PAYLOAD_BITS, jain


def summarize(run_dir, step_time=0.01, warmup=300):
    """Per-AP and global metrics of one run. Policy window = steps after `warmup` (same for every mode)."""
    rows = list(csv.DictReader(open(os.path.join(run_dir, "trace.csv"))))
    aps = sorted({int(r["ap"]) for r in rows})
    by = {a: [r for r in rows if int(r["ap"]) == a] for a in aps}
    f = lambda a, k: np.array([float(r[k]) for r in by[a]])
    thr = {a: f(a, "rx") * PAYLOAD_BITS / (step_time * 1e6) for a in aps}
    tot = sum(thr.values())
    tx = sum(f(a, "tx") for a in aps)
    rx = sum(f(a, "rx") for a in aps)
    pol = slice(warmup, None)
    return {
        "aps": aps, "step_time": step_time, "warmup": warmup,
        "cw": {a: f(a, "cw_set") for a in aps}, "thr": thr, "tot": tot,
        "reward": {a: f(a, "reward") for a in aps},
        "tx": {a: f(a, "tx") for a in aps}, "rx": {a: f(a, "rx") for a in aps},
        "thr_policy": {a: thr[a][pol].mean() for a in aps},
        "tot_policy": tot[pol].mean(), "tot_all": tot.mean(),
        "jain_policy": jain([thr[a][pol].mean() for a in aps]),
        "loss_policy": 1 - rx[pol].sum() / max(tx[pol].sum(), 1),
        "loss_all": 1 - rx.sum() / max(tx.sum(), 1),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--stepTime", type=float, default=0.01)
    parser.add_argument("--warmup", type=int, default=300)
    args = parser.parse_args()

    s = summarize(args.run_dir, args.stepTime, args.warmup)
    aps, thr, tot, pol = s["aps"], s["thr"], s["tot"], slice(args.warmup, None)
    f = lambda a, k: s[k][a]

    print("| Metric | " + " | ".join("AP%d" % a for a in aps) + " | Global |")
    print("|---|" + "---|" * (len(aps) + 1))

    def line(name, vals, g):
        print("| %s | %s | %s |" % (name, " | ".join("%.3f" % v for v in vals), g))

    line("CW mean (all)", [f(a, "cw").mean() for a in aps], "")
    line("CW mean warm-up", [f(a, "cw")[:args.warmup].mean() for a in aps], "")
    line("CW mean policy", [f(a, "cw")[pol].mean() for a in aps], "")
    line("CW first-100 mean", [f(a, "cw")[:100].mean() for a in aps], "")
    line("CW last-100 mean", [f(a, "cw")[-100:].mean() for a in aps], "")
    line("Throughput Mbps (all)", [thr[a].mean() for a in aps], "%.3f" % s["tot_all"])
    line("Throughput Mbps (policy)", [thr[a][pol].mean() for a in aps], "%.3f" % s["tot_policy"])
    tx = sum(s["tx"][a] for a in aps)
    rx = sum(s["rx"][a] for a in aps)
    line("Loss ratio (sum rx/tx)", [1 - s["rx"][a].sum() / max(s["tx"][a].sum(), 1) for a in aps],
         "%.3f" % (1 - rx.sum() / max(tx.sum(), 1)))
    line("Reward mean (policy)", [f(a, "reward")[pol].mean() for a in aps], "")
    line("Fairness (Jain, mean thr)", [], "%.3f" % jain([thr[a].mean() for a in aps]))


if __name__ == "__main__":
    main()
