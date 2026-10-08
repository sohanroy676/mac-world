"""v0.6.0 joint-step check: deterministic per-AP actions must reach the right AP.
Run from this directory: ../../venv/bin/python test_multi_ap_gym.py [--staCounts 2,3]
"""
import argparse
import sys

import numpy as np

from multi_ap import parse_ap_info, reshape_obs
from wrappers import EnvWrapper

parser = argparse.ArgumentParser()
parser.add_argument("--staCounts", default="2,3")
parser.add_argument("--steps", type=int, default=10)
parser.add_argument("--phases", default="2,5;5,2", help="';'-separated action pairs (exponent domain, CW=2^(a+4))")
CLI = parser.parse_args()

counts = [int(c) for c in CLI.staCounts.split(",")]
n = len(counts)
H = 20
sim_args = {"simTime": 3, "envStepTime": 0.1, "historyLength": H, "agentType": "continuous",
            "scenario": "basic", "apStaCounts": CLI.staCounts}
env = EnvWrapper(1, **sim_args)
obs = env.reset()
assert reshape_obs(obs[0], n).shape == (n, H), np.shape(obs)

fails = 0
print("phase step  action      | AP  cwSet cwAp  reward   loss    rx   tx")
for pi, phase in enumerate(CLI.phases.split(";")):
    action = [float(a) for a in phase.split(",")]
    assert len(action) == n
    want = [int(min(1024, max(16, 2 ** (a + 4)))) for a in action]
    for step in range(CLI.steps):
        o, r, d, info = env.step(np.array([action], dtype=np.float32))
        o2 = reshape_obs(o[0], n)
        recs = parse_ap_info(info[0], n)
        ok = o2.shape == (n, H) and np.isfinite(o2).all()
        for i, rec in enumerate(recs):
            ok &= rec["cw_set"] == want[i] and rec["cw_ap"] == want[i] and 0.0 <= rec["reward"] <= 1.0
        fails += not ok
        if step in (0, CLI.steps - 1) or not ok:
            for i, rec in enumerate(recs):
                print("%5d %4d  %-11s | AP%d %5d %5d %7.4f %7.4f %5d %5d %s" % (
                    pi, step, action, i + 1, rec["cw_set"], rec["cw_ap"], rec["reward"], rec["loss"],
                    rec["rx"], rec["tx"], "" if ok else "<-- FAIL"))
        if d[0]:
            break
env.close()
print("RESULT:", "FAIL (%d bad steps)" % fails if fails else "PASS")
sys.exit(1 if fails else 0)
