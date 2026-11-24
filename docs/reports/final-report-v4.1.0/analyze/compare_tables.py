#!/usr/bin/env python3
"""Consolidated alpha-1 comparison table from the committed result files: the v4.1.0 tournament (seeds 300-309, share of the ceiling)
plus the original per-AP OSCAR from the v3.6.0 first GC table (different seeds and protocol; labelled)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

hdr, rows = next((h, r) for _, h, r in md_tables(os.path.join(RESULTS, "wave3a-v4.1.0.md")) if h[0] == "family" and "worst" in h)
col = {c: i for i, c in enumerate(hdr)}
NAME = {"kwdirect": "kwdirect (central online search)", "static-F1": "Best static CW per AP (offline reference)", "static-F2": "Best static CWmin (offline reference)",
        "blade": "BLADE", "dac514": "DAC (Patras et al.)", "idlesense": "IdleSense", "kw": "KW (Gawłowicz et al.)", "ucbctx": "Contextual UCB",
        "global": "Global-CW OSCAR-style learner (one CW for all APs)", "pf": "Independent per-AP learner with fairness reward (PF)", "rafa-a1": "RAFA (shared actor, per scenario)"}
out = []
for r in rows:
    if r[0] in NAME:
        out.append([NAME[r[0]], r[col["s2 a1"]], r[col["s4 a1"]], r[col["s5a a1"]], r[col["worst"]]])
m1 = open(os.path.join(RESULTS, "m1-oracle-grids-v3.6.0.md"), encoding="utf8").read()
oscar = []
sec4 = m1.split("## First GC table, S4")[1].split("\n## ")[0]
sec25 = m1.split("## First GC table, S2 and S5a")[1].split("\n## ")[0]
for cell, sec, pat in (("S2", sec25, r"\| S2 \| OSCAR per AP \| ([-\d.]+) \| ([-\d.]+) \|"), ("S4", sec4, r"\| OSCAR per AP \| ([-\d.]+) \| ([-\d.]+) \|"),
                       ("S5a", sec25, r"\| S5a \| OSCAR per AP \| ([-\d.]+) \| ([-\d.]+) \|")):
    m = re.search(pat, sec)
    oscar.append(m.group(2) if m else "n/a")
txt = md_table(["Method", "S2 (20,40)", "S4 (hidden chain)", "S5a (unequal load)", "Worst of 9 cells"], [["BEB (reference)", "0", "0", "0", "0"]] + out)
open(os.path.join(GEN, "compare_alpha1.md"), "w", encoding="utf8").write(txt)
open(os.path.join(GEN, "compare_oscar_perap.md"), "w", encoding="utf8").write(
    "Original independent per-AP OSCAR (v3.6.0, evaluation seeds 100 to 102, 2 training episodes, gap closed at alpha 1): S2 %s, S4 %s, S5a %s; floor-infeasible in all three cells.\n" % tuple(oscar))
print(txt, oscar)
