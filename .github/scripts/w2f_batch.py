"""v4.1.0 Wave 2f: S8 (time-varying load shift at 30 s), alpha 1 and 0. BEB, static anchor, kwdirect and coord with and without the change detector."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = "24.44,1.31,24.44"
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []


def add(name, mode, extra):
    args = cells["s8"]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + extra + ["--tag", "w2f-" + name]
    jobs.append({"id": "w2f-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(4):
    add("s8-beb-s%d" % seed, "beb", ["--seed", str(seed)])
    add("s8-static64-s%d" % seed, "static", ["--apCws", "64,64,64", "--seed", str(seed)])
    for alpha in (0, 1):
        tau = "1.0" if alpha == 0 else "0.6"
        for det in (0, 1):
            ex = WIDE + ["--floors", FLOORS, "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", str(alpha), "--lyTau", tau, "--seed", str(seed)] + (["--lyDetect"] if det else [])
            add("s8-kwdirect-a%d-det%d-s%d" % (alpha, det, seed), "kwdirect", ex)
    for det in (0, 1):
        ex = WIDE + ["--floors", FLOORS, "--lyEta", "0.25", "--lyDelta", "0.5", "--lyBeta", "1.5", "--lyTau", "0.6", "--lyAlpha", "1", "--seed", str(seed)] + (["--lyDetect"] if det else [])
        add("s8-coord-a1-det%d-s%d" % (det, seed), "coord", ex)
mkdir = os.makedirs("../waves/w2", exist_ok=True)
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
