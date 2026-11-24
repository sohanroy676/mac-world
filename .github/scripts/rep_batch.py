#!/usr/bin/env python3
"""Final report (v4.1.0 line): batch generator for the new mentor-scenario cells (`.github/waves/rep/cells.json`).

  rep_batch.py val OUT.json            short pipeline check of every cell and method (a few simulated seconds)
  rep_batch.py s1  OUT.json            stage 1: BEB (floors) and static grid on seeds 0-2 (60 s, scored on 30-60 s) and learner training (seeds 2000-2002)
  rep_batch.py s2  OUT.json SEL.json   stage 2: evaluation on seeds 400-409 (60 s; cell e5 120 s), rules, statics chosen in SEL.json, kwdirect with floors, frozen learners
  rep_batch.py s2g OUT.json            stage 2 for cell g7s4 only (BEB and BEB+RTS/CTS, seeds 400-409)

SEL.json (written by rep_select.py from the stage-1 summaries): {cell: {"floors": "a,b,c", "common_a0": cw, "common_a1": cw, "model": "cw,cw,..", "prop": "cw,cw,.."}}.
Jobs follow the Wave 3a / 2k / 2l format: {"id", "w", "timeout", "cmds"}. Cost weight w = 1.1 x simulated seconds x max(0.4, STAs / 60) (a 60 s run on 60 STAs = 66).
Methods use the settings of the v4.1.0 tournament (Wave 3a); nothing is tuned on the evaluation seeds."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = json.load(open(os.path.join(HERE, "..", "waves", "rep", "cells.json")))
WIDE = ["--cwLo", "4", "--cwHi", "32767", "--cwExpLo", "-2", "--cwExpHi", "11", "--dacTc", "242e-6", "--dacCw0", "64"]
STATIC_W = ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
GRID = [16, 32, 64, 128, 256, 512, 1024]
RULES = {"dac514": ("dac", ["--dacTc", "514e-6"]), "blade": ("blade", []), "idlesense": ("idlesense", []),
         "kw": ("kw", ["--kwDelta", "0.2", "--kwEta", "0.1"])}
LEARNERS = {"global": ["--mode", "global"], "indep": ["--mode", "independent"], "pf": ["--mode", "independent", "--reward", "pf"]}
TRAIN_SEEDS = (2000, 2001, 2002)
EVAL_SEEDS = range(400, 410)
jobs = []


def sim_of(cell):
    return CELLS[cell].get("sim", 60)


def weight(cell, sim):
    return round(1.1 * sim * max(0.4, sum(CELLS[cell]["counts"]) / 60.0), 1)


def add(jid, cell, cmds, w):
    jobs.append({"id": jid, "w": w, "timeout": int(70 * w + 300), "cmds": cmds})


def run_cmd(cell, name, mode, extra, seed, sim, tag, rts=False):
    args = CELLS[cell]["args"] + ["--stepTime", "0.01", "--check", "--simTime", str(sim), "--mode", mode] + (["--useRts"] if rts else []) + extra + ["--seed", str(seed), "--tag", tag]
    return {"name": name, "args": args}


def single(prefix, cell, name, mode, extra, seed, sim=None, rts=False):
    sim = sim or sim_of(cell)
    tag = "%s-%s-%s-s%d" % (prefix, cell, name, seed)
    add(tag, cell, [run_cmd(cell, "run", mode, extra, seed, sim, tag, rts)], weight(cell, sim))


def actor_files(cell, learner):
    n = 1 if learner == "global" else len(CELLS[cell]["counts"])
    return ["agent%d_%s" % (i, f) for i in range(n) for f in ("actor", "actor_optimizer", "critic", "critic_optimizer")]


def train_job(prefix, cell, learner, tseed, episodes, sim):
    tag = "%s-%s-L-%s-t%d" % (prefix, cell, learner, tseed)
    args = CELLS[cell]["args"] + ["--stepTime", "0.01", "--check"] + LEARNERS[learner] + ["--simTime", str(sim), "--episodes", str(episodes), "--varySeeds",
                                                                                      "--seed", str(tseed), "--saveActor", "{ACT}", "--tag", tag + "-train"]
    add(tag, cell, [{"name": "train", "args": args}], 2 * weight(cell, sim * episodes))  # 2x: trainer overhead (Wave 2k convention)


def sched_args(cell):
    return []


def val():
    for cell in CELLS:
        sim = 45 if cell == "e5" else 6
        single("rv", cell, "beb", "beb", [], 1, sim)
        single("rv", cell, "bebrts", "beb", [], 1, sim, rts=True)
    c = "b2a"
    single("rv", c, "idlesense", "idlesense", [], 1, 6)
    single("rv", c, "dac", "dac", ["--dacTc", "514e-6"], 1, 6)
    single("rv", c, "blade", "blade", [], 1, 6)
    single("rv", c, "kw", "kw", ["--kwDelta", "0.2", "--kwEta", "0.1"], 1, 6)
    single("rv", c, "static", "static", ["--apCws", "64,64,64"] + STATIC_W, 1, 6)
    single("rv", c, "kwdirect", "kwdirect", WIDE + ["--floors", "5,5,5", "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", "1", "--lyTau", "0.6"], 1, 6)
    for cell in ("b2a", "e5"):
        for learner in LEARNERS:
            tag = "rv-%s-L-%s" % (cell, learner)
            targs = CELLS[cell]["args"] + ["--stepTime", "0.01", "--check"] + LEARNERS[learner] + ["--simTime", "4" if cell == "b2a" else "30", "--episodes", "1", "--seed", "2000", "--saveActor", "{ACT}", "--tag", tag + "-train"]
            eargs = CELLS[cell]["args"] + ["--stepTime", "0.01", "--check"] + LEARNERS[learner] + ["--simTime", "4" if cell == "b2a" else "30", "--eval", "--loadActor", "{ACT}", "--fairAlpha", "1", "--seed", "400", "--tag", tag]
            add(tag, cell, [{"name": "train", "args": targs}, {"name": "eval400", "args": eargs}], 20)


def stage1():
    for cell in CELLS:
        if CELLS[cell].get("partial"):
            continue
        sim = sim_of(cell)
        for seed in (0, 1, 2):
            single("rs1", cell, "beb", "beb", [], seed)
            for cw in GRID:
                single("rs1", cell, "cw%d" % cw, "static", ["--apCws", ",".join([str(cw)] * len(CELLS[cell]["counts"]))] + STATIC_W, seed)
        for learner in LEARNERS:
            for t in TRAIN_SEEDS:
                train_job("rs1", cell, learner, t, 3 if cell == "e5" else 12, 120 if cell == "e5" else 15)


def stage2(sel):
    for cell in CELLS:
        if CELLS[cell].get("partial"):
            continue
        sim, n = sim_of(cell), len(CELLS[cell]["counts"])
        s = sel[cell]
        for seed in EVAL_SEEDS:
            single("rs2", cell, "beb", "beb", [], seed)
            single("rs2", cell, "bebrts", "beb", [], seed, rts=True)
            for name, (mode, ex) in RULES.items():
                single("rs2", cell, name, mode, ex, seed)
            single("rs2", cell, "static-a0", "static", ["--apCws", ",".join([str(s["common_a0"])] * n)] + STATIC_W, seed)
            single("rs2", cell, "static-a1", "static", ["--apCws", ",".join([str(s["common_a1"])] * n)] + STATIC_W, seed)
            single("rs2", cell, "static-model", "static", ["--apCws", s["model"]] + STATIC_W, seed)
            single("rs2", cell, "static-prop", "static", ["--apCws", s["prop"]] + STATIC_W, seed)
            for al, tau in ((0, "1.0"), (1, "0.6")):
                single("rs2", cell, "kwdirect-a%d" % al, "kwdirect",
                       WIDE + ["--floors", s["floors"], "--lyEta", "0.25", "--lyDelta", "0.2", "--lyAlpha", str(al), "--lyTau", tau], seed)
        for learner in LEARNERS:
            for t in TRAIN_SEEDS:
                src = "rs1/rs1-%s-L-%s-t%d/actors" % (cell, learner, t)
                for half in (0, 1):
                    cmds = [{"name": "fetch", "fetch": {"src": src, "files": actor_files(cell, learner)}}]
                    for seed in list(EVAL_SEEDS)[5 * half:5 * half + 5]:
                        tag = "rs2-%s-L-%s-t%d-s%d" % (cell, learner, t, seed)
                        args = CELLS[cell]["args"] + ["--stepTime", "0.01", "--check"] + LEARNERS[learner] + ["--simTime", str(sim), "--eval", "--loadActor", "{ACT}", "--fairAlpha", "1", "--seed", str(seed), "--tag", tag]
                        cmds.append({"name": "eval%d" % seed, "args": args})
                    add("rs2-%s-L-%s-t%d-h%d" % (cell, learner, t, half), cell, cmds, 5 * weight(cell, sim))


def stage2g():
    cell = "g7s4"
    for seed in EVAL_SEEDS:
        single("rs2", cell, "beb", "beb", [], seed)
        single("rs2", cell, "bebrts", "beb", [], seed, rts=True)


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    {"val": val, "s1": stage1, "s2g": stage2g}.get(cmd, lambda: stage2(json.load(open(sys.argv[3]))))()
    json.dump({"jobs": jobs}, open(out, "w"))
    print(len(jobs), "jobs, %.0f lab-h (0.2 lab-h per 33 w)" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
