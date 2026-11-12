"""v3.8.0 M2b batch 2 (Hugging Face Space) -> .github/jobs/m2b-batch2-hf.json. Run: python3 .github/jobs/make_m2b_batch2_hf.py
  * drlCW: 3 cells (S2, S4, S5a) x 3 training seeds (python seeds 2000-2002, as M2c), 300 s training (paper Table I), each followed by
    three frozen 30 s evaluations on seeds 100-102 (Stage 1, as M2c). Reward references: docs/figures/v4.0.0-m2b/drlcw-refs/ref-<cell>.json
    (one 300 s BEB run per cell with the delay trace, batch 1); delay scaled by the BEB delay at the same decision (decision card, 2026-11-12).
  * platform cross-check, HF side: dac and ucbctx with the same args as the Actions jobs (m2b-xcheck-*-actions); compare the trace sha256.
All jobs are learner / controller jobs on the HF Space (one CPU type). Weights: minutes, from M2c timings on Actions (HF lane speed is similar)."""
import json
import os

CELLS = {
    "s2": (["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"], 11, 110),
    "s4": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"], 8, 75),
    "s5a": (["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "150,150,1"], 11, 180),
}
COMMON = ["--stepTime", "0.01", "--check", "--mode", "drlcw"]
jobs = []
for cell, (cargs, w_eval, w_train) in CELLS.items():
    ref = "../../../docs/figures/v4.0.0-m2b/drlcw-refs/ref-%s.json" % cell  # run_job runs in ns-3.29/scratch/linear-mesh
    for k in range(3):
        base = cargs + COMMON + ["--drlRef", ref]
        cmds = [{"name": "train", "args": base + ["--simTime", "300", "--episodes", "1", "--seed", str(2000 + k), "--saveActor", "{ACT}",
                                                  "--tag", "m2b-train-%s-drlt%d" % (cell, k)]}]
        for s in (100, 101, 102):
            cmds.append({"name": "eval-%d" % s, "args": base + ["--simTime", "30", "--eval", "--loadActor", "{ACT}", "--seed", str(s),
                                                                "--tag", "m2b-%s-drlt%d" % (cell, k)]})
        jobs.append({"id": "m2b-%s-drlcw-t%d" % (cell, k), "on": "hf", "w": w_train + 3 * w_eval, "cmds": cmds})
x = CELLS["s2"][0] + ["--stepTime", "0.01", "--check", "--simTime", "5", "--seed", "100", "--tag", "m2b-xcheck"]
jobs.append({"id": "m2b-xcheck-dac-hf", "on": "hf", "w": 5, "cmds": [{"name": "run", "args": x + ["--mode", "dac"]}]})
jobs.append({"id": "m2b-xcheck-ucbctx-hf-v2", "on": "hf", "w": 5, "cmds": [{"name": "run", "args": x + ["--mode", "ucbctx", "--ucbC", "0.1"]}]})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "m2b-batch2-hf.json"), "w"), indent=1)
print("%d jobs, %.1f lab-hours" % (len(jobs), sum(j["w"] for j in jobs) / 60))
