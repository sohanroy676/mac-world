"""v4.1.0 Wave 2c: finer grid for kwdirect and coord (alpha 1), and the best settings at alpha 0 and 4, on S2/S4/S5a, seeds 0-3, 60 s.
Usage: w2c_batch.py <out batch.json>."""
import itertools
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.0"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []


def add(name, cell, mode, extra):
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + WIDE + ["--floors", FLOORS[cell]] + extra + ["--tag", "w2c-" + name]
    jobs.append({"id": "w2c-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(4):
    for cell in ("s2", "s4", "s5a"):
        for eta, delta in itertools.product((0.15, 0.25, 0.4), (0.2, 0.35, 0.5)):
            base = ["--lyEta", str(eta), "--lyDelta", str(delta), "--seed", str(seed)]
            add("%s-kwdirect-e%g-d%g-s%d" % (cell, eta, delta, seed), cell, "kwdirect", base)
            if cell != "s2":
                add("%s-coord-e%g-d%g-s%d" % (cell, eta, delta, seed), cell, "coord", base + ["--lyBeta", "1.5"])
        for alpha in (0, 4):                 # the Wave 2b best settings at the other alphas
            base = ["--lyEta", "0.25", "--lyDelta", "0.35", "--lyAlpha", str(alpha), "--seed", str(seed)]
            add("%s-kwdirect-a%d-s%d" % (cell, alpha, seed), cell, "kwdirect", base)
            if cell != "s2":
                add("%s-coord-a%d-s%d" % (cell, alpha, seed), cell, "coord", base + ["--lyBeta", "1.5"])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
