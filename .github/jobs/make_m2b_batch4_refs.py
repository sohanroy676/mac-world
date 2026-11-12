"""v3.8.0 M2b batch 4 (Actions) -> .github/jobs/m2b-batch4-refs.json. Run: python3 .github/jobs/make_m2b_batch4_refs.py
BEB, IdleSense and the oracle statics (M1 / M2c oracles: S2 512,512; S4 64,64,64 and 128,64,128; S5a 128,128,128) on the claim seeds 103-109,
30 s, same args as m2c-ref-*, so the finals of batch 3 can be scored (seeds 100-102 of these runs exist in docs/figures/v4.0.0-m2c/m2c-ref-*)."""
import json
import os

CELLS = {
    "s2": (["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"], 11, ["512,512"]),
    "s4": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"], 8, ["64,64,64", "128,64,128"]),
    "s5a": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "150,150,1"], 11, ["128,128,128"]),
}
jobs = []
for cell, (cargs, w, statics) in CELLS.items():
    methods = [("beb", []), ("idlesense", [])] + [("static", ["--apCws", c]) for c in statics]
    for part, seeds in enumerate((range(103, 106), range(106, 110))):
        cmds = []
        for name, extra in methods:
            for s in seeds:
                cmds.append({"name": "%s%s-%d" % (name, extra[1].replace(",", "-") if extra else "", s),
                             "args": cargs + ["--stepTime", "0.01", "--check", "--simTime", "30", "--mode", name] + extra + ["--seed", str(s), "--tag", "m2b-%s-%s" % (cell, name)]})
        jobs.append({"id": "m2b-ref-%s-p%d" % (cell, part), "on": "actions", "w": w * len(cmds), "cmds": cmds})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "m2b-batch4-refs.json"), "w"), indent=1)
print("%d jobs, %d runs, %.1f lab-hours" % (len(jobs), sum(len(j["cmds"]) for j in jobs), sum(j["w"] for j in jobs) / 60))
