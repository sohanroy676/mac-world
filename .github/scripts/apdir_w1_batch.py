"""v4.2.0 uplink/downlink wave U1 (selection seeds 0-2, 30 s): BEB, IdleSense and DAC (Tc 514 us) in six direction cells, plus a
static (edge, middle) oracle grid per cell for the later floors and ceilings. Cells: S4-type 3-AP hidden chain with directions uuu (control),
ddd, bbb and u,d,b; 4-AP hidden line (pairs 1-3, 2-4, 1-4) with ddd and bbb. 10 Mbps per STA per direction, --rewardNorm 150.
Non-learned modes only, so every job is byte-identical on any runner CPU. Usage: apdir_w1_batch.py OUT.json"""
import json
import sys

CELLS = {
    "u3": ("10,10,10", "1-3", "u,u,u"), "d3": ("10,10,10", "1-3", "d,d,d"), "b3": ("10,10,10", "1-3", "b,b,b"), "m3": ("10,10,10", "1-3", "u,d,b"),
    "d4": ("10,10,10,10", "1-3,2-4,1-4", "d,d,d,d"), "b4": ("10,10,10,10", "1-3,2-4,1-4", "b,b,b,b"),
}
SEEDS = (0, 1, 2)
SIM = 30
GRID = (32, 64, 128, 256, 512)
jobs = []


def add(cell, name, mode_args, seed):
    counts, hidden, dirs = CELLS[cell]
    tag = "u1-%s-%s" % (cell, name)
    args = ["--apStaCounts", counts, "--apHidden", hidden, "--apDir", dirs, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01",
            "--check", "--extraTraces", "--simTime", str(SIM)] + mode_args + ["--seed", str(seed), "--tag", tag]
    jobs.append({"id": "%s-s%d" % (tag, seed), "on": "actions", "w": 1.1 * SIM, "timeout": int(70 * 1.1 * SIM * 2 + 600), "cmds": [{"name": "run", "args": args}]})


for cell in CELLS:
    n = CELLS[cell][0].count(",") + 1
    for seed in SEEDS:
        add(cell, "beb", ["--mode", "beb"], seed)
        add(cell, "idlesense", ["--mode", "idlesense"], seed)
        add(cell, "dac514", ["--mode", "dac", "--dacTc", "514e-6"], seed)
        for e in GRID:
            for m in GRID:
                cws = [e] + [m] * (n - 2) + [e]
                add(cell, "static-" + "-".join(map(str, cws)), ["--mode", "static", "--apCws", ",".join(map(str, cws))], seed)
assert len({j["id"] for j in jobs}) == len(jobs)
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
