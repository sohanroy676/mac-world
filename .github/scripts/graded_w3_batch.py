"""v4.2.0 graded-interference wave 3 (selection seeds 0-2): BEB and an exact static grid (--cwHold, --cwLo 4) per graded cell, so the oracle is not clamped at 16
and covers the uniform CWs the wave-2 learners chose. Cells (10,10,10, 10 Mbps, 30 s): g85 = 1-3:85, g100 = 1-3:100, ow100 = 1>3:100.
Grid: (edge, middle, edge), edge in 16..512, middle in 4..256 (symmetric edges). Usage: graded_w3_batch.py OUT.json"""
import json
import sys

CELLS = {"g85": "1-3:85", "g100": "1-3:100", "ow100": "1>3:100"}
EDGES = (16, 32, 64, 128, 256, 512)
MIDS = (4, 8, 16, 32, 64, 128, 256)
SEEDS = (0, 1, 2)
STATIC_W = ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
SIM = 30


def job(prefix, cell, name, extra, seed, sim=SIM):
    tag = "%s-%s-%s" % (prefix, cell, name)
    args = ["--apStaCounts", "10,10,10", "--apHidden", CELLS[cell], "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01", "--check",
            "--extraTraces", "--simTime", str(sim)] + extra + ["--seed", str(seed), "--tag", tag]
    return {"id": "%s-s%d" % (tag, seed), "on": "actions", "w": 1.1 * sim, "timeout": int(70 * 1.1 * sim * 2 + 600), "cmds": [{"name": "run", "args": args}]}


def build():
    jobs = []
    for cell in CELLS:
        for seed in SEEDS:
            jobs.append(job("g3", cell, "beb", ["--mode", "beb"], seed))
            for e in EDGES:
                for m in MIDS:
                    jobs.append(job("g3", cell, "f1-%d-%d-%d" % (e, m, e), ["--mode", "static", "--apCws", "%d,%d,%d" % (e, m, e)] + STATIC_W, seed))
    assert len({j["id"] for j in jobs}) == len(jobs)
    return {"lanes": 4, "packs": 20, "jobs": jobs}


if __name__ == "__main__":
    b = build()
    json.dump(b, open(sys.argv[1], "w"))
    print(len(b["jobs"]), "runs, %.0f lab-h (7 min/run)" % (len(b["jobs"]) * 7 / 60))
