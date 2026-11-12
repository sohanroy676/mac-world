"""v3.8.0 M2b batch 3 (Actions) -> .github/jobs/m2b-batch3-finals.json. Run: python3 .github/jobs/make_m2b_batch3_finals.py
Final n = 10 runs (eval seeds 100-109, 30 s) of the setting each non-learned rival selected on the selection seeds 0-2
(rule as in M2: highest mean alpha-1 GC over S2 and S4 among settings floor-feasible on both; none feasible -> highest mean, labelled infeasible):
  dac     Tc 514 us (feasible on both)         ucbctx  c = 1 (infeasible on S2)         model-static  Tc 257 us (infeasible on S2)
Evaluation seeds 100-102 select a training seed for learners; claims use 103-109 only (plan), all ten are run. Jobs are 5 seeds each.
Weights: 30 s eval about 11 min (S2), 8 (S4), 11 (S5a) on an Actions lane."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
from ap_controllers import model_static_cw  # noqa: E402

CELLS = {
    "s2": (["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"], 11, [20, 40]),
    "s4": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"], 8, [10, 10, 10]),
    "s5a": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "150,150,1"], 11, [10, 10, 10]),
}
jobs = []
for cell, (cargs, w, counts) in CELLS.items():
    rivals = {
        "dac": ["--mode", "dac", "--dacTc", repr(514e-6)],
        "ucbctx": ["--mode", "ucbctx", "--ucbC", "1"],
        "ms": ["--mode", "static", "--apCws", ",".join("%d" % round(model_static_cw(n, tc=257e-6)) for n in counts)],
    }
    for name, extra in rivals.items():
        for part, seeds in enumerate((range(100, 105), range(105, 110))):
            cmds = [{"name": "eval-%d" % s, "args": cargs + ["--stepTime", "0.01", "--check", "--simTime", "30"] + extra + ["--seed", str(s), "--tag", "m2b-%s-%s" % (cell, name)]} for s in seeds]
            jobs.append({"id": "m2b-final-%s-%s-p%d" % (cell, name, part), "on": "actions", "w": 5 * w, "cmds": cmds})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "m2b-batch3-finals.json"), "w"), indent=1)
print("%d jobs, %.1f lab-hours" % (len(jobs), sum(j["w"] for j in jobs) / 60))
