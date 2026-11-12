"""v3.8.0 M2b batch 1 -> .github/jobs/m2b-batch1.json (format of run-packs.yml / tools/hf). Run: python3 .github/jobs/make_m2b_batch1.py
Contents (all on selection seeds 0-2 unless noted; nothing here touches evaluation seeds 100-119):
  * tuning of the three non-learned rivals, 3 settings each (same budget as the M2 rivals), S2 and S4, 30 s:
      ucbctx c in {0.1, 0.3, 1}; dac Tc in {128, 257, 514} us (Tc is an inference, see docs/results/m2b-specs-v4.0.0.md);
      model-static with the same three Tc values.
  * drlCW reference runs: one BEB run of 300 s per cell with --delayWindow 0.5, reduced to ref.json (thp, per, delay) by drlcw_refs.py --write.
  * platform cross-check: dac and ucbctx, same args, one job on actions and one on hf (compare the trace sha256).
Weights w are minutes from the M2c Actions timings (30 s eval: S2 11, S4 8, S5a 11 min; BEB 300 s about 10x that)."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ns-3.29", "scratch", "linear-mesh"))
from ap_controllers import model_static_cw  # noqa: E402

CELLS = {
    "s2": dict(topo="20,40", counts=[20, 40], args=["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"], w=11),
    "s4": dict(topo="10,10,10", counts=[10, 10, 10], args=["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"], w=8),
    "s5a": dict(topo="10,10,10", counts=[10, 10, 10], args=["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "150,150,1"], w=11),
}
COMMON = ["--stepTime", "0.01", "--check"]
TCS = {"128": 128e-6, "257": 257e-6, "514": 514e-6}
UCB_C = {"01": "0.1", "03": "0.3", "1": "1"}


def cmd(name, cell, extra, sim=30):
    return {"name": name, "args": CELLS[cell]["args"] + COMMON + ["--simTime", str(sim)] + extra}


def exps(cell, tag, extra):
    return [cmd("eval-s%d" % s, cell, extra + ["--seed", str(s), "--tag", "m2b-tune-%s-%s" % (cell, tag)]) for s in (0, 1, 2)]


jobs = []
for cell in ("s2", "s4"):
    for k, c in UCB_C.items():
        jobs.append({"id": "m2b-tune-%s-ucbctx%s" % (cell, k), "on": "actions", "w": 3 * CELLS[cell]["w"], "cmds": exps(cell, "ucbctx" + k, ["--mode", "ucbctx", "--ucbC", c])})
    for k, tc in TCS.items():
        jobs.append({"id": "m2b-tune-%s-dac%s" % (cell, k), "on": "actions", "w": 3 * CELLS[cell]["w"], "cmds": exps(cell, "dac" + k, ["--mode", "dac", "--dacTc", repr(tc)])})
        cws = ",".join("%d" % round(model_static_cw(n, tc=tc)) for n in CELLS[cell]["counts"])
        jobs.append({"id": "m2b-tune-%s-ms%s" % (cell, k), "on": "actions", "w": 3 * CELLS[cell]["w"], "cmds": exps(cell, "ms" + k, ["--mode", "static", "--apCws", cws])})
for cell in ("s2", "s4", "s5a"):
    jobs.append({"id": "m2b-drlref-%s" % cell, "on": "actions", "w": 10 * CELLS[cell]["w"], "cmds": [
        cmd("beb300", cell, ["--mode", "beb", "--delayWindow", "0.5", "--seed", "0", "--tag", "m2b-drlref-" + cell], sim=300),
        {"name": "ref", "args": ["drlcw_refs.py", "--write", "{ACT}/ref.json", "{LAST}/trace.csv"]}]})
for mode, extra in (("dac", []), ("ucbctx", ["--ucbC", "0.1"])):
    for plat in ("actions", "hf"):
        jobs.append({"id": "m2b-xcheck-%s-%s" % (mode, plat), "on": plat, "w": 5, "cmds": [cmd("run", "s2", ["--mode", mode, "--seed", "100", "--tag", "m2b-xcheck"] + extra, sim=5)]})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "m2b-batch1.json"), "w"), indent=1)
tot = sum(j["w"] for j in jobs)
print("%d jobs, %d weighted minutes (%.1f lab-hours)" % (len(jobs), tot, tot / 60))
for j in jobs:
    if "ms" in j["id"] and "tune" in j["id"]:
        print(j["id"], j["cmds"][0]["args"][-3:])
