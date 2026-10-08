"""v0.9.0: summarize a multi-AP trainer run (trace.csv) as a markdown table.
Usage: ../../venv/bin/python summarize_run.py results/multi-ap-<ts> [--stepTime 0.01] [--warmup 300]
"""
import argparse
import csv
import os

import numpy as np

from multi_ap import PAYLOAD_BITS, jain

parser = argparse.ArgumentParser()
parser.add_argument("run_dir")
parser.add_argument("--stepTime", type=float, default=0.01)
parser.add_argument("--warmup", type=int, default=300)
args = parser.parse_args()

rows = list(csv.DictReader(open(os.path.join(args.run_dir, "trace.csv"))))
aps = sorted({int(r["ap"]) for r in rows})
by = {a: [r for r in rows if int(r["ap"]) == a] for a in aps}
f = lambda a, k: np.array([float(r[k]) for r in by[a]])
thr = {a: f(a, "rx") * PAYLOAD_BITS / (args.stepTime * 1e6) for a in aps}
tot = sum(thr.values())
pol = slice(args.warmup, None)

print("| Metric | " + " | ".join("AP%d" % a for a in aps) + " | Global |")
print("|---|" + "---|" * (len(aps) + 1))


def line(name, vals, g):
    print("| %s | %s | %s |" % (name, " | ".join("%.3f" % v for v in vals), g))


line("CW mean (all)", [f(a, "cw_set").mean() for a in aps], "")
line("CW mean warm-up", [f(a, "cw_set")[:args.warmup].mean() for a in aps], "")
line("CW mean policy", [f(a, "cw_set")[pol].mean() for a in aps], "")
line("CW first-100 mean", [f(a, "cw_set")[:100].mean() for a in aps], "")
line("CW last-100 mean", [f(a, "cw_set")[-100:].mean() for a in aps], "")
line("Throughput Mbps (all)", [thr[a].mean() for a in aps], "%.3f" % tot.mean())
line("Throughput Mbps (policy)", [thr[a][pol].mean() for a in aps], "%.3f" % tot[pol].mean())
tx = sum(f(a, "tx") for a in aps)
rx = sum(f(a, "rx") for a in aps)
line("Loss ratio (sum rx/tx)", [1 - f(a, "rx").sum() / max(f(a, "tx").sum(), 1) for a in aps],
     "%.3f" % (1 - rx.sum() / max(tx.sum(), 1)))
line("Reward mean (policy)", [f(a, "reward")[pol].mean() for a in aps], "")
line("Fairness (Jain, mean thr)", [], "%.3f" % jain([thr[a].mean() for a in aps]))
