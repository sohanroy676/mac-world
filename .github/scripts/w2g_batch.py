"""v4.1.0 Wave 2g: rival sanity (BLADE, IdleSense, original KW, contextual UCB, DAC at its tuned Tc) on S2, S4, S5a, 60 s, seeds 0-3,
and the S8 detector retune (larger Page-Hinkley threshold) for coord and kwdirect at alpha 1."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = "24.44,1.31,24.44"
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
RIVALS = {"blade": [], "idlesense": [], "kw": ["--kwDelta", "0.2", "--kwEta", "0.1"], "ucbctx": ["--ucbC", "1.0", "--extraTraces"], "dac": ["--dacTc", "514e-6"]}
jobs = []


def add(name, cell, mode, extra):
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + extra + ["--tag", "w2g-" + name]
    jobs.append({"id": "w2g-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(4):
    for cell in ("s2", "s4", "s5a"):
        for mode, ex in RIVALS.items():
            add("%s-%s-s%d" % (cell, mode, seed), cell, mode, ex + ["--seed", str(seed)])
    for lam in (10, 30):
        for det_delta in (0.05, 0.2):
            tail = ["--lyDetect", "--lyDetectLam", str(lam), "--lyDetectDelta", str(det_delta), "--seed", str(seed)]
            add("s8-coord-a1-lam%d-dd%g-s%d" % (lam, det_delta, seed), "s8", "coord",
                WIDE + ["--floors", FLOORS, "--lyEta", "0.25", "--lyDelta", "0.5", "--lyBeta", "1.5", "--lyTau", "0.6", "--lyAlpha", "1"] + tail)
            add("s8-kwdirect-a1-lam%d-dd%g-s%d" % (lam, det_delta, seed), "s8", "kwdirect",
                WIDE + ["--floors", FLOORS, "--lyEta", "0.25", "--lyDelta", "0.2", "--lyTau", "0.6", "--lyAlpha", "1"] + tail)
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
