"""Shared helpers for the report build: markdown table parsing, plotting style, small statistics. Python 3 with numpy, scipy, matplotlib."""
import math
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))             # docs/reports/final-report-v4.1.0
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))  # repository root
RESULTS = os.path.join(REPO, "docs", "results")
FIGS = os.path.join(ROOT, "figures")
GEN = os.path.join(ROOT, "generated")
for d in (FIGS, GEN):
    os.makedirs(d, exist_ok=True)

# reference palette, light mode (dataviz skill, categorical slots 1-8, fixed order)
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100", "magenta": "#e87ba4", "green": "#008300", "violet": "#6250d6", "red": "#e34948"}
CAT = [C["blue"], C["orange"], C["aqua"], C["violet"], C["yellow"], C["magenta"], C["green"], C["red"]]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True, "figure.dpi": 100, "savefig.dpi": 200,
        "legend.frameon": False, "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
    })


style()


def save(fig, name):
    p = os.path.join(FIGS, name)
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return "figures/" + name


def md_tables(path):
    """All pipe tables of a markdown file: [(heading_or_preceding_text, header_cells, [row_cells...])]."""
    out, ctx, cur = [], "", None
    for line in open(path, encoding="utf8"):
        t = line.rstrip("\n")
        if t.strip().startswith("|"):
            cells = [c.strip() for c in t.strip().strip("|").split("|")]
            if cur is None:
                cur = [ctx, cells, []]
            elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            else:
                cur[2].append(cells)
        else:
            if cur is not None:
                out.append(tuple(cur))
                cur = None
            if t.strip():
                ctx = t.strip()
    if cur is not None:
        out.append(tuple(cur))
    return out


def num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s.replace("−", "-"))
    return float(m.group(0)) if m else float("nan")


def t_crit(n):
    """Two-sided 95% Student t critical value for n samples (n-1 dof)."""
    from scipy import stats
    return float(stats.t.ppf(0.975, max(n - 1, 1)))


def mean_ci(xs):
    import numpy as np
    xs = [x for x in xs if x == x]
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan"), 0
    m = float(np.mean(xs))
    sd = float(np.std(xs, ddof=1)) if n > 1 else 0.0
    return m, t_crit(n) * sd / math.sqrt(n) if n > 1 else 0.0, n


def jain(xs):
    s = sum(xs)
    return (s * s) / (len(xs) * sum(x * x for x in xs)) if s > 0 else 0.0


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"
