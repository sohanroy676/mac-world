"""v4.1.0 Wave 2i: S7 delay cells (s7a, s7b), 60 s, seeds 0-3: BEB, static anchor, kwdirect with the delay objective (tau 0.6 and 1.0)."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s7a": "7.33,14.65", "s7b": "19.1,9.9,19.1"}  # 0.99 x offered load per AP (Mbps)
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacCw0", "64"]
jobs = []


def add(name, cell, mode, extra):
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + extra + ["--tag", "w2i-" + name]
    jobs.append({"id": "w2i-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(4):
    for cell in ("s7a", "s7b"):
        add("%s-beb-s%d" % (cell, seed), cell, "beb", ["--seed", str(seed)])
        add("%s-static-s%d" % (cell, seed), cell, "static", ["--apCws", ",".join(map(str, cells[cell]["anchors"][0])), "--seed", str(seed)])
        for tau in ("0.6", "1.0"):
            add("%s-kwdelay-tau%s-s%d" % (cell, tau, seed), cell, "kwdirect",
                WIDE + ["--extraTraces", "--delayWindow", "0.3", "--floors", FLOORS[cell], "--lyObjective", "delay", "--lyEta", "0.25", "--lyDelta", "0.2", "--lyTau", tau, "--seed", str(seed)])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
