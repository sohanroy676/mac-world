"""v3.8.0 M2b batch 6 (Actions) -> .github/jobs/m2b-batch6-blade-tune.json. Run: python3 .github/jobs/make_m2b_batch6_blade_tune.py
BLADE tuning on the selection seeds 0-2 (nothing here touches evaluation seeds 100-119), 30 s, S2 and S4, MAR_tar in {0.05, 0.1, 0.2}
(paper default 0.1; its Fig. 17 and Sec. 6.2.1 say performance is flat within +-0.05 of the default and degrades toward MAR_max 0.35).
Same cell args and tuning rule as batch 1 (tune_*_final.md): highest mean alpha-1 GC over S2 and S4 among settings floor-feasible on both."""
import json
import os

CELLS = {
    "s2": (["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"], 11),
    "s4": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"], 8),
}
jobs = []
for cell, (cargs, w) in CELLS.items():
    for tar in ("0.05", "0.1", "0.2"):
        k = tar.replace(".", "")
        cmds = [{"name": "eval-s%d" % s, "args": cargs + ["--stepTime", "0.01", "--check", "--simTime", "30", "--mode", "blade", "--bladeMarTar", tar,
                                                         "--seed", str(s), "--tag", "m2b-tune-%s-blade%s" % (cell, k)]} for s in (0, 1, 2)]
        jobs.append({"id": "m2b-tune-%s-blade%s" % (cell, k), "on": "actions", "w": 3 * w, "cmds": cmds})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "m2b-batch6-blade-tune.json"), "w"), indent=1)
print("%d jobs, %.1f lab-hours" % (len(jobs), sum(j["w"] for j in jobs) / 60))
