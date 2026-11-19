"""v4.1.0 Wave 2d: alpha-aware L3 weights (coord at alpha 0 and 4 on S4/S5a) and kwdirect with a 0.6 s probe window at alpha 0. Seeds 0-3, 60 s."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.0"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []


def add(name, cell, mode, extra):
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + WIDE + ["--floors", FLOORS[cell]] + extra + ["--tag", "w2d-" + name]
    jobs.append({"id": "w2d-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(4):
    for cell in ("s4", "s5a"):
        for alpha in (0, 4):
            for beta in (0.5, 1.5):
                add("%s-coord-a%d-b%g-s%d" % (cell, alpha, beta, seed), cell, "coord", ["--lyEta", "0.25", "--lyDelta", "0.35", "--lyAlpha", str(alpha), "--lyBeta", str(beta), "--seed", str(seed)])
    for cell in ("s2", "s4", "s5a"):
        for delta in (0.2, 0.35):
            add("%s-kwdirect-a0-tau0.6-d%g-s%d" % (cell, delta, seed), cell, "kwdirect", ["--lyEta", "0.25", "--lyDelta", str(delta), "--lyAlpha", "0", "--lyTau", "0.6", "--seed", str(seed)])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
