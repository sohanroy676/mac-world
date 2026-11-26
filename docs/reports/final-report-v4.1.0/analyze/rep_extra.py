"""Part II material from the report waves: generated/exec_new.md, generated/compare_new.md, generated/build_info.md and figures/rep_heatmap.png.
Run after rep_cells.py."""
import json
import os
import subprocess
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import GEN, REPO, md_table, save, INK2  # noqa: E402
import rep_load as L  # noqa: E402

K = json.load(open(os.path.join(GEN, "keynums.json")))
CELLS = ["a1a", "a1b", "a1c", "a1d", "b2a", "b2b", "b2c", "c3a", "c3b", "c3c", "c3d", "d4a", "d4b", "d4c", "d4d", "f6s", "f6u"]
NAMES = {c: L.CELLS[c]["mentor"] for c in CELLS}
NAMES["f6s"], NAMES["f6u"] = "6S", "6U"
METH = ["bebrts", "dac514", "blade", "idlesense", "kw", "static-model", "static-prop", "static-a0", "static-a1", "kwdirect-a0", "kwdirect-a1", "L-global", "L-indep", "L-pf"]

# ---- heat map of the change against BEB
Z = np.array([[K[c][m]["d"] if m in K[c] else np.nan for m in METH] for c in CELLS])
fig, ax = plt.subplots(figsize=(7.4, 5.0))
im = ax.imshow(np.clip(Z, -80, 80), cmap="RdBu", norm=TwoSlopeNorm(vmin=-80, vcenter=0, vmax=80), aspect="auto")
ax.set_xticks(range(len(METH)))
ax.set_xticklabels([L.LABEL[m] for m in METH], rotation=45, ha="right", fontsize=7)
ax.set_yticks(range(len(CELLS)))
ax.set_yticklabels([NAMES[c] for c in CELLS], fontsize=8)
for i in range(len(CELLS)):
    for j in range(len(METH)):
        if Z[i, j] == Z[i, j]:
            ax.text(j, i, "%+.0f" % Z[i, j], ha="center", va="center", fontsize=6.5, color="white" if abs(Z[i, j]) > 45 else "#0b0b0b")
ax.grid(False)
ax.set_title("Total goodput change against BEB (%), every report cell and controller")
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cb.set_label("% (colour clipped at ±80)", fontsize=7)
save(fig, "rep_heatmap.png")

SINGLE = ["a1a", "a1b", "a1c", "a1d", "c3a", "c3b", "c3c", "c3d", "d4a", "d4b", "d4c", "d4d"]
best_cells = {c: max((m for m in METH if m in K[c]), key=lambda m: K[c][m]["d"]) for c in CELLS}

# ---- scorecard
import collections

rows = []
for m in METH:
    ds = [K[c][m]["d"] for c in CELLS if m in K[c]]
    feas = [K[c][m]["feas"] for c in CELLS if m in K[c]]
    n_better = sum(1 for c in CELLS if m in K[c] and K[c][m]["d"] > K[c][m]["dci"] and K[c][m]["d"] > 0.5)
    rows.append([L.LABEL[m], "%d / %d" % (n_better, len(ds)), "%+.1f" % np.median(ds), "%+.1f" % min(ds), "%+.1f" % max(ds), "%d %%" % round(100 * np.mean(feas))])
cnt = collections.Counter(L.LABEL[best_cells[c]] for c in CELLS)
gap = {c: K[c]["static-a1"]["d"] - K[c]["L-global"]["d"] for c in SINGLE}
cmp_txt = """### 7.4 The report cells: every controller on 17 cells

Part I ran 17 cells (scenarios 1 to 6, seeds 400 to 409; the dynamic-station cell 5 and the hidden-chain cell S4 are reported with their own metrics). The figure and the table summarise the total-goodput change of every controller against BEB. "Better" counts the cells where the change is positive, larger than 0.5 % and larger than its 95 % confidence interval. "Floor met" is the share of runs in which every AP keeps at least 95 % of the smaller of its BEB goodput and its proportional share (the fair-floor test of Part II section 2.2).

![Total goodput change against BEB for every controller and cell](figures/rep_heatmap.png){w=600}

"""
cmp_txt += "Table: Summary over the 17 report cells (total goodput change against BEB).\n"
cmp_txt += md_table(["Controller", "Cells better than BEB", "Median change (%)", "Worst (%)", "Best (%)", "Floor met"], rows)
cmp_txt += """
Reading the table:
- No single controller is best everywhere (best controller per cell: %s).
- Global-CW OSCAR is within %.1f points of the common static CW chosen for alpha 1 in the 12 single-domain cells (largest gap in cell %s); it is below it in every one of these cells (smallest gap %.1f points).
- In the hidden chain (2C) the central online search and the PF learner are the controllers that raise the starved middle BSS (%.1f and %.1f Mbit/s against %.1f for BEB), at %+.1f %% and %+.1f %% of total goodput.
- Independent per-AP OSCAR, trained for this report with a small budget (12 episodes of 15 s per agent), is below BEB in %d of the %d cells; the result does not say what a longer training would reach (limit).
- BEB with RTS/CTS is %.0f %% to %.0f %% below BEB in every cell where the load saturates the channel (all except 6U).
""" % (", ".join("%s %d" % kv for kv in cnt.most_common()), max(gap.values()), L.CELLS[max(gap, key=gap.get)]["mentor"],
       min(gap.values()), K["b2c"]["kwdirect-a1"]["per_ap"][1], K["b2c"]["L-pf"]["per_ap"][1], K["b2c"]["beb"]["per_ap"][1],
       K["b2c"]["kwdirect-a1"]["d"], K["b2c"]["L-pf"]["d"], sum(1 for c in CELLS if K[c]["L-indep"]["d"] < 0), len(CELLS),
       -max(K[c]["bebrts"]["d"] for c in CELLS if c != "f6u"), -min(K[c]["bebrts"]["d"] for c in CELLS if c != "f6u"))
