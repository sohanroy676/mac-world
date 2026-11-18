"""v4.1.0 Wave 2 tuning batch: cascade (L1+L2) on S2 and S4, coord (L1+L2+L3) on S4, grid over L2 step eta and probe delta.
Usage: w2_tune.py <out batch.json>; then make_packs.py. 60 s runs, seeds 0-3 (search seeds), scored on seconds 30-60 by the analysis."""
import itertools
import json
import os
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
WIDE = ["--cwHold", "--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
jobs = []
for mode, cell in (("cascade", "s2"), ("cascade", "s4"), ("coord", "s4")):
    for eta, delta in itertools.product((0.1, 0.25, 0.5), (0.2, 0.35, 0.7)):
        for seed in range(4):
            name = "%s-%s-e%g-d%g-s%d" % (mode, cell, eta, delta, seed)
            args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", "60", "--mode", mode] + WIDE + \
                ["--lyEta", str(eta), "--lyDelta", str(delta), "--seed", str(seed), "--tag", "w2-" + name]
            jobs.append({"id": "w2-" + name, "w": 66.0, "timeout": int(70 * 66 + 300), "cmds": [{"name": "run", "args": args}]})
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
