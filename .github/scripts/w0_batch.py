"""v4.1.0 Wave 0 (rehearsal): write the packs file. Usage: w0_batch.py <shards> <out packs.json> [--test]

Every shard gets the SAME 11 runs (job ids end in -s<shard>), so the collector can compare the trace SHA-256 of one run
across all accounts (Gate 0: complete and hash-identical results from at least 4 accounts). The runs cover every job
type of the later waves: BEB, exact static (F1), static CWmin (F2), schedule (F3), DAC, KW, the S8 load schedule, a
60 s run and one small learner run. --test cuts every run to 5 simulated seconds for a local argument check.
"""
import json
import os
import sys

n_shards, out = int(sys.argv[1]), sys.argv[2]
test = "--test" in sys.argv
cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
WIDE = ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
RUNS = [  # (name, cell, simulated seconds, pack, extra args)
    ("s2-beb", "s2", 30, 0, ["--mode", "beb"]),
    ("s4-beb", "s4", 30, 0, ["--mode", "beb"]),
    ("s2-f1-512", "s2", 30, 0, ["--mode", "static", "--apCws", "512,512"] + WIDE),
    ("s4-f1-75", "s4", 30, 0, ["--mode", "static", "--apCws", "75,75,75"] + WIDE),
    ("s4-f2-31-63-31", "s4", 30, 1, ["--mode", "static", "--apCws", "31,63,31", "--cwMinOnly", "--cwLo", "3"]),
    ("s4-f3-16", "s4", 30, 1, ["--mode", "static", "--apCws", "16,16,16", "--schedA", "1,3", "--schedPeriodSteps", "20", "--schedASteps", "10",
                                "--schedMuteCw", "1023"] + WIDE),
    ("s4-dac", "s4", 30, 1, ["--mode", "dac", "--dacTc", "514e-6"]),
    ("s2-kw", "s2", 30, 1, ["--mode", "kw", "--kwDelta", "0.7", "--kwEta", "0.03"]),
    ("s8p3-beb", "s8p3", 15, 2, ["--mode", "beb"]),
    ("t23-learn", "t23", 5, 2, ["--mode", "independent", "--start_timesteps", "50"]),
    ("s4-f1-64-60s", "s4", 60, 2, ["--mode", "static", "--apCws", "64,64,64"] + WIDE),
]
shards = []
for k in range(n_shards):
    packs = [[], [], []]
    for name, cell, sim, pack, extra in RUNS:
        sim = 5 if test else sim
        w = round(1.1 * sim, 1)
        args = cells[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", str(sim)] + extra + ["--seed", "0", "--tag", "w0-" + name]
        job = {"id": "w0-%s-s%d" % (name, k), "w": w, "timeout": int(70 * w + 300), "cmds": [{"name": "run", "args": args}]}
        if name == "t23-learn":
            job["pin"] = True  # one thread, no CPU-specific kernels: the learner's floats should then match across CPU models
        packs[pack].append(job)
    shards.append([{"id": "p%d" % i, "jobs": p} for i, p in enumerate(packs)])
json.dump({"lanes": 4, "shards": shards}, open(out, "w"), indent=1)
w_all = sum(j["w"] for s in shards for p in s for j in p["jobs"])
print("%d shards x %d runs, %.1f lab-h" % (n_shards, len(RUNS), w_all / 33.0 * 0.2))
