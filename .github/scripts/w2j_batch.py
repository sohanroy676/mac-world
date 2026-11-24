"""v4.1.0 Wave 2j: class B learner pilot. 1 training seed (2000) x cells s2, s4, s5a x learners RAFA (per-scenario), Global, PF.
Training as in M3/M2c (RAFA: 6 episodes of 15 s, lambda 1; Global/PF: 12 episodes of 15 s), then one 60 s eval, seed 0, alpha 1."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.30,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.00"}
LEARN = {
    "rafa": (6, ["--mode", "shared", "--obs", "rafa", "--reward", "fair", "--alphaInput"], ["--fairAlpha", "1"]),
    "global": (12, ["--mode", "global"], []),
    "pf": (12, ["--mode", "independent", "--reward", "pf"], []),
}
jobs = []
for cell in ("s2", "s4", "s5a"):
    for name, (eps, margs, eargs) in LEARN.items():
        fl = ["--floors", FLOORS[cell], "--floorLambda", "1"] if name == "rafa" else []  # training only: eval rejects --floorLambda without --floors
        base = cells[cell]["args"] + ["--stepTime", "0.01", "--check"] + margs
        train = base + ["--simTime", "15", "--episodes", str(eps), "--varySeeds", "--seed", "2000"] + fl + ["--saveActor", "{ACT}", "--tag", "w2j-%s-%s-train" % (cell, name)]
        ev = base + ["--simTime", "60", "--eval", "--loadActor", "{ACT}"] + eargs + ["--seed", "0", "--tag", "w2j-%s-%s" % (cell, name)]
        sim = 15 * eps + 60
        jobs.append({"id": "w2j-%s-%s" % (cell, name), "w": 1.1 * sim, "timeout": int(70 * 1.1 * sim * 2 + 600),
                     "cmds": [{"name": "train", "args": train}, {"name": "eval", "args": ev}]})
ONLY = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")]
if ONLY:  # e.g. --only=rafa: keep these learners (rerun of failed jobs)
    jobs = [j for j in jobs if any(j["id"].endswith("-" + o) for o in ONLY)]
    for j in jobs:
        j["id"] = j["id"].replace("w2j-", "w2j2-")
json.dump({"jobs": jobs}, open([a for a in sys.argv[1:] if not a.startswith("--")][0], "w"))
print(len(jobs), "jobs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
