"""v1.0.0: standard 802.11 BEB baseline on the multi-AP topology (ns-3 --dryRun, no agent).
Usage: ../../venv/bin/python baseline_beb.py --apStaCounts 2,3 [--simTime 15] [--stepTime 0.01] [--seed 1]
Throughput = received * PAYLOAD_BITS / simTime (dry-run counters cover the whole run incl. the 1 s warm-up,
so this is an approximation of the trainer's per-step mean; see docs/core-v1.0.0.md).
--seed is the ns-3 seed (>=1); the trainer uses ns-3 seed = python seed + 1.
"""
import argparse
import os
import re
import subprocess
import tempfile

from multi_ap import PAYLOAD_BITS, jain

parser = argparse.ArgumentParser()
parser.add_argument("--apStaCounts", default="2,3")
parser.add_argument("--simTime", type=float, default=15)
parser.add_argument("--stepTime", type=float, default=0.01)
parser.add_argument("--seed", type=int, default=1)
args = parser.parse_args()

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
binary = os.path.join(root, "build/scratch/linear-mesh/linear-mesh")
env = dict(os.environ, LD_LIBRARY_PATH=os.path.join(root, "build/lib"))
cmd = [binary, "--dryRun=true", "--disableGym=true", "--apStaCounts=" + args.apStaCounts,
       "--simTime=%g" % args.simTime, "--envStepTime=%g" % args.stepTime, "--seed=%d" % args.seed]
with tempfile.TemporaryDirectory() as cwd:  # cw.csv is written to cwd
    out = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, check=True)
text = out.stdout + out.stderr
assert "Per-AP statistics check: PASS" in text, "per-AP statistics check did not pass"

ap = re.findall(r"^AP(\d+) stas=\d+ sent_phy=(\d+) .*? received=(\d+) ", text, re.M)
rx = [int(r) for _, _, r in ap]
tx = [int(t) for _, t, _ in ap]
thr = [r * PAYLOAD_BITS / (args.simTime * 1e6) for r in rx]
print("| Metric | " + " | ".join("AP%s" % a for a, _, _ in ap) + " | Global |")
print("|---|" + "---|" * (len(ap) + 1))
print("| CW (BEB, fixed min) | " + " | ".join("16" for _ in ap) + " | |")
print("| Throughput Mbps | " + " | ".join("%.3f" % t for t in thr) + " | %.3f |" % sum(thr))
print("| Loss ratio (phy) | " + " | ".join("%.3f" % (1 - r / max(t, 1)) for r, t in zip(rx, tx))
      + " | %.3f |" % (1 - sum(rx) / max(sum(tx), 1)))
print("| Fairness (Jain) | | | %.3f |" % jain(thr))
