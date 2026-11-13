"""v3.8.0 M2b batch 5 (HF, same vendor as the training) -> .github/jobs/m2b-batch5-drlcw-claims.json. Run: python3 .github/jobs/make_m2b_batch5_drlcw_claims.py
Frozen 30 s evals of the drlCW actors selected on seeds 100-102 (docs/results/m2b-results-v4.0.0.md): S2 t0, S4 t1, S5a t1 and t2
(S5a: no seed was floor-feasible; t2 has the best alpha-0 GC, t1 the best alpha 1 and 4), on the claim seeds 103-109. Actors: docs/figures/v4.0.0-m2b/drlcw-v2/."""
import json
import os

CELLS = {
    "s2": (["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"], 11, [0]),
    "s4": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"], 8, [1]),
    "s5a": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "150,150,1"], 11, [1, 2]),
}
jobs = []
for cell, (cargs, w, ks) in CELLS.items():
    ref = "../../../docs/figures/v4.0.0-m2b/drlcw-refs/ref-%s.json" % cell
    for k in ks:
        act = "../../../docs/figures/v4.0.0-m2b/drlcw-v2/m2b-%s-drlcw-v2-t%d/" % (cell, k)
        for part, seeds in enumerate((range(103, 107), range(107, 110))):
            cmds = [{"name": "eval-%d" % s, "args": cargs + ["--stepTime", "0.01", "--check", "--mode", "drlcw", "--drlRef", ref, "--simTime", "30", "--eval",
                                                          "--loadActor", act, "--seed", str(s), "--tag", "m2b-%s-drlv2t%d" % (cell, k)]} for s in seeds]
            jobs.append({"id": "m2b-claim-%s-drlcw-t%d-p%d" % (cell, k, part), "on": "hf", "w": w * len(cmds), "cmds": cmds})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "m2b-batch5-drlcw-claims.json"), "w"), indent=1)
print("%d jobs, %d evals, %.1f lab-hours" % (len(jobs), sum(len(j["cmds"]) for j in jobs), sum(j["w"] for j in jobs) / 60))
