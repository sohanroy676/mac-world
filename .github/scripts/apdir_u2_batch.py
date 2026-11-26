"""v4.2.0 uplink/downlink wave U2 (selection seeds 0-2): (a) exact static grid below CW 16 (--cwHold, --cwLo 4) per direction cell, so the oracle is not
clamped at 16; (b) kwdirect (the v4.1.0 online controller, settings of Wave 2/4a) at alpha 0, 1, 4 with fair floors = min(BEB_i, fair share of the BEB total),
BEB means from wave U1 (seeds 0-2, 30 s, second half). Cells as in apdir_w1_batch.py. Usage: apdir_u2_batch.py OUT.json"""
import json
import sys

CELLS = {
    "u3": ("10,10,10", "1-3", "u,u,u"), "d3": ("10,10,10", "1-3", "d,d,d"), "b3": ("10,10,10", "1-3", "b,b,b"), "m3": ("10,10,10", "1-3", "u,d,b"),
    "d4": ("10,10,10,10", "1-3,2-4,1-4", "d,d,d,d"), "b4": ("10,10,10,10", "1-3,2-4,1-4", "b,b,b,b"),
}
FLOORS = {"b3": "25.28,0.52,25.28", "b4": "18.45,7.67,9.92,18.45", "d3": "24.37,5.21,24.37", "d4": "20.20,13.69,13.71,20.20",
          "m3": "25.34,0.35,25.34", "u3": "24.21,1.46,24.21"}
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
STATIC_W = ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
EDGES = (4, 8, 12, 16, 24, 32, 64, 128, 256)
MIDS = (4, 8, 12, 16, 24, 32, 64)
SEEDS = (0, 1, 2)
jobs = []


def add(cell, name, sim, extra, seed):
    counts, hidden, dirs = CELLS[cell]
    tag = "u2-%s-%s" % (cell, name)
    args = ["--apStaCounts", counts, "--apHidden", hidden, "--apDir", dirs, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01",
            "--check", "--extraTraces", "--simTime", str(sim)] + extra + ["--seed", str(seed), "--tag", tag]
    jobs.append({"id": "%s-s%d" % (tag, seed), "on": "actions", "w": 1.1 * sim, "timeout": int(70 * 1.1 * sim * 2 + 600), "cmds": [{"name": "run", "args": args}]})


for cell in CELLS:
    n = CELLS[cell][0].count(",") + 1
    for seed in SEEDS:
        for e in EDGES:
            for m in MIDS:
                cws = [e] + [m] * (n - 2) + [e]
                add(cell, "f1-" + "-".join(map(str, cws)), 30, ["--mode", "static", "--apCws", ",".join(map(str, cws))] + STATIC_W, seed)
        for al in (0, 1, 4):
            add(cell, "kwdirect-a%d" % al, 60, ["--mode", "kwdirect"] + WIDE + ["--floors", FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2",
                                                                               "--lyAlpha", str(al), "--lyTau", "0.6"], seed)
assert len({j["id"] for j in jobs}) == len(jobs)
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "runs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
