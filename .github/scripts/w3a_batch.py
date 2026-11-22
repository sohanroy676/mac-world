"""v4.1.0 Wave 3a: tournament runs on seeds 300-309 (60 s) for everything except the frozen learners (Wave 2l): BEB, static F1/F2 points validated
on seeds 200-209 (ceilings-v4.1.0.md), DAC, BLADE, IdleSense, original KW, contextual UCB, kwdirect at its per-alpha setting (Wave 2e/2d) and
coord on S4 alpha 1. The rivals do not take alpha (their knobs were tuned once on seeds 0-3, Wave 2g); they are scored at all three alphas.
F3 (schedule) is not rerun: its period arguments are not in this batch; it stays a reference from seeds 200-209."""
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.0"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
STATIC_W = ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
F1 = {("s2", 0): "289,525", ("s2", 1): "512,512", ("s2", 4): "512,512", ("s4", 0): "54,84,95", ("s4", 1): "128,64,128", ("s4", 4): "254,104,200",
      ("s5a", 0): "110,161,94", ("s5a", 1): "128,128,128", ("s5a", 4): "227,133,279"}
F2 = {("s2", 0): "255,511", ("s2", 1): "255,255", ("s2", 4): "255,255", ("s4", 0): "63,63,63", ("s4", 1): "127,15,63", ("s4", 4): "127,7,63"}
RIVALS = {"dac514": ("dac", ["--dacTc", "514e-6"]), "blade": ("blade", []), "idlesense": ("idlesense", []),
          "kw": ("kw", ["--kwDelta", "0.2", "--kwEta", "0.1"]), "ucbctx": ("ucbctx", ["--ucbC", "1.0"])}
jobs = []


def add(name, cell, mode, extra, seed):
    tag = "w3a-%s-%s-s%d" % (cell, name, seed)
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + extra + ["--seed", str(seed), "--tag", tag]
    jobs.append({"id": tag, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})


for seed in range(300, 310):
    for cell in ("s2", "s4", "s5a"):
        add("beb", cell, "beb", [], seed)
        for name, (mode, ex) in RIVALS.items():
            add(name, cell, mode, ex, seed)
        for al in (0, 1, 4):
            add("f1-a%d" % al, cell, "static", ["--apCws", F1[(cell, al)]] + STATIC_W, seed)
            if (cell, al) in F2:
                add("f2-a%d" % al, cell, "static", ["--apCws", F2[(cell, al)], "--cwMinOnly", "--cwLo", "3"], seed)
            tau = "1.0" if (al == 0 and cell != "s5a") else "0.6"
            add("kwdirect-a%d" % al, cell, "kwdirect", WIDE + ["--floors", FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", str(al), "--lyTau", tau], seed)
    add("coord-a1", "s4", "coord", WIDE + ["--floors", FLOORS["s4"], "--lyEta", "0.25", "--lyDelta", "0.5", "--lyBeta", "1.5", "--lyTau", "0.6", "--lyAlpha", "1"], seed)
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
