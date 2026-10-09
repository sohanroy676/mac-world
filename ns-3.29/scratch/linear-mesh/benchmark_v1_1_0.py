"""v1.1.0: run the benchmark matrix (topology x mode x seed), strictly one ns-3 job at a time.
Usage (from this directory):
  ../../venv/bin/python benchmark_v1_1_0.py --topos 2,3 5,15 --modes beb global independent --seeds 0 1 2
Resume an interrupted batch with --benchDir results/bench-<ts>: entries already PASS in manifest.csv are skipped.
Each job is OSCAR_multi_ap_train.py --mode M --seed S --check; the log goes to <benchDir>/<topo>-<mode>-s<seed>.log.
Seed S is the python seed; the ns-3 seed is S + 1 (same for every mode, so runs are paired by seed).
"""
import argparse
import csv
import os
import re
import shlex
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("--topos", nargs="+", required=True, help="apStaCounts values, e.g. 2,3 5,15")
parser.add_argument("--modes", nargs="+", default=["beb", "global", "independent"])
parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
parser.add_argument("--simTime", type=float, default=15)
parser.add_argument("--stepTime", type=float, default=0.01)
parser.add_argument("--benchDir", default="results/bench-%s" % time.strftime("%Y%m%d-%H%M%S"))
parser.add_argument("--no-check", action="store_true")
parser.add_argument("--trainerArgs", default="", help="extra trainer args, e.g. '--historyLength 20 --start_timesteps 10'")
args = parser.parse_args()

FIELDS = ["topo", "mode", "seed", "run_dir", "result", "returncode", "seconds"]
manifest = os.path.join(args.benchDir, "manifest.csv")
os.makedirs(args.benchDir, exist_ok=True)
done = set()
if os.path.exists(manifest):
    for r in csv.DictReader(open(manifest)):
        if r["result"] == "PASS":
            done.add((r["topo"], r["mode"], int(r["seed"])))
else:
    with open(manifest, "w", newline="") as f:
        csv.DictWriter(f, FIELDS).writeheader()

jobs = [(t, m, s) for t in args.topos for s in args.seeds for m in args.modes if (t, m, s) not in done]
print("bench dir: %s | %d jobs to run, %d already PASS" % (args.benchDir, len(jobs), len(done)), flush=True)
for n, (topo, mode, seed) in enumerate(jobs, 1):
    if subprocess.run(["pgrep", "-x", "linear-mesh"], capture_output=True).stdout.strip():
        sys.exit("an ns-3 linear-mesh process is already running; refusing to start another")
    log = os.path.join(args.benchDir, "%s-%s-s%d.log" % (topo, mode, seed))
    cmd = [sys.executable, "OSCAR_multi_ap_train.py", "--apStaCounts", topo, "--mode", mode, "--seed", str(seed),
           "--simTime", str(args.simTime), "--stepTime", str(args.stepTime)]
    cmd += shlex.split(args.trainerArgs)
    if not args.no_check:
        cmd.append("--check")
    print("[%d/%d] %s mode=%s seed=%d ..." % (n, len(jobs), topo, mode, seed), flush=True)
    t0 = time.time()
    with open(log, "w") as lf:
        rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT).returncode
    text = open(log).read()
    m = re.search(r"out: (results/multi-ap-\S+)", text)
    passed = rc == 0 and "CHECK FAIL" not in text and (args.no_check or "RESULT: PASS" in text)
    row = dict(topo=topo, mode=mode, seed=seed, run_dir=m.group(1) if m else "", result="PASS" if passed else "FAIL",
               returncode=rc, seconds=int(time.time() - t0))
    with open(manifest, "a", newline="") as f:
        csv.DictWriter(f, FIELDS).writerow(row)
    print("   -> %s (rc=%d, %d s) %s" % (row["result"], rc, row["seconds"], row["run_dir"]), flush=True)
    if not passed:
        sys.exit("job failed; see %s" % log)
print("batch complete")
