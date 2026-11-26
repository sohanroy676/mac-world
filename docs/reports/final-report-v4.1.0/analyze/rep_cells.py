"""Tables and figures for the mentor scenarios (Part I) from the report waves rs2a + rs2b.

  python analyze/rep_cells.py rs2a.jsonl rs2b.jsonl
Writes generated/tbl_<cell>.md, generated/spread_<cell>.md, figures/rep_*.png and generated/keynums.json (numbers the narrative quotes).
"""
import json
import math
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import C, CAT, GEN, INK2, md_table, save, mean_ci  # noqa: E402
import rep_load as L  # noqa: E402

runs = L.load(sys.argv[1:])
KEY = {}

FIG_METHODS = ["bebrts", "dac514", "kw", "kwdirect-a1", "L-global", "L-indep", "L-pf"]
FIG_COL = {"bebrts": C["yellow"], "dac514": C["aqua"], "kw": C["violet"], "kwdirect-a1": C["blue"], "L-global": C["orange"],
           "L-indep": C["red"], "L-pf": C["magenta"]}
SHORT = {"bebrts": "BEB+RTS", "dac514": "DAC", "kw": "KW", "kwdirect-a1": "Central search", "L-global": "Global-CW OSCAR",
         "L-indep": "Independent OSCAR", "L-pf": "PF learner"}


def f(x, d=2):
    return "n/a" if x is None or x != x else f"{x:.{d}f}"


def pm(t, d=2):
    return "n/a" if t is None else f"{t[0]:.{d}f} ± {t[1]:.{d}f}"


def cell_table(cell, name=None):
    counts = L.cell_counts(cell)
    S = L.summarize(runs, cell, counts)
    rows = []
    for m in L.ORDER:
        if m not in S:
            continue
        o = S[m]
        d = o["d_total_pct"]
        rows.append([L.LABEL[m], pm(o["total"], 1), "–" if m == "beb" else ("%+.1f ± %.1f" % (d[0], d[1]) if d else "n/a"),
                     " / ".join(f(v, 1) for v in o["per_ap"]), f(o["jain"][0], 3), f(o["min_sta"][0], 2),
                     "%d%%" % round(100 * o["feas"]), f(o["loss"][0], 2), str(o["n"])])
    hdr = ["Controller", "Total goodput (Mbit/s)", "Δ vs BEB (%)", "Per AP (Mbit/s)", "Jain (per station)", "Worst station (Mbit/s)",
           "Floor met", "PHY loss", "Seeds"]
    txt = "Table: %s, stations per AP %s. Goodput in the second half of each 60 s run, mean ± 95%% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).\n" % (
        name or cell, ",".join(map(str, counts)))
    txt += md_table(hdr, rows)
    open(os.path.join(GEN, "tbl_%s.md" % cell), "w").write(txt)
    # spread across training seeds
    sp = []
    for m in ("L-global", "L-indep", "L-pf"):
        d = runs[cell].get(m, {})
        if not d:
            continue
        per_t = {}
        for seed, byt in d.items():
            for t, r in byt.items():
                per_t.setdefault(t, []).append(sum(r["thr_half2"]))
        means = [np.mean(v) for v in per_t.values()]
        sp.append([L.LABEL[m]] + ["%.1f" % x for x in sorted(means)] + ["%.2f" % (max(means) - min(means))])
        KEY.setdefault("spread", {}).setdefault(cell, {})[m] = float(max(means) - min(means))
    if sp:
        open(os.path.join(GEN, "spread_%s.md" % cell), "w").write(
            "Table: %s: mean total goodput (Mbit/s) of each of the three independently trained learners (training seeds 2000, 2001, 2002), and the largest gap.\n" % (name or cell)
            + md_table(["Learner", "Trained 2000", "Trained 2001", "Trained 2002", "Gap"], sp))
    KEY[cell] = {m: {"total": S[m]["total"][0], "d": (S[m]["d_total_pct"][0] if S[m]["d_total_pct"] else 0.0),
                     "dci": (S[m]["d_total_pct"][1] if S[m]["d_total_pct"] else 0.0), "jain": S[m]["jain"][0],
                     "feas": S[m]["feas"], "loss": S[m]["loss"][0], "retry": S[m]["retry"][0], "cw": S[m]["cw"], "per_ap": S[m]["per_ap"], "n": S[m]["n"],
                     "min_sta": S[m]["min_sta"][0]} for m in S}
    return S