open(os.path.join(GEN, "compare_new.md"), "w").write(cmp_txt)

g_one = [K[c]["L-global"]["d"] for c in SINGLE]
ind = [K[c]["L-indep"]["d"] for c in CELLS if c != "f6u"]
open(os.path.join(GEN, "exec_new.md"), "w").write(
    """- **New results in this report (Part I, seeds 400 to 409, 17 cells).** Global-CW OSCAR, one agent with one CW for all APs, improves on BEB by %+.0f %% to %+.0f %% in the 12 single-domain cells (2 to 4 APs, 20 to 100 stations, balanced or not), within %.1f points of the best static CW in each. Independent per-AP OSCAR, trained here with a small budget, is below BEB in %d of %d saturated cells. In the hidden chain (2C) no controller raises the starved middle BSS without lowering the total goodput: per-AP controllers (central online search, PF learner) raise it from %.1f to %.1f and %.1f Mbit/s at %+.1f %% and %+.1f %% of total goodput. BEB with RTS/CTS is about 30 %% below BEB in every saturated cell. Scenario 8 (uplink/downlink) and the OBSS-PD extension cannot be run in this simulator and are reported as such.
""" % (min(g_one), max(g_one), max(gap.values()), sum(1 for d_ in ind if d_ < 0), len(ind),
       K["b2c"]["beb"]["per_ap"][1], K["b2c"]["kwdirect-a1"]["per_ap"][1], K["b2c"]["L-pf"]["per_ap"][1], K["b2c"]["kwdirect-a1"]["d"], K["b2c"]["L-pf"]["d"]))

# ---- build info
try:
    commit = subprocess.check_output(["git", "-C", REPO, "rev-parse", "--short=8", "HEAD"], text=True).strip()
except Exception:
    commit = "unknown"
open(os.path.join(GEN, "build_info.md"), "w").write(
    """### 10.5 Part I data: how it was produced

- **Code:** repository commit `%s` of branch `claude/project-thread-enj71t` at the time this document was built, on top of tag v4.1.0 (`feature/v4`). The run image was built from commit `7a19099d` (adds per-run retry means and one-second series to the wave summaries); it is `ghcr.io/sohanroy676/mac-world-run@sha256:fd70bf0f764cf70345af14eac853db024c304b21f0442238588afbbd993e160a`.
- **Cells:** `.github/waves/rep/cells.json` (19 cells; 17 evaluated on seeds 400 to 409 plus the dynamic-station cell and the S4 RTS/CTS cell).
- **Stage 1 (selection and training):** wave rs1 (598 jobs, GitHub Actions run 45465177965): BEB on seeds 0 to 2 for the fair floors, the static grid of common CWs (16 to 1024) on seeds 0 to 2, and three training seeds (2000 to 2002) for each of three learners per cell, 12 episodes of 15 s (cell 5: 2 episodes of 120 s). `.github/scripts/rep_select.py` turns it into `.github/waves/rep/SEL.json` (floors, common static CWs, the Patras-model CWs).
- **Stage 2 (evaluation):** waves rs2a (run 45535003362), rs2b (run 45640242511, cancelled by GitHub after 1272 of 1289 jobs) and rs2c (the 17 lost jobs, run 45753047953): 2,577 jobs (1,288 in rs2a and 1,289 in rs2b; the 17 rerun in rs2c are among those of rs2b), BEB, BEB+RTS/CTS, DAC, BLADE, IdleSense, KW, four static CWs, the central online search at two alphas and nine frozen learner actors per cell, every one on seeds 400 to 409.
- **Rules of the study:** nothing tuned on the evaluation seeds; each cell's static CWs and floors were chosen on seeds 0 to 2; learners are evaluated frozen; compute was the project owner's own GitHub Actions only.
- **Rebuild:** `python3 .github/scripts/rep_batch.py {val,s1,s2,s2g}` regenerates the batches, `make_packs.py` the packs, `collect_wave.py` the summaries (branch `wave-collected`), and `docs/reports/final-report-v4.1.0/build.sh` the tables, figures and this document.
""" % commit)
print("ok", best_cells)
