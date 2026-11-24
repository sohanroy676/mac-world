"""v4.1.0 Wave 2b: BEB references at 60 s (seeds 0-3, 6 cells) and the floor-guarded controllers on S2/S4/S5a.
Usage: w2b_batch.py <out batch.json>. Floors = BEB means of seeds 200-209 (60 s, seconds 30-60), the same as the ceilings analysis."""
import itertools
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.0"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []


def add(name, cell, mode, extra, sim=60):
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", str(sim), "--mode", mode] + extra + ["--tag", "w2b-" + name]
    jobs.append({"id": "w2b-" + name, "w": round(1.1 * sim, 1), "timeout": int(70 * 1.1 * sim + 300), "cmds": [{"name": "run", "args": args}]})


for cell in cells:
    if cell.startswith("t"):
        continue
    for seed in range(4):
        add("%s-beb-s%d" % (cell, seed), cell, "beb", ["--seed", str(seed)])
for seed in range(4):
    for cell in ("s2", "s4", "s5a"):
        fl = ["--floors", FLOORS[cell]]
        for delta in (0.35, 0.7):
            for mode in ("cascade", "kwdirect"):
                add("%s-%s-d%g-s%d" % (cell, mode, delta, seed), cell, mode, WIDE + fl + ["--lyEta", "0.25", "--lyDelta", str(delta), "--seed", str(seed)])
            if cell != "s2":
                for beta in (0.5, 1.5):
                    add("%s-coord-d%g-b%g-s%d" % (cell, delta, beta, seed), cell, "coord", WIDE + fl + ["--lyEta", "0.25", "--lyDelta", str(delta), "--lyBeta", str(beta), "--seed", str(seed)])
add("s4-qcsma-d0.35-b0.5-s0", "s4", "qcsma", WIDE + ["--floors", FLOORS["s4"], "--lyEta", "0.25", "--lyDelta", "0.35", "--lyBeta", "0.5", "--seed", "0"])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