def group_bars(cells, labels, fname, title, ylabel="Goodput change vs BEB (%)"):
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    w = 0.8 / len(FIG_METHODS)
    for k, m in enumerate(FIG_METHODS):
        ys, es = [], []
        for c in cells:
            S = SUMS[c]
            if m in S and S[m]["d_total_pct"]:
                ys.append(S[m]["d_total_pct"][0]); es.append(S[m]["d_total_pct"][1])
            else:
                ys.append(np.nan); es.append(0)
        x = np.arange(len(cells)) + (k - (len(FIG_METHODS) - 1) / 2) * w
        ax.bar(x, ys, w * 0.92, yerr=es, color=FIG_COL[m], label=SHORT[m], error_kw={"lw": 0.8, "ecolor": INK2}, zorder=3)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(range(len(cells)))
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(ncol=4, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    return save(fig, fname)


SUMS = {}
for cell in L.CELLS:
    if cell in runs and runs[cell] and cell not in ("e5", "g7s4"):
        SUMS[cell] = cell_table(cell, "cell " + cell + " (mentor %s)" % L.CELLS[cell]["mentor"])

figs = {}
if all(c in SUMS for c in ("a1a", "a1b", "a1c", "a1d")):
    figs["f1"] = group_bars(["a1a", "a1b", "a1c", "a1d"], ["1A 10+10", "1B 15+15", "1C 20+20", "1D 25+25"], "rep_s1_bars.png",
                            "Scenario 1: goodput change vs BEB, two fully overlapping APs")
if all(c in SUMS for c in ("c3a", "c3b", "c3c", "c3d")):
    figs["f3"] = group_bars(["c3a", "c3b", "c3c", "c3d"], ["3A 3x10", "3B 3x20", "3C 4x10", "3D 4x20"], "rep_s3_bars.png",
                            "Scenario 3: goodput change vs BEB, three and four APs")
if all(c in SUMS for c in ("d4a", "d4b", "d4c", "d4d")):
    figs["f4"] = group_bars(["d4a", "d4b", "d4c", "d4d"], ["4A 10x4", "4B 10-40", "4C 5-35", "4D 40-5"], "rep_s4_bars.png",
                            "Scenario 4: goodput change vs BEB, unequal station counts")
if all(c in SUMS for c in ("b2a", "b2b", "b2c")):
    figs["f2"] = group_bars(["b2a", "b2b", "b2c"], ["2A", "2B", "2C"], "rep_s2_bars.png", "Scenario 2: goodput change vs BEB, partial overlap (hidden pairs)")

# scenario 4: CW chosen per AP against the AP's station count
if all(c in SUMS for c in ("d4b", "d4c", "d4d")):
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.9), sharey=True)
    for ax, c, t in zip(axs, ("d4b", "d4c", "d4d"), ("4B", "4C", "4D")):
        n = L.cell_counts(c)
        for m, col in (("dac514", C["aqua"]), ("kw", C["violet"]), ("kwdirect-a1", C["blue"]), ("L-global", C["orange"]),
                       ("L-indep", C["red"]), ("L-pf", C["magenta"])):
            cw = SUMS[c].get(m, {}).get("cw")
            if cw:
                ax.plot(n, cw, "o-", color=col, label=SHORT.get(m, m), lw=1.4, ms=4)
        ax.set_yscale("log"); ax.set_title(t); ax.set_xlabel("stations of the AP")
        ax.set_xticks(n)
    axs[0].set_ylabel("mean CW (slots)")
    h, lb = axs[0].get_legend_handles_labels()
    fig.legend(h, lb, ncol=6, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, -0.2))
    figs["f4cw"] = save(fig, "rep_s4_cw.png")

# per-AP goodput per station (fairness) for 4B
if "d4b" in SUMS:
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    n = L.cell_counts("d4b")
    meths = ["beb", "dac514", "kw", "kwdirect-a1", "L-global", "L-pf"]
    cols = {"beb": INK2, "dac514": C["aqua"], "kw": C["violet"], "kwdirect-a1": C["blue"], "L-global": C["orange"], "L-pf": C["magenta"]}
    w = 0.8 / len(meths)
    for k, m in enumerate(meths):
        if m in SUMS["d4b"]:
            ps = [x / nn for x, nn in zip(SUMS["d4b"][m]["per_ap"], n)]
            ax.bar(np.arange(4) + (k - (len(meths) - 1) / 2) * w, ps, w * 0.92, color=cols[m], label=SHORT.get(m, "BEB"), zorder=3)
    ax.set_xticks(range(4)); ax.set_xticklabels(["AP1 (10 STAs)", "AP2 (20)", "AP3 (30)", "AP4 (40)"])
    ax.set_ylabel("goodput per station (Mbit/s)"); ax.set_title("Scenario 4B: per-station goodput of each BSS")
    ax.legend(ncol=3, fontsize=7)
    figs["f4fair"] = save(fig, "rep_s4b_perSTA.png")

