"""Loader for the report-wave summaries (rs2a, rs2b): one record per simulation run, keyed (cell, method, seed).

Learner evaluation jobs hold several runs (name eval4xx); their summaries carry job = '<pack job id>-hN'. A learner record is keyed by
the training seed t (2000-2002) and the evaluation seed; `learner_seed_mean` averages the training seeds per evaluation seed.
"""
import ast
import json
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

from common import REPO, mean_ci, jain

sys.path.insert(0, os.path.join(REPO, "ns-3.29", "scratch", "linear-mesh"))
import gc_analysis as g  # noqa: E402

CELLS = json.load(open(os.path.join(REPO, ".github", "waves", "rep", "cells.json")))
SEL = json.load(open(os.path.join(REPO, ".github", "waves", "rep", "SEL.json")))

LABEL = {
    "beb": "BEB (802.11)", "bebrts": "BEB + RTS/CTS", "dac514": "DAC", "blade": "BLADE", "idlesense": "IdleSense",
    "kw": "KW (online)", "static-model": "Static, Patras model", "static-prop": "Static, proportional",
    "static-a0": "Static, common (a=0)", "static-a1": "Static, common (a=1)",
    "kwdirect-a0": "Central search (a=0)", "kwdirect-a1": "Central search (a=1)",
    "L-global": "Global-CW OSCAR", "L-indep": "Independent OSCAR", "L-pf": "PF learner",
}
ORDER = list(LABEL)


def load(paths):
    """-> runs[cell][method][seed] = record (learners: runs[cell][method][seed] = list of records, one per training seed)."""
    runs = defaultdict(lambda: defaultdict(dict))
    for p in paths:
        for line in open(p):
            r = json.loads(line)
            if r.get("check") != "PASS" or not r["job"].startswith("rs2-"):
                continue
            m = re.match(r"rs2-(\w+?)-(.+)$", r["job"])
            cell, rest = m.group(1), m.group(2)
            cfg = r["cfg"] if isinstance(r["cfg"], dict) else ast.literal_eval(r["cfg"])
            r["counts"] = [int(x) for x in cfg["apStaCounts"].split(",")]
            if rest.startswith("L-"):
                lm = re.match(r"L-(\w+?)-t(\d+)-h\d+$", rest)
                method, tseed = "L-" + lm.group(1), int(lm.group(2))
                seed = int(r["name"][4:])
                runs[cell][method].setdefault(seed, {})[tseed] = r
            else:
                sm = re.match(r"(.+)-s(\d+)$", rest)
                runs[cell][sm.group(1)][int(sm.group(2))] = r
    return runs


def thr(r, key="thr_half2"):
    return r[key]


def learner_mean_record(d):
    """average the records of the training seeds into one pseudo-record (per-AP lists averaged)."""
    rs = list(d.values())
    out = dict(rs[0])
    for k in ("thr_half2", "thr_all", "retry_policy", "loss_policy", "cw_mean", "thr_policy", "txfail_policy"):
        if k in rs[0] and rs[0][k] is not None:
            out[k] = np.mean([np.array(x[k], float) for x in rs], axis=0).tolist()
    out["delay"] = rs[0].get("delay")
    out["_n_train"] = len(rs)
    return out


def seed_records(runs, cell, method):
    """{seed: record} with learners averaged over training seeds."""
    d = runs[cell].get(method, {})
    if method.startswith("L-"):
        return {s: learner_mean_record(v) for s, v in d.items()}
    return d


def metrics(r, counts):
    x = [float(v) for v in r["thr_half2"]]
    per = [xi / n for xi, n in zip(x, counts)]
    return {
        "total": sum(x), "per_ap": x, "per_sta": per, "jain": jain(per),
        "min_sta": min(per),
        "u0": g.utility(x, counts, 0), "u1": g.utility(x, counts, 1), "u4": g.utility(x, counts, 4),
        "loss": float(r["loss_policy"]) if r.get("loss_policy") is not None else float("nan"),
        "retry": float(np.mean(r["retry_policy"])) if r.get("retry_policy") else float("nan"),
        "cw": r.get("cw_mean"),
    }


def cell_counts(cell):
    return CELLS[cell]["counts"]


def summarize(runs, cell, counts):
    """per method: dict of arrays over seeds and paired differences vs BEB. Returns {method: {...}}."""
    base = seed_records(runs, cell, "beb")
    if cell in SEL:
        fl = [float(v) for v in SEL[cell]["floors"].split(",")]
    else:  # no stage-1 selection (cell g7s4): floors from the BEB mean of the evaluation seeds
        fl = g.floors(np.mean([b["thr_half2"] for b in base.values()], axis=0).tolist(), counts)
    out = {}
    for meth in ORDER:
        rec = seed_records(runs, cell, meth)
        seeds = sorted(rec)
        if not seeds:
            continue
        M = {s: metrics(rec[s], counts) for s in seeds}
        common = [s for s in seeds if s in base]
        B = {s: metrics(base[s], counts) for s in common}
        o = {"n": len(seeds), "seeds": seeds, "M": M}
        for k in ("total", "jain", "min_sta", "loss", "retry", "u1", "u0", "u4"):
            o[k] = mean_ci([M[s][k] for s in seeds])
        o["per_ap"] = np.mean([M[s]["per_ap"] for s in seeds], axis=0).tolist()
        o["cw"] = (np.mean([M[s]["cw"] for s in seeds], axis=0).tolist() if all(M[s]["cw"] for s in seeds) else None)
        o["d_total_pct"] = mean_ci([100.0 * (M[s]["total"] / B[s]["total"] - 1) for s in common]) if common else None
        o["d_u1"] = mean_ci([M[s]["u1"] - B[s]["u1"] for s in common]) if common else None
        o["d_u0"] = mean_ci([M[s]["u0"] - B[s]["u0"] for s in common]) if common else None
        o["feas"] = float(np.mean([g.feasible(M[s]["per_ap"], fl, 0.05) for s in seeds]))
        out[meth] = o
    return out
