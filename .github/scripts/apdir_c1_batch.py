"""v4.2.0 uplink/downlink confirmation wave C1: fresh seeds 103-122, 60 s, scored on the second half. Per direction cell: BEB, IdleSense, DAC (Tc 514 us),
the exact static oracle point chosen on seeds 0-2 for each alpha (docs/results/uplink-downlink-oracle-points-v4.2.0.json, from wave U2) and kwdirect
(v4.1.0 settings) at alpha 0, 1, 4 with the U2 floors. Written as two files by cell (one file would overflow the Actions matrix output):
apdir_c1_batch.py OUT_A.json OUT_B.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apdir_u2_batch as u2  # noqa: E402

ORACLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "results", "uplink-downlink-oracle-points-v4.2.0.json")))
SEEDS = range(103, 123)
SIM = 60


def build(cells):
    jobs = []

    def add(cell, name, extra, seed):
        counts, hidden, dirs = u2.CELLS[cell]
        tag = "c1-%s-%s" % (cell, name)
        args = ["--apStaCounts", counts, "--apHidden", hidden, "--apDir", dirs, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01",
                "--check", "--extraTraces", "--simTime", str(SIM)] + extra + ["--seed", str(seed), "--tag", tag]
        jobs.append({"id": "%s-s%d" % (tag, seed), "on": "actions", "w": 1.1 * SIM, "timeout": int(70 * 1.1 * SIM * 2 + 600), "cmds": [{"name": "run", "args": args}]})

    for cell in cells:
        for seed in SEEDS:
            add(cell, "beb", ["--mode", "beb"], seed)
            add(cell, "idlesense", ["--mode", "idlesense"], seed)
            add(cell, "dac514", ["--mode", "dac", "--dacTc", "514e-6"], seed)
            for al in ("0", "1", "4"):
                add(cell, "f1-a%s" % al, ["--mode", "static", "--apCws", ORACLE[cell][al].replace("-", ",")] + u2.STATIC_W, seed)
                add(cell, "kwdirect-a%s" % al, ["--mode", "kwdirect"] + u2.WIDE + ["--floors", u2.FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2",
                                                                                   "--lyAlpha", al, "--lyTau", "0.6"], seed)
    assert len({j["id"] for j in jobs}) == len(jobs)
    return {"lanes": 4, "packs": 20, "jobs": jobs}


if __name__ == "__main__":
    for path, cells in ((sys.argv[1], ("u3", "d3", "b3")), (sys.argv[2], ("m3", "d4", "b4"))):
        b = build(cells)
        json.dump(b, open(path, "w"))
        print(path, len(b["jobs"]), "runs")
