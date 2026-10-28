"""v3.2.0: fair evaluation protocol, strictly one ns-3 job at a time.
Phase 1 (train): per learned mode, one policy trained for --trainEpisodes episodes with different ns-3 seeds
  (--varySeeds) at python seed --trainSeed, actors saved to <benchDir>/actors/<mode>.
Phase 2 (eval): each frozen policy (--loadActor --eval: no noise, no warm-up, no training) and BEB run on the same
  held-out python seeds --evalSeeds (ns-3 seed = seed + 1), so runs are paired by seed.
Usage (from this directory):
  ../../venv/bin/python fair_protocol_v3_2_0.py --topo 20,40 --modes independent global shared --learnerArgs "--alpha 0" --benchDir results/fair-v3.2.0
Resume with the same --benchDir: PASS rows are skipped. manifest.csv (eval + BEB rows) has the columns
aggregate_bench.py reads; eval runs carry --tag fz-<mode>[-td3]. Training rows go to train_manifest.csv.
Aggregate: ../../venv/bin/python aggregate_bench.py <benchDir> --out <dir> --topo <topo> --title v3.2.0
One trained policy per mode: policy-seed variance is not covered; repeat with another --trainSeed and --benchDir for that.
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
parser.add_argument("--topo", required=True, help="apStaCounts, e.g. 20,40")
parser.add_argument("--modes", nargs="+", default=["independent", "global", "shared"], choices=["independent", "global", "shared"])
parser.add_argument("--algo", choices=["ddpg", "td3"], default="ddpg")
parser.add_argument("--trainSeed", type=int, default=0)
parser.add_argument("--trainEpisodes", type=int, default=3)
parser.add_argument("--evalSeeds", nargs="+", type=int, default=list(range(100, 108)))
parser.add_argument("--simTime", type=float, default=15)
parser.add_argument("--stepTime", type=float, default=0.01)
parser.add_argument("--benchDir", default="results/fair-%s" % time.strftime("%Y%m%d-%H%M%S"))
parser.add_argument("--trainerArgs", default="", help="extra trainer args for EVERY job incl. BEB, e.g. '--historyLength 20 --obsWindow 20'")
parser.add_argument("--learnerArgs", default="", help="extra trainer args for learned modes only (train and eval, not BEB), e.g. '--alpha 0 --rewardScale 100 --cwMinOnly'")
parser.add_argument("--variant", default="", help="v3.4.0: label appended to run tags, log names and the actor dir (e.g. '-pf'), so variants of one mode can share an aggregate")
parser.add_argument("--no-beb", action="store_true")
parser.add_argument("--no-check", action="store_true")
args = parser.parse_args()

FIELDS = ["topo", "mode", "seed", "run_dir", "result", "returncode", "seconds"]
os.makedirs(args.benchDir, exist_ok=True)
suffix = ("-td3" if args.algo == "td3" else "") + args.variant


def load(path):
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            csv.DictWriter(f, FIELDS).writeheader()
        return set()
    return {(r["mode"], int(r["seed"])) for r in csv.DictReader(open(path)) if r["result"] == "PASS"}


def run(manifest, label, mode, seed, extra, learner=True):
    if subprocess.run(["pgrep", "-x", "linear-mesh"], capture_output=True).stdout.strip():
        sys.exit("an ns-3 linear-mesh process is already running; refusing to start another")
    log = os.path.join(args.benchDir, "%s-%s-s%d.log" % (args.topo, label, seed))
    cmd = [sys.executable, "OSCAR_multi_ap_train.py", "--apStaCounts", args.topo, "--mode", mode, "--seed", str(seed),
           "--simTime", str(args.simTime), "--stepTime", str(args.stepTime)] + shlex.split(args.trainerArgs) + (shlex.split(args.learnerArgs) if learner else []) + extra
    if not args.no_check:
        cmd.append("--check")
    print("%s seed=%d ..." % (label, seed), flush=True)
    t0 = time.time()
    with open(log, "w") as lf:
        rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT).returncode
    text = open(log).read()
    m = re.search(r"out: (results/multi-ap-\S+)", text)
    passed = rc == 0 and "CHECK FAIL" not in text and (args.no_check or "RESULT: PASS" in text)
    row = dict(topo=args.topo, mode=mode, seed=seed, run_dir=m.group(1) if m else "", result="PASS" if passed else "FAIL",
               returncode=rc, seconds=int(time.time() - t0))
    with open(manifest, "a", newline="") as f:
        csv.DictWriter(f, FIELDS).writerow(row)
    print("   -> %s (rc=%d, %d s) %s" % (row["result"], rc, row["seconds"], row["run_dir"]), flush=True)
    if not passed:
        sys.exit("job failed; see %s" % log)


train_manifest = os.path.join(args.benchDir, "train_manifest.csv")
eval_manifest = os.path.join(args.benchDir, "manifest.csv")
trained = load(train_manifest)
evaled = load(eval_manifest)
actor_dir = lambda mode: os.path.abspath(os.path.join(args.benchDir, "actors", mode + suffix))

for mode in args.modes:
    if (mode, args.trainSeed) not in trained:
        run(train_manifest, "train-" + mode + suffix, mode, args.trainSeed,
            ["--algo", args.algo, "--episodes", str(args.trainEpisodes), "--varySeeds", "--saveActor", actor_dir(mode)])
for seed in args.evalSeeds:
    if not args.no_beb and ("beb", seed) not in evaled:
        run(eval_manifest, "beb", "beb", seed, [], learner=False)
    for mode in args.modes:
        if (mode, seed) not in evaled:
            run(eval_manifest, "fz-" + mode + suffix, mode, seed,
                ["--algo", args.algo, "--loadActor", actor_dir(mode), "--eval", "--tag", "fz-" + mode + suffix])
print("batch complete")
