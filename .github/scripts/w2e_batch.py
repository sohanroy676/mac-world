"""v4.1.0 Wave 2e: probe window 0.6 s for kwdirect at alpha 1 and 4 (delta 0.2, 0.35), 1.0 s at alpha 0, and coord with a 0.6 s window on S4 alpha 1."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.0"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []


def add(name, cell, mode, extra):
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + WIDE + ["--floors", FLOORS[cell]] + extra + ["--tag", "w2e-" + name]
    jobs.append({"id": "w2e-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(4):
    for cell in ("s2", "s4", "s5a"):
        for alpha in (1, 4):
            for delta in (0.2, 0.35):
                add("%s-kwdirect-a%d-tau0.6-d%g-s%d" % (cell, alpha, delta, seed), cell, "kwdirect", ["--lyEta", "0.25", "--lyDelta", str(delta), "--lyAlpha", str(alpha), "--lyTau", "0.6", "--seed", str(seed)])
        add("%s-kwdirect-a0-tau1.0-d0.2-s%d" % (cell, seed), cell, "kwdirect", ["--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", "0", "--lyTau", "1.0", "--seed", str(seed)])
    for delta in (0.35, 0.5):
        add("s4-coord-a1-tau0.6-d%g-s%d" % (delta, seed), "s4", "coord", ["--lyEta", "0.25", "--lyDelta", str(delta), "--lyBeta", "1.5", "--lyTau", "0.6", "--seed", str(seed)])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
