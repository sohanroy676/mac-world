"""v4.2.0 uplink/downlink wave U4. Two files:
  P (kwdirect guard pilot): d3 and d4, alpha 0 and 1, seeds 0-2, 60 s. Variants of the L2 guard (--lyEtaMin, --lyBestDecay); the U3 diagnosis was that after the
  first accepted move the best-seen utility is a lucky maximum, every later probe reverts, eta halves to ~0 and the CW freezes at 16. Plus 180 s runs of
  the old and one new setting to see whether a longer horizon matters.
  L (learned per-scenario RAFA, wide CW range 4..1024): per direction cell, 4 training seeds (2000-2003), 6 episodes x 15 s, alpha input, floor lambda 1,
  then in the same job: alpha 1 on seeds 103-110, alpha 0 and 4 on seeds 103-104. No training-seed selection: all 4 are reported (no selection leak).
Usage: apdir_u4_batch.py OUT_P.json OUT_L.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apdir_u2_batch as u2  # noqa: E402

VARIANTS = {"base": (0.0, 0.0), "m1": (0.1, 0.0), "m1b5": (0.1, 0.5), "m25b5": (0.25, 0.5), "m25b10": (0.25, 1.0), "b5": (0.0, 0.5)}
RAFA_WIDE = ["--cwLo", "4", "--cwHi", "1024", "--cwExpLo", "-2", "--cwExpHi", "6"]


def cell_args(cell, sim):
    counts, hidden, dirs = u2.CELLS[cell]
    return ["--apStaCounts", counts, "--apHidden", hidden, "--apDir", dirs, "--offeredLoad", "10", "--rewardNorm", "150", "--stepTime", "0.01",
            "--check", "--extraTraces", "--simTime", str(sim)]


def job(tag, sim_equiv, cmds):
    return {"id": tag, "on": "actions", "w": 1.1 * sim_equiv, "timeout": int(70 * 1.1 * sim_equiv * 2 + 600), "cmds": cmds}


def pilot():
    jobs = []
    for cell in ("d3", "d4"):
        for name, (emin, bdec) in VARIANTS.items():
            for al in (0, 1):
                for seed in (0, 1, 2):
                    tag = "u4-%s-kw-%s-a%d" % (cell, name, al)
                    args = cell_args(cell, 60) + ["--mode", "kwdirect"] + u2.WIDE + ["--floors", u2.FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2",
                                                  "--lyAlpha", str(al), "--lyTau", "0.6", "--lyEtaMin", str(emin), "--lyBestDecay", str(bdec),
                                                  "--seed", str(seed), "--tag", tag]
                    jobs.append(job("%s-s%d" % (tag, seed), 60, [{"name": "run", "args": args}]))
        for name in ("base", "m25b5"):
            emin, bdec = VARIANTS[name]
            for seed in (0, 1, 2):
                tag = "u4-%s-kwlong-%s-a1" % (cell, name)
                args = cell_args(cell, 180) + ["--mode", "kwdirect"] + u2.WIDE + ["--floors", u2.FLOORS[cell], "--lyEta", "0.25", "--lyDelta", "0.2",
                                              "--lyAlpha", "1", "--lyTau", "0.6", "--lyEtaMin", str(emin), "--lyBestDecay", str(bdec),
                                              "--seed", str(seed), "--tag", tag]
                jobs.append(job("%s-s%d" % (tag, seed), 180, [{"name": "run", "args": args}]))
    assert len({j["id"] for j in jobs}) == len(jobs)
    return {"lanes": 4, "packs": 20, "jobs": jobs}


def learned():
    jobs = []
    margs = ["--mode", "shared", "--obs", "rafa", "--reward", "fair", "--alphaInput", "--rafaDlObs"] + RAFA_WIDE
    for cell in ("u3", "d3", "b3", "m3", "d4", "b4"):
        for ts in range(2000, 2004):
            tag = "u4-%s-rafa-t%d" % (cell, ts)
            train = cell_args(cell, 15) + margs + ["--episodes", "6", "--varySeeds", "--seed", str(ts), "--floors", u2.FLOORS[cell], "--floorLambda", "1",
                                                  "--saveActor", "{ACT}", "--tag", tag + "-train"]
            cmds = [{"name": "train", "args": train}]
            for al, seeds in (("1", range(103, 111)), ("0", range(103, 105)), ("4", range(103, 105))):
                for es in seeds:
                    cmds.append({"name": "eval-a%s-s%d" % (al, es), "args": cell_args(cell, 60) + margs + ["--eval", "--loadActor", "{ACT}", "--fairAlpha", al,
                                                                                                         "--seed", str(es), "--tag", "%s-a%s" % (tag, al)]})
            sim = 90 + 60 * (8 + 2 + 2)
            jobs.append(job(tag, sim, cmds))
    assert len({j["id"] for j in jobs}) == len(jobs)
    return {"lanes": 4, "packs": 20, "jobs": jobs}


if __name__ == "__main__":
    for path, d in ((sys.argv[1], pilot()), (sys.argv[2], learned())):
        json.dump(d, open(path, "w"))
        print(path, len(d["jobs"]), "jobs", "%.0f lab-h (est)" % (sum(j["w"] for j in d["jobs"]) / 66.0 * 690 / 3600))
