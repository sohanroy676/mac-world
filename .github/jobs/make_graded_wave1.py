"""v4.2.0 graded-interference wave 1 (Actions) -> .github/jobs/packs-graded-wave1.json. Run: python3 .github/jobs/make_graded_wave1.py
S4-like topology 10,10,10, 10 Mbps per STA, 30 s, seeds 100-104. Five cells: symmetric graded 1-3 at 85/100/108 dB, one-way 1>3 at 100 and 200 dB.
Per cell: BEB, IdleSense and four static CW settings (edge,middle,edge). Same trainer args as m2b-ref jobs (no oracle claim: this wave only maps the cells)."""
import json
import os

CELLS = {"g85": "1-3:85", "g100": "1-3:100", "g108": "1-3:108", "ow100": "1>3:100", "ow200": "1>3:200"}
STATICS = ["32,64,32", "64,64,64", "128,64,128", "256,128,256"]
SEEDS = list(range(100, 105))
W = 8  # minutes per 30 s S4 run (batch4 refs)
jobs = []
for cell, hid in CELLS.items():
    cargs = ["--apStaCounts", "10,10,10", "--apHidden", hid, "--offeredLoad", "10", "--rewardNorm", "150"]
    methods = [("beb", []), ("idlesense", [])] + [("static", ["--apCws", c]) for c in STATICS]
    for part, seeds in enumerate((SEEDS[:3], SEEDS[3:])):
        cmds = []
        for name, extra in methods:
            for s in seeds:
                cmds.append({"name": "%s%s-%d" % (name, extra[1].replace(",", "-") if extra else "", s),
                             "args": cargs + ["--stepTime", "0.01", "--check", "--simTime", "30", "--mode", name] + extra + ["--seed", str(s), "--tag", "graded-%s-%s" % (cell, name)]})
        jobs.append({"id": "graded-w1-%s-p%d" % (cell, part), "on": "actions", "w": W * len(cmds), "cmds": cmds})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "packs-graded-wave1.json"), "w"), indent=1)
print("%d packs, %d runs, %.1f lab-hours" % (len(jobs), sum(len(j["cmds"]) for j in jobs), sum(j["w"] for j in jobs) / 60))
