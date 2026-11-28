"""v4.2.0 graded-interference wave 4 (held-out seeds 103-122, 60 s, second-half throughput). Oracle points from wave 3 (graded-interference-oracle-points-v4.2.0.json).
File A (non-learned): beb, idlesense, dac514, exact static at the alpha-0 and alpha-1 oracle, kwdirect alpha 0 and 1 (settings of apdir_u2_batch.py, floors = wave-3 floors).
File B (learned): per cell, RAFA (shared, lambda 1, 6 episodes) and Global (12 episodes), train seeds 2000-2002, each job = train + 5 frozen evals on seeds 103-107.
Usage: graded_w4_batch.py OUT_A.json OUT_B.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graded_w3_batch as w3  # noqa: E402
import apdir_u2_batch as u2  # noqa: E402

ORACLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "results", "graded-interference-oracle-points-v4.2.0.json")))
FLOORS = {"g85": "12.42,7.05,12.42", "g100": "12.50,10.20,12.50", "ow100": "9.50,11.60,11.80"}
SEEDS = range(103, 123)
SIM = 60


def build_a():
    jobs = []
    for cell in w3.CELLS:
        for seed in SEEDS:
            jobs.append(w3.job("g4", cell, "beb", ["--mode", "beb"], seed, SIM))
            jobs.append(w3.job("g4", cell, "idlesense", ["--mode", "idlesense"], seed, SIM))
            jobs.append(w3.job("g4", cell, "dac514", ["--mode", "dac", "--dacTc", "514e-6"], seed, SIM))
            for al in ("0", "1"):
                jobs.append(w3.job("g4", cell, "f1-a" + al, ["--mode", "static", "--apCws", ORACLE[cell][al].replace("-", ",")] + w3.STATIC_W, seed, SIM))
                jobs.append(w3.job("g4", cell, "kwdirect-a" + al, ["--mode", "kwdirect"] + u2.WIDE + ["--floors", FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2",
                                                                                                     "--lyAlpha", al, "--lyTau", "0.6"], seed, SIM))
    assert len({j["id"] for j in jobs}) == len(jobs)
    return {"lanes": 4, "packs": 20, "jobs": jobs}


def build_b():
    jobs = []
    for cell, hid in w3.CELLS.items():
        base = ["--apStaCounts", "10,10,10", "--apHidden", hid, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01", "--check"]
        for t in range(3):
            rafa = ["--mode", "shared", "--obs", "rafa", "--reward", "fair", "--alphaInput"]
            cmds = [{"name": "train", "args": base + rafa + ["--simTime", "15", "--episodes", "6", "--varySeeds", "--seed", str(2000 + t), "--floorLambda", "1",
                                                              "--floors", FLOORS[cell], "--saveActor", "{ACT}", "--tag", "g4-%s-rafa-t%d-train" % (cell, t)]}]
            cmds += [{"name": "eval-%d" % s, "args": base + rafa + ["--simTime", str(SIM), "--eval", "--loadActor", "{ACT}", "--fairAlpha", "1", "--seed", str(s),
                                                                    "--tag", "g4-%s-rafa-t%d" % (cell, t)]} for s in range(103, 108)]
            jobs.append({"id": "g4-%s-rafa-t%d" % (cell, t), "on": "actions", "w": 120, "timeout": 20000, "cmds": cmds})
            cmds = [{"name": "train", "args": base + ["--simTime", "15", "--mode", "global", "--episodes", "12", "--varySeeds", "--seed", str(2000 + t), "--saveActor", "{ACT}",
                                                      "--tag", "g4-%s-global-t%d-train" % (cell, t)]}]
            cmds += [{"name": "eval-%d" % s, "args": base + ["--simTime", str(SIM), "--mode", "global", "--eval", "--loadActor", "{ACT}", "--seed", str(s),
                                                             "--tag", "g4-%s-global-t%d" % (cell, t)]} for s in range(103, 108)]
            jobs.append({"id": "g4-%s-global-t%d" % (cell, t), "on": "actions", "w": 150, "timeout": 20000, "cmds": cmds})
    return {"lanes": 4, "packs": 20, "jobs": jobs}


if __name__ == "__main__":
    for path, b in ((sys.argv[1], build_a()), (sys.argv[2], build_b())):
        json.dump(b, open(path, "w"))
        print(path, len(b["jobs"]), "jobs")
