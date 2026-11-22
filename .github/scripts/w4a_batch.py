"""v4.1.0 Wave 4a: confirmation on fresh seeds 103-122, 300 s. BEB, DAC514, static F1, kwdirect (per-alpha setting), kwdirect under Gate C
(--cwGateC: 100 ms updates, 2^k-1), coord on S4 alpha 1, and the best frozen learner per cell (actors fetched from branch wave-actors).
Scored on the second half of the run (thr_half2); thr_all is also kept."""
import json
import os
import subprocess
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
FLOORS = {"s2": "9.3,17.19", "s4": "24.44,1.31,24.44", "s5a": "15.03,11.25,10.0"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
STATIC_W = ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
F1 = {("s2", 0): "289,525", ("s2", 1): "512,512", ("s2", 4): "512,512", ("s4", 0): "54,84,95", ("s4", 1): "128,64,128", ("s4", 4): "254,104,200",
      ("s5a", 0): "110,161,94", ("s5a", 1): "128,128,128", ("s5a", 4): "227,133,279"}
MARGS = {"rafa": ["--mode", "shared", "--obs", "rafa", "--reward", "fair", "--alphaInput", "--fairAlpha", "1"], "global": ["--mode", "global"],
         "pf": ["--mode", "independent", "--reward", "pf"]}
LEARN = [("s2", "global", 2003), ("s4", "pf", 2003), ("s4", "rafa", 2001), ("s5a", "pf", 2007)]
SIM = 300
SEEDS = range(103, 123)
tree = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "origin/wave-actors"], text=True).split()
jobs = []


def job(tag, cmds):
    jobs.append({"id": tag, "w": 1.1 * SIM, "timeout": int(70 * 1.1 * SIM * 2 + 600), "cmds": cmds})


def add(name, cell, mode, extra, seed):
    tag = "w4a-%s-%s-s%d" % (cell, name, seed)
    args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", str(SIM), "--mode", mode] + extra + ["--seed", str(seed), "--tag", tag]
    job(tag, [{"name": "run", "args": args}])


for seed in SEEDS:
    for cell in ("s2", "s4", "s5a"):
        add("beb", cell, "beb", [], seed)
        add("dac514", cell, "dac", ["--dacTc", "514e-6"], seed)
        for al in (0, 1, 4):
            add("f1-a%d" % al, cell, "static", ["--apCws", F1[(cell, al)]] + STATIC_W, seed)
            tau = "1.0" if (al == 0 and cell != "s5a") else "0.6"
            kw = WIDE + ["--floors", FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", str(al), "--lyTau", tau]
            add("kwdirect-a%d" % al, cell, "kwdirect", kw, seed)
            add("kwdirect-gatec-a%d" % al, cell, "kwdirect", kw + ["--cwGateC"], seed)
    add("coord-a1", "s4", "coord", WIDE + ["--floors", FLOORS["s4"], "--lyEta", "0.25", "--lyDelta", "0.5", "--lyBeta", "1.5", "--lyTau", "0.6", "--lyAlpha", "1"], seed)
for cell, lr, ts in LEARN:
    name = "w2k-%s-%s-t%d" % (cell, lr, ts)
    src = [f.rsplit("/actors/", 1)[0] for f in tree if f.endswith("/" + name + "/actors/agent0_actor")]
    assert len(src) == 1, (name, src)
    files = sorted(f.split("/actors/", 1)[1] for f in tree if f.startswith(src[0] + "/actors/"))
    for seed in SEEDS:
        tag = "w4a-%s-L-%s-t%d-s%d" % (cell, lr, ts, seed)
        job(tag, [{"name": "fetch", "fetch": {"src": src[0] + "/actors", "files": files}},
                  {"name": "eval", "args": cells[cell]["args"] + ["--stepTime", "0.01", "--check"] + MARGS[lr] + [
                      "--simTime", str(SIM), "--eval", "--loadActor", "{ACT}", "--seed", str(seed), "--tag", tag]}])
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
