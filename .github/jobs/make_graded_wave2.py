"""v4.2.0 graded-interference wave 2 (Actions) -> .github/jobs/packs-graded-wave2.json. Run: python3 .github/jobs/make_graded_wave2.py
Cells g85 (1-3:85) and ow100 (1>3:100), 10,10,10, 10 Mbps, 30 s. Exploratory, not a claim run.
  A. RAFA (shared, rafa obs, fair reward, alpha input, lambda 1, 6 episodes of 15 s, train seeds 2000-2002), floors = wave-1 BEB per-AP means (seeds 100-104).
  B. Global (12 episodes of 15 s, train seeds 2000-2002), same recipe as m2c.
  A and B are evaluated frozen at alpha 1 on seeds 105-109 (held out from the floors); paired refs on 105-109: BEB, IdleSense, static 64,64,64 and 256,128,256.
  C. Finer static grid on seeds 100-102 (edge in 128/256/512 x middle in 64/128/256, minus 256,128,256 already run in wave 1)."""
import json
import os

CELLS = {
    "g85": ("1-3:85", "15.05,7.05,15.17"),
    "ow100": ("1>3:100", "9.89,10.97,14.50"),
}
EV = range(105, 110)
jobs = []
for cell, (hid, floors) in CELLS.items():
    base = ["--apStaCounts", "10,10,10", "--apHidden", hid, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01", "--check"]
    for t in range(3):
        rafa = ["--mode", "shared", "--obs", "rafa", "--reward", "fair", "--alphaInput"]
        cmds = [{"name": "train", "args": base + rafa + ["--simTime", "15", "--episodes", "6", "--varySeeds", "--seed", str(2000 + t), "--floorLambda", "1", "--floors", floors, "--saveActor", "{ACT}", "--tag", "g2-%s-rafa-t%d-train" % (cell, t)]}]
        cmds += [{"name": "eval-%d" % s, "args": base + rafa + ["--simTime", "30", "--eval", "--loadActor", "{ACT}", "--fairAlpha", "1", "--seed", str(s), "--tag", "g2-%s-rafa-t%d" % (cell, t)]} for s in EV]
        jobs.append({"id": "g2-%s-rafa-t%d" % (cell, t), "on": "actions", "w": 90, "cmds": cmds})
        cmds = [{"name": "train", "args": base + ["--simTime", "15", "--mode", "global", "--episodes", "12", "--varySeeds", "--seed", str(2000 + t), "--saveActor", "{ACT}", "--tag", "g2-%s-global-t%d-train" % (cell, t)]}]
        cmds += [{"name": "eval-%d" % s, "args": base + ["--simTime", "30", "--mode", "global", "--eval", "--loadActor", "{ACT}", "--seed", str(s), "--tag", "g2-%s-global-t%d" % (cell, t)]} for s in EV]
        jobs.append({"id": "g2-%s-global-t%d" % (cell, t), "on": "actions", "w": 120, "cmds": cmds})
    refs = [("beb", []), ("idlesense", []), ("static", ["--apCws", "64,64,64"]), ("static", ["--apCws", "256,128,256"])]
    cmds = [{"name": "%s%s-%d" % (m, e[1].replace(",", "-") if e else "", s), "args": base + ["--simTime", "30", "--mode", m] + e + ["--seed", str(s), "--tag", "g2-%s-%s-ref" % (cell, m)]} for m, e in refs for s in EV]
    jobs.append({"id": "g2-%s-refs" % cell, "on": "actions", "w": 8 * len(cmds), "cmds": cmds})
    grid = ["%d,%d,%d" % (e, m, e) for e in (128, 256, 512) for m in (64, 128, 256) if (e, m) != (256, 128)]
    for part in range(2):
        cmds = [{"name": "static%s-%d" % (c.replace(",", "-"), s), "args": base + ["--simTime", "30", "--mode", "static", "--apCws", c, "--seed", str(s), "--tag", "g2-%s-grid" % cell]} for c in grid[part::2] for s in range(100, 103)]
        jobs.append({"id": "g2-%s-grid-p%d" % (cell, part), "on": "actions", "w": 8 * len(cmds), "cmds": cmds})
json.dump({"lanes": 4, "packs": 20, "jobs": jobs}, open(os.path.join(os.path.dirname(__file__), "packs-graded-wave2.json"), "w"), indent=1)
print("%d packs, %d cmds, %.1f lab-hours (weights)" % (len(jobs), sum(len(j["cmds"]) for j in jobs), sum(j["w"] for j in jobs) / 60))
