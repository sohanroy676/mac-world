"""v4.1.0 Wave 4s: Gate C smoke. kwdirect alpha 1 with --cwGateC, 20 s, seed 0 on S2/S4, then a probe of the trace (2^k-1 values, changes only every 10 steps)."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []
for cell in ("s2", "s4"):
    tag = "w4s-%s-kwdirect-gatec" % cell
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "20", "--mode", "kwdirect"] + WIDE + [
        "--floors", FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", "1", "--lyTau", "0.6", "--cwGateC", "--seed", "0", "--tag", tag]
    jobs.append({"id": tag, "w": 22.0, "timeout": 3000, "cmds": [{"name": "run", "args": args}, {"name": "probe", "args": ["gatec_probe_v4_1_0.py", "{LAST}"]}]})
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs")