# scenario 3: CW of the global actor vs APs/stations
if all(c in SUMS for c in ("c3a", "c3b", "c3c", "c3d")):
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    labs = ["3A 3x10", "3B 3x20", "3C 4x10", "3D 4x20"]
    for m, col in (("L-global", C["orange"]), ("L-pf", C["magenta"]), ("kwdirect-a1", C["blue"]), ("kw", C["violet"]), ("dac514", C["aqua"])):
        ys = [np.mean(SUMS[c][m]["cw"]) if m in SUMS[c] and SUMS[c][m]["cw"] else np.nan for c in ("c3a", "c3b", "c3c", "c3d")]
        ax.plot(range(4), ys, "o-", color=col, label=SHORT.get(m, m), lw=1.4, ms=4)
    ax.set_xticks(range(4)); ax.set_xticklabels(labs); ax.set_yscale("log"); ax.set_ylabel("mean CW (slots)")
    ax.set_title("Scenario 3: CW chosen as density grows"); ax.legend(fontsize=7)
    figs["f3cw"] = save(fig, "rep_s3_cw.png")

# ---------------- scenario 5: dynamic stations (cell e5) ----------------
if "e5" in runs and runs["e5"]:
    ph = L.CELLS["e5"]["phases"]
    ser = {}
    for m in L.ORDER:
        rec = L.seed_records(runs, "e5", m)
        arr = []
        for s, r in rec.items():
            if r.get("series_thr"):
                t = np.array(json.loads(r["series_thr"]) if isinstance(r["series_thr"], str) else r["series_thr"], float)
                c_ = np.array(json.loads(r["series_cw"]) if isinstance(r.get("series_cw"), str) else r.get("series_cw") or [], float)
                rt = np.array(json.loads(r["series_retry"]) if isinstance(r.get("series_retry"), str) else r.get("series_retry") or [], float)
                arr.append((t, c_, rt))
        if arr:
            ser[m] = arr
    KEY["e5_methods"] = sorted(ser)
    if ser:
        def tot(a):
            return np.sum(a[0], axis=0)
        rows, pm_rows = [], []
        T = min(len(tot(a)) for arrs in ser.values() for a in arrs)
        for m, arrs in ser.items():
            thr_t = np.mean([tot(a)[:T] for a in arrs], axis=0)
            cw_t = np.mean([np.mean(a[1], axis=0)[:T] for a in arrs], axis=0) if arrs[0][1].size else None
            rt_t = np.mean([np.mean(a[2], axis=0)[:T] for a in arrs], axis=0) if arrs[0][2].size else None
            ser[m] = (thr_t, cw_t, rt_t, len(arrs))
        # phase metrics
        for m, (thr_t, cw_t, rt_t, n) in ser.items():
            dips, recs, stabs, means, rets, dips_arr, dips_dep = [], [], [], [], [], [], []
            for k, (a, b, n_sta) in enumerate(ph):
                seg = thr_t[a:b]
                steady = np.mean(seg[len(seg) // 2:])
                means.append(np.mean(seg))
                if k > 0:
                    prev = np.mean(thr_t[ph[k - 1][0] + (ph[k - 1][1] - ph[k - 1][0]) // 2:ph[k - 1][1]])
                    dd = 100.0 * (min(seg[:5]) / prev - 1)
                    dips.append(dd)
                    (dips_arr if ph[k][2] > ph[k - 1][2] else dips_dep).append(dd)
                    ok = [i for i in range(len(seg)) if abs(seg[i] / steady - 1) <= 0.05 and all(abs(seg[j] / steady - 1) <= 0.05 for j in range(i, min(len(seg), i + 3)))]
                    recs.append(ok[0] if ok else float("nan"))
                    if cw_t is not None:
                        cseg = cw_t[a:b]
                        cst = np.mean(cseg[len(cseg) // 2:])
                        okc = [i for i in range(len(cseg)) if abs(cseg[i] / cst - 1) <= 0.10 and all(abs(cseg[j] / cst - 1) <= 0.10 for j in range(i, min(len(cseg), i + 3)))]
                        stabs.append(okc[0] if okc else float("nan"))
                if rt_t is not None:
                    rets.append(np.mean(rt_t[a:b]))
            pm_rows.append([L.LABEL[m], "%.1f" % np.mean(thr_t), "%.1f" % np.nanmean(dips_arr), "%.1f" % np.nanmean(dips_dep), "%.1f" % np.nanmean(recs),
                            ("%.1f" % np.nanmean(stabs)) if stabs else "n/a", ("%.3f" % np.mean(rets)) if rets else "n/a", str(n)])
            KEY.setdefault("e5", {})[m] = {"mean": float(np.mean(thr_t)), "dip_arr": float(np.nanmean(dips_arr)), "dip_dep": float(np.nanmean(dips_dep)), "rec": float(np.nanmean(recs)),
                                           "stab": (float(np.nanmean(stabs)) if stabs else None), "retry": (float(np.mean(rets)) if rets else None),
                                           "phase_means": [float(x) for x in means]}
        open(os.path.join(GEN, "tbl_e5_phase.md"), "w").write(
            "Table: Scenario 5, adaptation metrics over the six phases (active stations per AP 10, 15, 20, 25, 15, 10; 20 s each). Dip = lowest 1 s goodput in the first 5 s after a change, relative to the previous phase's level (three joining steps, two leaving steps); recovery = seconds until goodput stays within 5% of the phase's second-half level; CW settling = seconds until the mean CW stays within 10% of its second-half level. Means over the five transitions and over evaluation seeds.\n"
            + md_table(["Controller", "Mean goodput (Mbit/s)", "Dip when stations join (%)", "Dip when stations leave (%)", "Recovery (s)", "CW settling (s)", "Retry rate", "Runs"], pm_rows))
        pmeans = [["%s" % L.LABEL[m]] + ["%.1f" % v for v in KEY["e5"][m]["phase_means"]] for m in ser]
        open(os.path.join(GEN, "tbl_e5_means.md"), "w").write(
            "Table: Scenario 5, mean total goodput (Mbit/s) in each phase.\n"
            + md_table(["Controller"] + ["P%d (%d STAs)" % (i + 1, ph[i][2]) for i in range(6)], pmeans))
        # figure: goodput and CW over time
        fig, axs = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True)
        show = [("beb", INK2), ("kw", C["violet"]), ("dac514", C["aqua"]), ("kwdirect-a1", C["blue"]), ("L-global", C["orange"]), ("L-pf", C["magenta"])]
        for m, col in show:
            if m in ser:
                thr_t, cw_t, rt_t, n = ser[m]
                axs[0].plot(np.arange(len(thr_t)) + 0.5, thr_t, color=col, lw=1.1, label=SHORT.get(m, "BEB"))
                if cw_t is not None:
                    axs[1].plot(np.arange(len(cw_t)) + 0.5, cw_t, color=col, lw=1.1)
        for ax in axs:
            for a, b, nn in ph:
                ax.axvline(a, color=GRID if False else "#c9c8c3", lw=0.7)
        for a, b, nn in ph:
            axs[0].text((a + b) / 2, axs[0].get_ylim()[1], "%d STAs" % nn, ha="center", va="bottom", fontsize=7, color=INK2)
        axs[0].set_ylabel("total goodput (Mbit/s)"); axs[1].set_ylabel("mean CW (slots)"); axs[1].set_yscale("log"); axs[1].set_xlabel("time (s)")
        axs[0].legend(ncol=3, fontsize=7, loc="lower left")
        fig.suptitle("Scenario 5: 3 APs, active stations per AP stepped 10 → 25 → 10", x=0.01, ha="left", fontsize=10, fontweight="bold", y=1.0)
        figs["f5"] = save(fig, "rep_s5_time.png")

# ---------------- scenario 6: delay ----------------
for cell in ("f6s", "f6u", "b2c", "g7s4"):
    if cell not in runs or not runs[cell]:
        continue
    counts = L.cell_counts(cell)
    rows = []
    for m in L.ORDER:
        rec = L.seed_records(runs, cell, m)
        dl = [r["delay"] for r in rec.values() if r.get("delay")]
        if not dl:
            continue
        # delay lines: [ap, n, mean, p50, p99] in milliseconds
        arr = np.array(dl, float)  # seeds x AP x 5
        mean_ms = np.mean(arr[:, :, 2], axis=0)
        p99_ms = np.mean(arr[:, :, 4], axis=0)
        loads = np.mean([r["thr_half2"] for r in rec.values()], axis=0)
        rows.append([L.LABEL[m], " / ".join("%.2f" % v for v in loads), " / ".join("%.1f" % v for v in mean_ms), " / ".join("%.1f" % v for v in p99_ms), str(len(rec))])
        KEY.setdefault(cell + "_delay", {})[m] = {"mean_ms": mean_ms.tolist(), "p99_ms": p99_ms.tolist(), "thr": loads.tolist()}
    note = {"f6s": "offered 50 / 100 / 150 / 200 Mbit/s for AP1 / AP2 / AP3 / AP4 (saturated)",
            "f6u": "offered 2.5 / 5 / 7.5 / 10 Mbit/s for AP1 / AP2 / AP3 / AP4 (unsaturated, total 25 Mbit/s)",
            "b2c": "cell 2C, 15 stations per AP, AP1 and AP3 cannot hear each other (AP1 / AP2 / AP3)",
            "g7s4": "project scenario S4, 10 stations per AP, AP1 and AP3 cannot hear each other (AP1 / AP2 / AP3)"}[cell]
    open(os.path.join(GEN, "tbl_%s_delay.md" % cell), "w").write(
        "Table: %s: goodput and MAC delay per AP. Delay is the time from enqueue to acknowledged delivery, mean and 99th percentile, in ms; mean over seeds.\n" % note
        + md_table(["Controller", "Goodput (Mbit/s)", "Mean delay (ms)", "p99 delay (ms)", "Seeds"], rows))

# ---------------- scenario 7: hidden nodes, RTS/CTS (g7s4, b2*) ----------------
if "g7s4" in runs and runs["g7s4"]:
    cell_table("g7s4", "cell g7s4 (project S4, hidden chain)")
    S = L.summarize(runs, "g7s4", L.cell_counts("g7s4"))
    KEY["g7s4"] = {m: {"total": S[m]["total"][0], "d": (S[m]["d_total_pct"][0] if S[m]["d_total_pct"] else 0.0), "jain": S[m]["jain"][0],
                       "loss": S[m]["loss"][0], "retry": S[m]["retry"][0], "min_sta": S[m]["min_sta"][0], "per_ap": S[m]["per_ap"]} for m in S}

# RTS/CTS impact across cells
rt = []
for cell, lab in (("a1a", "1A, 2 APs, one domain"), ("c3a", "3A, 3 APs, one domain"), ("b2a", "2A, hidden AP3"), ("b2b", "2B, hidden AP1"),
                  ("b2c", "2C, hidden chain"), ("g7s4", "S4, hidden chain")):
    if cell not in runs:
        continue
    S_ = L.summarize(runs, cell, L.cell_counts(cell))
    if "beb" not in S_ or "bebrts" not in S_:
        continue
    a, b = S_["beb"], S_["bebrts"]
    rt.append([lab, f(a["total"][0], 1), f(b["total"][0], 1), "%+.1f" % b["d_total_pct"][0], f(a["jain"][0], 2), f(b["jain"][0], 2),
               f(a["min_sta"][0], 2), f(b["min_sta"][0], 2), f(a["loss"][0], 2), f(b["loss"][0], 2), f(a["retry"][0], 2), f(b["retry"][0], 2)])
    KEY.setdefault("rts", {})[cell] = {"beb": a["total"][0], "rts": b["total"][0], "d": b["d_total_pct"][0]}
open(os.path.join(GEN, "tbl_rts_impact.md"), "w").write(
    "Table: Effect of RTS/CTS (BEB without and with the RTS/CTS handshake), goodput in Mbit/s, mean over evaluation seeds 400-409.\n"
    + md_table(["Cell", "Total, no RTS", "Total, RTS", "Change (%)", "Jain no RTS", "Jain RTS", "Worst STA no RTS", "Worst STA RTS", "PHY loss no RTS", "PHY loss RTS", "Retry no RTS", "Retry RTS"], rt))

json.dump(KEY, open(os.path.join(GEN, "keynums.json"), "w"), indent=1, default=float)
print("figures:", figs)
print("cells:", sorted(SUMS))
