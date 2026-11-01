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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["a1", "a2"])
    ap.add_argument("out")
    ap.add_argument("--s7loadS4", type=float, default=0.0, help="Mbps per STA = 0.8 x BEB aggregate / STAs (A1: 1.93)")
    ap.add_argument("--s7loadS2", type=float, default=0.0, help="(A1: 0.37)")
    a = ap.parse_args()
    if a.which == "a2" and (a.s7loadS4 <= 0 or a.s7loadS2 <= 0):
        ap.error("a2 needs --s7loadS4 and --s7loadS2")
    jobs = a1() if a.which == "a1" else a2(a.s7loadS4, a.s7loadS2)
    ids = [j["id"] for j in jobs]
    assert len(ids) == len(set(ids))
    json.dump(jobs, open(a.out, "w"), indent=1)
    print(len(jobs), "jobs ->", a.out)
