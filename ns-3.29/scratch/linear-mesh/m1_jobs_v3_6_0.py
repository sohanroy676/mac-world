"""v3.6.0 (M1) job-list generator for batch_driver_v3_5_0.py.

  python m1_jobs_v3_6_0.py a1 OUT.json                 # BEB on selection seeds 0-2: S2, S4, S5a, S8 phase 3
  python m1_jobs_v3_6_0.py a2 OUT.json --s7loadS4 1.93 --s7loadS2 0.37   # oracle grids, convergence, G0a, S7 (Mbps per STA = 0.8 x BEB aggregate / STAs)

Cells: s2 = 20,40 load 10; s4 = 10,10,10 --apHidden 1-3 load 10; s5a = S4 with --apLoads 150,150,1 (loads as stated);
s8p3 = S4 with the 5 first STAs of AP1 and AP3 off for the whole run (--staSchedule window outside the run), load 10;
s7-s2 / s7-s4 = delay cells at --offeredLoad X. Equal-load cells use 10 Mbps per STA + --rewardNorm 150.
Tags: m1-<cell>-<method>, method = beb | <cw1>-<cw2>[-<cw3>] | idlesense. Selection seeds only (python seeds 0-2).
"""
import argparse
import itertools
import json

SEEDS = (0, 1, 2)
BASE = ["--simTime", "15", "--stepTime", "0.01", "--check", "--extraTraces"]
CELLS = {
    "s2": ["--apStaCounts", "20,40", "--offeredLoad", "10", "--rewardNorm", "150"],
    "s4": ["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150"],
    "s5a": ["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "150,150,1"],
    "s8p3": ["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--offeredLoad", "10", "--rewardNorm", "150",
             "--staSchedule", "0:0-4:100:101/2:0-4:100:101"],
}


def job(cell, method, seed, extra_cell=None):
    if method == "beb":
        mode = ["--mode", "beb"]
    elif method == "idlesense":
        mode = ["--mode", "idlesense"]
    else:
        mode = ["--mode", "static", "--apCws", method.replace("-", ",")]
    args = list(CELLS.get(cell) or extra_cell) + BASE + mode + ["--seed", str(seed), "--tag", "m1-%s-%s" % (cell, method)]
    return {"id": "%s-%s-s%d" % (cell, method, seed), "args": args, "deps": []}


def grid(cell, cws, seeds=SEEDS, extra_cell=None):
    return [job(cell, "-".join(map(str, c)), s, extra_cell) for c in cws for s in seeds]


def a1():
    # S8 phase 3 first: it is the only cell whose flag has not run at this length (validate before the rest)
    return [job(c, "beb", s) for c in ("s8p3", "s4", "s2", "s5a") for s in SEEDS]


def a2(s7load_s4, s7load_s2):
    jobs = []
    # S4 grid: edges x middle, common CWs, alpha-0 (small CW) region
    s4 = [(e, m, e) for e in (128, 256, 512) for m in (32, 64, 128, 256)]
    s4 += [(c, c, c) for c in (16, 32, 64, 512, 1023)]
    s4 += [(32, 64, 32), (32, 128, 32), (32, 256, 32), (64, 128, 64), (64, 256, 64)]
    jobs += grid("s4", s4)
    # IdleSense convergence (published rule, default parameters) and G0a (S2 oracle region)
    jobs += [job(c, "idlesense", s) for c in ("s2", "s4") for s in SEEDS]
    jobs += grid("s2", [(512, 512), (256, 256)])
    jobs += grid("s8p3", [(e, m, e) for e in (64, 128, 256) for m in (32, 64, 128, 256)])
    jobs += grid("s5a", [(a, b, 128) for a in (64, 128, 256, 512) for b in (32, 64, 128, 256)])
    # S7: delay cells at the given load per STA
    s7c = lambda apc, hid, load: ["--apStaCounts", apc] + (["--apHidden", hid] if hid else []) + ["--offeredLoad", str(load), "--rewardNorm", "150"]
    s4c = s7c("10,10,10", "1-3", s7load_s4)
    jobs += [job("s7-s4", "beb", s, s4c) for s in SEEDS]
    jobs += grid("s7-s4", [(c, c, c) for c in (16, 32, 64, 128, 256)] + [(256, 128, 256), (256, 64, 256), (128, 64, 128)], extra_cell=s4c)
    s2c = s7c("20,40", "", s7load_s2)
    jobs += [job("s7-s2", "beb", s, s2c) for s in SEEDS]
    jobs += grid("s7-s2", [(c, c) for c in (16, 32, 64, 128, 256, 512)], extra_cell=s2c)
    return jobs


S7B = ["--apStaCounts", "10,10,10", "--apHidden", "1-3", "--apLoads", "1.93,1.0,1.93", "--rewardNorm", "150"]


def a4(gate_only):
    """v3.6.1: S7-S4 redesign (per-AP loads, tag s7-s4b) and S8p3 lower edge CWs. gate_only = 4 feasibility jobs, seed 0."""
    if gate_only:
        return [job("s7-s4b", m, 0, S7B) for m in ("beb", "64-64-64", "128-64-128", "256-128-256")]
    jobs = [job("s7-s4b", "beb", s, S7B) for s in SEEDS]
    jobs += grid("s7-s4b", [(c, c, c) for c in (16, 32, 64, 128, 256)] + [(256, 128, 256), (256, 64, 256), (128, 64, 128)], extra_cell=S7B)
    jobs += grid("s8p3", [(e, m, e) for e in (16, 32) for m in (16, 32, 64, 128)])
    return jobs


EVAL_SEEDS = (100, 101, 102)
GC_BASE = ["--simTime", "15", "--stepTime", "0.01", "--check"]
ACTORS = "/home/pranay/mac-world/ns-3.29/scratch/linear-mesh/results/m1/actors"


def a3(statics, pf_seeds=(0, 1, 2), cells=("s4", "s2", "s5a")):
    """First GC table jobs (eval seeds 100-102): BEB, static oracles, IdleSense, Global-CW, OSCAR per AP (independent,
    local reward), static PF learner (independent --reward pf, 3 train seeds). Learners: 2 training episodes (v3.4.0),
    frozen eval. Tags m1gc-<cell>-<method>; method = beb | idlesense | global | oscar | pf<k>; statics by apCws."""
    jobs = []

    def add(cell, name, seed, mode, extra, deps=()):
        jobs.append({"id": "gc-%s-%s-s%d" % (cell, name, seed), "deps": list(deps),
                     "args": list(CELLS[cell]) + GC_BASE + ["--mode", mode, "--seed", str(seed)] + extra})

    for cell in cells:
        for sd in EVAL_SEEDS:
            add(cell, "beb", sd, "beb", ["--tag", "m1gc-%s-beb" % cell])
        for cws in statics.get(cell, []):
            for sd in EVAL_SEEDS:
                add(cell, "static-" + cws.replace(",", "-"), sd, "static", ["--apCws", cws, "--tag", "m1gc-%s-static" % cell])
        for sd in EVAL_SEEDS:
            add(cell, "idlesense", sd, "idlesense", ["--tag", "m1gc-%s-idlesense" % cell])
        arms = [("global", "global", [], 2000, "global"), ("oscar", "independent", [], 2000, "oscar")]  # training ns-3 seeds 2001+ (plan)
        arms += [("pf%d" % k, "independent", ["--reward", "pf"], 2000 + k, "pf%d" % k) for k in pf_seeds]
        for name, mode, extra, tseed, tag in arms:
            d = "%s/%s-%s" % (ACTORS, cell, name)
            tid = "gc-%s-%s-train" % (cell, name)
            jobs.append({"id": tid, "deps": [], "args": list(CELLS[cell]) + GC_BASE + [
                "--mode", mode, "--seed", str(tseed), "--episodes", "2", "--varySeeds", "--saveActor", d,
                "--tag", "m1gc-%s-train-%s" % (cell, name)] + extra})
            for sd in EVAL_SEEDS:
                add(cell, name, sd, mode, ["--loadActor", d, "--eval", "--tag", "m1gc-%s-%s" % (cell, tag)] + extra, deps=[tid])
    return jobs


def a5(statics, sim_time="30", seeds=tuple(range(100, 110)), pf_seeds=(0, 1, 2), cells=("s4", "s2", "s5a")):
    """v3.6.1 Stage-2 GC jobs: same methods as a3 at eval seeds 100-109 and simTime 30 (plan rule: a cell with IdleSense runs
    30 s for every method). Learners reload the frozen actors saved by a3 (no training jobs). Tags m1gc30-<cell>-<method>."""
    base = ["--simTime", sim_time, "--stepTime", "0.01", "--check"]
    jobs = []

    def add(cell, name, seed, mode, extra):
        jobs.append({"id": "gc30-%s-%s-s%d" % (cell, name, seed), "deps": [],
                     "args": list(CELLS[cell]) + base + ["--mode", mode, "--seed", str(seed)] + extra})

    for cell in cells:
        for sd in seeds:
            add(cell, "beb", sd, "beb", ["--tag", "m1gc30-%s-beb" % cell])
            for cws in statics.get(cell, []):
                add(cell, "static-" + cws.replace(",", "-"), sd, "static", ["--apCws", cws, "--tag", "m1gc30-%s-static" % cell])
            add(cell, "idlesense", sd, "idlesense", ["--tag", "m1gc30-%s-idlesense" % cell])
            arms = [("global", "global", []), ("oscar", "independent", [])]
            arms += [("pf%d" % k, "independent", ["--reward", "pf"]) for k in pf_seeds]
            for name, mode, extra in arms:
                add(cell, name, sd, mode, ["--loadActor", "%s/%s-%s" % (ACTORS, cell, name), "--eval", "--tag", "m1gc30-%s-%s" % (cell, name)] + extra)
    return jobs


def a5(statics, seeds, sim_time, cells=("s4", "s2", "s5a"), pf_seeds=(0, 1, 2)):
    """v3.6.1: GC-table evaluations at more eval seeds and one sim length (plan rule: 30 s in cells with IdleSense).
    Same methods as a3, learners reload the actors a3 saved (no training jobs). Tags m1gc30-<cell>-<method>."""
    jobs = []
    base = ["--simTime", str(sim_time), "--stepTime", "0.01", "--check"]

    def add(cell, name, seed, mode, extra):
        jobs.append({"id": "gc%d-%s-%s-s%d" % (sim_time, cell, name, seed), "deps": [],
                     "args": list(CELLS[cell]) + base + ["--mode", mode, "--seed", str(seed)] + extra})

    for cell in cells:
        for sd in seeds:
            add(cell, "beb", sd, "beb", ["--tag", "m1gc%d-%s-beb" % (sim_time, cell)])
            for cws in statics.get(cell, []):
                add(cell, "static-" + cws.replace(",", "-"), sd, "static", ["--apCws", cws, "--tag", "m1gc%d-%s-static" % (sim_time, cell)])
            add(cell, "idlesense", sd, "idlesense", ["--tag", "m1gc%d-%s-idlesense" % (sim_time, cell)])
            arms = [("global", "global", []), ("oscar", "independent", [])]
            arms += [("pf%d" % k, "independent", ["--reward", "pf"]) for k in pf_seeds]
            for name, mode, extra in arms:
                add(cell, name, sd, mode, ["--loadActor", "%s/%s-%s" % (ACTORS, cell, name), "--eval",
                                           "--tag", "m1gc%d-%s-%s" % (sim_time, cell, name)] + extra)
    return jobs


def a6():
    """v3.7.0 M2: BEB + RTS/CTS (`--mode beb --useRts`). Selection seeds 0-2 at 15 s (S8p3 and both S7 delay cells; tags
    m2-<cell>-rts, run dirs compare to m1-<cell>-beb) and GC evaluation on S2/S4/S5a, seeds 100-109 at 30 s (tag m2gc30-<cell>-rts)."""
    jobs = []
    s7 = {"s7-s4b": S7B, "s7-s2": ["--apStaCounts", "20,40", "--offeredLoad", "0.37", "--rewardNorm", "150"]}
    for cell in ("s8p3", "s7-s4b", "s7-s2"):
        for sd in SEEDS:
            j = job(cell, "beb", sd, s7.get(cell))
            j["id"] = "m2-%s-rts-s%d" % (cell, sd)
            j["args"] = [a if a != "m1-%s-beb" % cell else "m2-%s-rts" % cell for a in j["args"]] + ["--useRts"]
            jobs.append(j)
    for cell in ("s4", "s2", "s5a"):
        for sd in range(100, 110):
            jobs.append({"id": "m2gc30-%s-rts-s%d" % (cell, sd), "deps": [],
                         "args": list(CELLS[cell]) + ["--simTime", "30", "--stepTime", "0.01", "--check", "--mode", "beb", "--useRts",
                                                       "--seed", str(sd), "--tag", "m2gc30-%s-rts" % cell]})
    return jobs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["a1", "a2", "a3", "a4", "a4gate", "a5", "a6"])
    ap.add_argument("out")
    ap.add_argument("--s7loadS4", type=float, default=0.0, help="Mbps per STA = 0.8 x BEB aggregate / STAs (A1: 1.93)")
    ap.add_argument("--s7loadS2", type=float, default=0.0, help="(A1: 0.37)")
    ap.add_argument("--statics", default="", help="a3: cell=cw,cw,cw+cw,cw,cw;cell=... static oracle settings to evaluate, e.g. s4=64,64,64+128,64,128;s2=512,512")
    ap.add_argument("--evalSeeds", default="100,101,102,103,104,105,106,107,108,109", help="a5")
    ap.add_argument("--simTime", type=int, default=30, help="a5")
    a = ap.parse_args()
    if a.which == "a2" and (a.s7loadS4 <= 0 or a.s7loadS2 <= 0):
        ap.error("a2 needs --s7loadS4 and --s7loadS2")
    if a.which == "a3":
        st = {kv.split("=")[0]: kv.split("=")[1].split("+") for kv in a.statics.split(";") if kv}
        jobs = a3(st)
    elif a.which == "a5":
        st = {kv.split("=")[0]: kv.split("=")[1].split("+") for kv in a.statics.split(";") if kv}
        jobs = a5(st, [int(x) for x in a.evalSeeds.split(",")], a.simTime)
    elif a.which == "a6":
        jobs = a6()
    elif a.which in ("a4", "a4gate"):
        jobs = a4(a.which == "a4gate")
    else:
        jobs = a1() if a.which == "a1" else a2(a.s7loadS4, a.s7loadS2)
    ids = [j["id"] for j in jobs]
    assert len(ids) == len(set(ids))
    json.dump(jobs, open(a.out, "w"), indent=1)
    print(len(jobs), "jobs ->", a.out)
