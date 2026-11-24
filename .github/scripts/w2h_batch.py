"""v4.1.0 Wave 2h: S4 alpha 0 recheck on validation seeds 200-209: BEB, DAC (Tc 514 us), kwdirect alpha 0 (tau 1.0, delta 0.2)."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = "24.44,1.31,24.44"
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []


def add(name, mode, extra):
    args = cells["s4"]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + extra + ["--tag", "w2h-" + name]
    jobs.append({"id": "w2h-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(200, 210):
    add("s4-beb-s%d" % seed, "beb", ["--seed", str(seed)])
    add("s4-dac514-s%d" % seed, "dac", ["--dacTc", "514e-6", "--seed", str(seed)])
    add("s4-kwdirect-a0-s%d" % seed, "kwdirect", WIDE + ["--floors", FLOORS, "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", "0", "--lyTau", "1.0", "--seed", str(seed)])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
