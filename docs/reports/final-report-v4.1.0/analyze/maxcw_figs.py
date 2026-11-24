#!/usr/bin/env python3
"""Figures and table snippets for the max-CW study (v4.1.0): ceilings, tournament (Wave 3a), confirmation (Wave 4a), Gate C.
Everything is read from the committed result files in docs/results/ (parsed markdown tables), nothing is typed in by hand."""
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

CELLS = ["s2 a0", "s2 a1", "s2 a4", "s4 a0", "s4 a1", "s4 a4", "s5a a0", "s5a a1", "s5a a4"]
NICE = {"s2 a0": "S2α=0", "s2 a1": "S2α=1", "s2 a4": "S2α=4", "s4 a0": "S4α=0", "s4 a1": "S4α=1", "s4 a4": "S4α=4",
        "s5a a0": "S5aα=0", "s5a a1": "S5aα=1", "s5a a4": "S5aα=4"}


def tournament():
    tabs = md_tables(os.path.join(RESULTS, "wave3a-v4.1.0.md"))
    hdr, rows = next((h, r) for _, h, r in tabs if h[0] == "family" and "worst" in h)
    names = [r[0] for r in rows]
    vals = np.array([[num(c) if c not in ("-", "n/a") else np.nan for c in r[1:10]] for r in rows])
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    cmap = LinearSegmentedColormap.from_list("div", [C["orange"], "#f4f4f2", C["blue"]])
    show = np.clip(vals, -0.5, 1.1)
    im = ax.imshow(np.ma.masked_invalid(show), cmap=cmap, norm=TwoSlopeNorm(vmin=-0.5, vcenter=0.5, vmax=1.1), aspect="auto")
    ax.set_xticks(range(9)); ax.set_xticklabels([NICE[c] for c in CELLS], rotation=35, ha="right")
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names)
    ax.grid(False)
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            v = vals[i, j]
            if v == v:
                ax.text(j, i, "%.2f" % v if v > -9 else "<-9", ha="center", va="center", fontsize=7, color=INK)
    ax.set_title("Wave 3a tournament: share of the validated ceiling (seeds 300-309)")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("share (colour clipped to -0.5 .. 1.1)", fontsize=8)
    return save(fig, "maxcw_tournament_heatmap.png"), names, vals


def confirmation():
    tabs = md_tables(os.path.join(RESULTS, "wave4a-v4.1.0.md"))
    hdr, rows = next((h, r) for _, h, r in tabs if h[0] == "family" and "worst" in h)
    data = {}
    for r in rows:
        cells = []
        for c in r[1:10]:
            m = re.match(r"(-?[\d.]+) \(([\d.]+)\) (\d+)/(\d+)", c)
            cells.append((float(m.group(1)), float(m.group(2)), int(m.group(4))) if m else None)
        data[r[0]] = cells
    pick = [("kwdirect", "kwdirect (online)", C["blue"]), ("f1", "static F1 (tuned reference)", C["orange"]), ("dac514", "DAC (Patras)", C["aqua"]),
            ("L-pf", "PF learner", C["violet"]), ("L-global", "Global-CW learner (S2 only)", C["yellow"])]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    w = 0.16
    for k, (key, lab, col) in enumerate(pick):
        xs, ys, es = [], [], []
        for j, cell in enumerate(data[key]):
            if cell is None:
                continue
            m, sd, n = cell
            xs.append(j + (k - 2) * w); ys.append(max(m, -0.3)); es.append(t_crit(n) * sd / np.sqrt(n))
        ax.bar(xs, ys, w * 0.9, color=col, label=lab, yerr=es, error_kw={"elinewidth": 0.8, "capsize": 1.5, "ecolor": INK2})
    ax.axhline(1, color=INK2, lw=0.8, ls="--"); ax.text(-0.48, 1.03, "ceiling = 1", fontsize=7, color=INK2, ha="left")
    ax.axhline(0.95, color=C["red"], lw=0.8, ls=":"); ax.text(-0.48, 0.905, "target 0.95", fontsize=7, color=C["red"], ha="left")
    ax.set_xticks(range(9)); ax.set_xticklabels([NICE[c] for c in CELLS], rotation=35, ha="right")
    ax.set_ylim(-0.3, 1.25); ax.set_xlim(-0.5, 8.5); ax.set_ylabel("share of validated ceiling")
    ax.set_title("Wave 4a confirmation (seeds 103-122, 300 s): mean share, 95% CI")
    ax.legend(ncol=3, fontsize=7, loc="lower left", bbox_to_anchor=(0, -0.42))
    ax.text(0.0, -0.36, "bars cut at -0.3: PF and RAFA reach about -1.9 on S4 α0", transform=ax.transAxes, fontsize=7, color=INK2)
    return save(fig, "maxcw_confirmation_share.png"), data


def gatec():
    txt = open(os.path.join(RESULTS, "wave4a-v4.1.0.md"), encoding="utf8").read()
    pts = re.findall(r"- (s\w+) a(\d): ([-\d.]+) \+- ([\d.]+)", txt)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    xs = np.arange(len(pts))
    ys = [float(p[2]) for p in pts]; es = [float(p[3]) for p in pts]
    ax.bar(xs, ys, 0.6, color=C["orange"], yerr=es, error_kw={"elinewidth": 0.8, "capsize": 2, "ecolor": INK2})
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(xs); ax.set_xticklabels([NICE["%s a%s" % (p[0], p[1])] for p in pts], rotation=35, ha="right")
    ax.set_ylabel("share change"); ax.set_title("Gate C cost: kwdirect at 100 ms, 2^k-1, minus exact kwdirect (95% CI)")
    return save(fig, "maxcw_gatec_cost.png"), pts


def ceilings_table():
    tabs = md_tables(os.path.join(RESULTS, "ceilings-v4.1.0.md"))
    hdr, rows = next((h, r) for _, h, r in tabs if h[0] == "cell")
    keep = [0, 1, 2, 3, 4, 5, 6]
    return md_table([hdr[i] for i in keep], [[r[i] for i in keep] for r in rows])


if __name__ == "__main__":
    f1, names, vals = tournament()
    f2, data = confirmation()
    f3, pts = gatec()
    open(os.path.join(GEN, "maxcw_ceilings_table.md"), "w", encoding="utf8").write(ceilings_table())
    # worst-cell table from the confirmation (one row per family)
    tabs = md_tables(os.path.join(RESULTS, "wave4a-v4.1.0.md"))
    hdr, rows = next((h, r) for _, h, r in tabs if h[0] == "family" and "worst" in h)
    open(os.path.join(GEN, "maxcw_confirmation_table.md"), "w", encoding="utf8").write(md_table(hdr, rows))
    tabs = md_tables(os.path.join(RESULTS, "wave3a-v4.1.0.md"))
    hdr, rows = next((h, r) for _, h, r in tabs if h[0] == "family" and "worst" in h)
    open(os.path.join(GEN, "maxcw_tournament_table.md"), "w", encoding="utf8").write(md_table(hdr, rows))
    print("ok", f1, f2, f3)
