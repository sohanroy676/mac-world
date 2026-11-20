"""v4.1.0 Wave 2k: class B learner stage 1. 12 training seeds (2000-2011) x cells s2/s4/s5a x learners RAFA, Global, PF.
Same recipes as Wave 2j (RAFA 6 episodes lambda 1; Global/PF 12 episodes, 15 s each). Each job trains one seed and evaluates it on
3 selection seeds (0, 1, 2) for 60 s at alpha 1; the actor is kept in the pack bundle for the later tournament evals (seeds 300-309,
alphas 0/1/4 for RAFA via --fairAlpha). Selection seeds are not tournament seeds."""
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
        for ts in range(2000, 2012):
            fl = ["--floors", FLOORS[cell], "--floorLambda", "1"] if name == "rafa" else []
            base = cells[cell]["args"] + ["--stepTime", "0.01", "--check"] + margs
            tag = "w2k-%s-%s-t%d" % (cell, name, ts)
            train = base + ["--simTime", "15", "--episodes", str(eps), "--varySeeds", "--seed", str(ts)] + fl + ["--saveActor", "{ACT}", "--tag", tag + "-train"]
            cmds = [{"name": "train", "args": train}]
            for es in (0, 1, 2):
                cmds.append({"name": "eval%d" % es, "args": base + ["--simTime", "60", "--eval", "--loadActor", "{ACT}"] + eargs + ["--seed", str(es), "--tag", tag]})
            sim = 15 * eps + 180
            jobs.append({"id": tag, "w": 1.1 * sim, "timeout": int(70 * 1.1 * sim * 2 + 600), "cmds": cmds})
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "jobs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
