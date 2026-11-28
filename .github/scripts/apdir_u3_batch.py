"""v4.2.0 uplink/downlink wave U3: retune kwdirect for the downlink cells d3 and d4 (U2 showed it near BEB there). Grid over lyEta, lyDelta, lyTau at
alpha 0 and 1, seeds 0-2, 60 s, same floors as U2. Usage: apdir_u3_batch.py OUT.json"""
import itertools
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import apdir_u2_batch as u2  # noqa: E402  (reuses CELLS, FLOORS, WIDE; its module code only builds a job list)

jobs = []
for cell in ("d3", "d4"):
    counts, hidden, dirs = u2.CELLS[cell]
    for eta, delta, tau in itertools.product((0.1, 0.25, 0.5), (0.1, 0.2, 0.4), (0.3, 0.6, 1.0)):
        for al in (0, 1):
            for seed in (0, 1, 2):
                name = "kw-e%g-d%g-t%g-a%d" % (eta, delta, tau, al)
                tag = "u3-%s-%s" % (cell, name)
                args = ["--apStaCounts", counts, "--apHidden", hidden, "--apDir", dirs, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01",
                        "--check", "--extraTraces", "--simTime", "60", "--mode", "kwdirect"] + u2.WIDE + [
                        "--floors", u2.FLOORS[cell], "--lyEta", str(eta), "--lyDelta", str(delta), "--lyAlpha", str(al), "--lyTau", str(tau),
                        "--seed", str(seed), "--tag", tag]
                jobs.append({"id": "%s-s%d" % (tag, seed), "on": "actions", "w": 66.0, "timeout": int(70 * 66 * 2 + 600), "cmds": [{"name": "run", "args": args}]})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs")
