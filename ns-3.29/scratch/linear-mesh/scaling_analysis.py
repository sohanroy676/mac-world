"""v1.6.0: cross-N scaling analysis (2 -> 10 APs) recomputed from the raw per-run traces of v1.1.0..v1.5.0.
Usage (from this directory):
  ../../venv/bin/python scaling_analysis.py [--preset v1.6.0|fixed60] [--out ../../../docs/figures/v1.6.0] [--stepTime 0.01] [--warmup 300]
v2.2.0: --preset fixed60 = fixed total 60 STAs, N=2,4,6,10 (bench-v2.0.0-fixed60-cwfix, fixed binary); default keeps v1.6.0.
Same policy window and throughput definition as aggregate_bench.py (via summarize_run.summarize).
Cross-check: each N's aggregate mean must equal the committed per-version tables.md (2 dp).
"""
import argparse
import csv
import os
import re
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from summarize_run import summarize  # noqa: E402

# (N APs, topo string as in the manifest, bench dir, committed tables.md for the cross-check)
DATASETS_V160 = [
    (2, "20,40", "results/bench-v1.1.0", "../../../docs/figures/v1.1.0-b5/tables.md"),
    (4, "5,10,15,20", "results/bench-v1.2.0", "../../../docs/figures/v1.2.0-b2/tables.md"),
    (6, "5,10,15,20,25,30", "results/bench-v1.3.0", "../../../docs/figures/v1.3.0-b2/tables.md"),
    (8, "5,10,15,20,25,30,35,40", "results/bench-v1.4.0", "../../../docs/figures/v1.4.0/tables.md"),
    (10, "4,8,12,16,20,24,28,32,36,40", "results/bench-v1.5.0", "../../../docs/figures/v1.5.0/tables.md"),
]
_F60 = "../../../docs/figures/v2.0.0/fixed60-cwfix/%s/tables.md"
DATASETS_FIXED60 = [(n, t, "results/bench-v2.0.0-fixed60-cwfix", _F60 % t) for n, t in [
    (2, "30,30"), (4, "15,15,15,15"), (6, "10,10,10,10,10,10"), (10, "6,6,6,6,6,6,6,6,6,6")]]

# same as aggregate_bench.py
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MODES = ["beb", "global", "independent"]
LABEL = {"beb": "BEB (802.11)", "global": "Global-CW OSCAR", "independent": "Independent per-AP"}
COLOR = {"beb": "#888888", "global": "#d95f02", "independent": "#1b9e77"}

parser = argparse.ArgumentParser()
parser.add_argument("--preset", choices=["v1.6.0", "fixed60"], default="v1.6.0")
parser.add_argument("--out", default="../../../docs/figures/v1.6.0")
parser.add_argument("--stepTime", type=float, default=0.01)
parser.add_argument("--warmup", type=int, default=300)
args = parser.parse_args()
DATASETS = DATASETS_FIXED60 if args.preset == "fixed60" else DATASETS_V160
TITLE = ("v2.2.0 fixed-60-STA scaling table" if args.preset == "fixed60" else "v1.6.0 scaling table")
NOTE = ("Total STAs fixed at 60, equal split." if args.preset == "fixed60" else "N=2 uses 20,40 (n=5), others n=3.")


def ci(x):
    """(mean, half-width of the 95% CI). Half-width is nan for n < 2."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return float(x.mean()), float("nan")
    assert len(x) - 1 in T95, "need n <= 11 seeds"
    return float(x.mean()), T95[len(x) - 1] * float(x.std(ddof=1)) / np.sqrt(len(x))


def fmt(x, d=2):
    m, h = ci(x)
    return "%.*f ± %.*f" % (d, m, d, h) if np.isfinite(h) else "%.*f (n=1)" % (d, m)


def convergence_step(tot, win=100, tol=0.05, tail=300):
    roll = np.convolve(tot, np.ones(win) / win, mode="valid")
    ref = tot[-tail:].mean()
    bad = np.where(np.abs(roll - ref) > tol * ref)[0]
    return int(bad[-1] + win) if len(bad) else 0


def deassoc_counts(log):
    """(all deassoc events, events at t=1.144 s) from a run log; (nan, nan) if the log is missing."""
    if not os.path.exists(log):
        return float("nan"), float("nan")
    n = n144 = 0
    for line in open(log, errors="replace"):
        m = re.search(r"deassociated from \S+ at t=([0-9.]+)s", line)
        if m:
            n += 1
            n144 += abs(float(m.group(1)) - 1.144) < 1e-3
    return n, n144


rows = []  # per-run records
for n_ap, topo, bench, _ in DATASETS:
    stas = sum(int(x) for x in topo.split(","))
    for r in csv.DictReader(open(os.path.join(bench, "manifest.csv"))):
        if r["topo"] != topo or r["result"] != "PASS":
            continue
        s = summarize(r["run_dir"], args.stepTime, args.warmup)
        assert len(s["aps"]) == n_ap, (topo, r["run_dir"])
        d, d144 = deassoc_counts(os.path.join(bench, "%s-%s-s%s.log" % (topo, r["mode"], r["seed"])))
        thr = list(s["thr_policy"].values())
        rows.append(dict(
            n_ap=n_ap, stas=stas, mode=r["mode"], seed=int(r["seed"]), agg=s["tot_policy"], per_sta=s["tot_policy"] / stas,
            mean_ap=float(np.mean(thr)), min_ap=float(np.min(thr)), loss=s["loss_policy"], jain=s["jain_policy"],
            conv=convergence_step(s["tot"]), seconds=float(r["seconds"]), deassoc=d, deassoc_1144=d144))

os.makedirs(args.out, exist_ok=True)
with open(os.path.join(args.out, "scaling_per_seed.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

sel = lambda n, m, k: [r[k] for r in rows if r["n_ap"] == n and r["mode"] == m]
Ns = [d[0] for d in DATASETS]
STAS = {d[0]: sum(int(x) for x in d[1].split(",")) for d in DATASETS}

# --- cross-check against committed per-version tables ----------------------------------------------------------
print("Cross-check vs committed tables.md (aggregate mean, 2 dp):")
ok_all = True
for n_ap, topo, _, tbl in DATASETS:
    txt = open(tbl).read()
    sec = txt.split("## %s STAs per AP" % topo)[1].split("\n## ")[0]
    for m in MODES:
        mm = re.search(r"\| %s \| (\d+) \| ([0-9.]+) ±" % re.escape(LABEL[m]), sec)
        mean, _ = ci(sel(n_ap, m, "agg"))
        ok = bool(mm) and int(mm.group(1)) == len(sel(n_ap, m, "agg")) and abs(float(mm.group(2)) - mean) < 0.006
        ok_all &= ok
        print("  N=%-2d %-12s n=%d recomputed %.2f table %s -> %s" % (
            n_ap, m, len(sel(n_ap, m, "agg")), mean, mm.group(2) if mm else "?", "PASS" if ok else "FAIL"))
print("CROSS-CHECK", "PASS" if ok_all else "FAIL")

# --- table -----------------------------------------------------------------------------------------------------
md = ["# %s (generated by scaling_analysis.py)" % TITLE, "",
      "Policy window = steps >= %d; mean ± 95%% CI (Student t) over seeds. %s" % (args.warmup, NOTE), "",
      "| N APs | STAs | Mode | n | Aggregate Mbps | per-STA kbps | mean per-AP Mbps | min per-AP Mbps | Phy loss | Jain "
      "| Convergence step | Run time s | Deassoc events | Deassoc @1.144 s |", "|" + "---|" * 14]
for n in Ns:
    for m in MODES:
        if not sel(n, m, "agg"):
            continue
        md.append("| %d | %d | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            n, STAS[n], LABEL[m], len(sel(n, m, "agg")), fmt(sel(n, m, "agg")),
            fmt([x * 1000 for x in sel(n, m, "per_sta")], 1), fmt(sel(n, m, "mean_ap")), fmt(sel(n, m, "min_ap")),
            fmt(sel(n, m, "loss"), 3), fmt(sel(n, m, "jain"), 3), fmt(sel(n, m, "conv"), 0),
            fmt(sel(n, m, "seconds"), 0), fmt(sel(n, m, "deassoc"), 1), fmt(sel(n, m, "deassoc_1144"), 1)))
md += ["", "Paired difference vs BEB (same ns-3 seed), aggregate throughput:", "",
       "| N APs | Mode | n pairs | Δ Mbps | Δ % | above BEB |", "|---|---|---|---|---|---|"]
paired = {}  # (n, m) -> (mean pct, half-width pct)
for n in Ns:
    beb = {r["seed"]: r["agg"] for r in rows if r["n_ap"] == n and r["mode"] == "beb"}
    for m in ["global", "independent"]:
        cur = {r["seed"]: r["agg"] for r in rows if r["n_ap"] == n and r["mode"] == m}
        seeds = sorted(set(cur) & set(beb))
        d = [cur[s] - beb[s] for s in seeds]
        p = [100 * (cur[s] - beb[s]) / beb[s] for s in seeds]
        paired[(n, m)] = ci(p)
        md.append("| %d | %s | %d | %s | %s | %d/%d |" % (n, LABEL[m], len(seeds), fmt(d), fmt(p, 1), sum(x > 0 for x in d), len(d)))
with open(os.path.join(args.out, "scaling_table.md"), "w") as f:
    f.write("\n".join(md) + "\n")
print("\n".join(md))


# --- figures ---------------------------------------------------------------------------------------------------
def line_plot(key, ylabel, fname, scale=1.0, modes=MODES):
    fig, ax = plt.subplots(figsize=(7, 4))
    for m in modes:
        ms, hs = zip(*[ci([x * scale for x in sel(n, m, key)]) for n in Ns])
        ax.errorbar(Ns, ms, yerr=np.nan_to_num(hs), marker="o", capsize=3, label=LABEL[m], color=COLOR[m])
    ax.set_xticks(Ns)
    ax.set_xticklabels(["%d\n(%d STAs)" % (n, STAS[n]) for n in Ns])
    ax.set_xlabel("AP count (total STAs)")
    ax.set_ylabel(ylabel)
    ax.set_title(ylabel + " (mean ± 95% CI)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, fname), dpi=150)
    plt.close(fig)


line_plot("agg", "Aggregate throughput, policy window (Mbps)", "aggregate_vs_n.png")
line_plot("per_sta", "Per-STA throughput (kbps)", "per_sta_vs_n.png", 1000)
line_plot("mean_ap", "Mean per-AP throughput (Mbps)", "per_ap_vs_n.png")
line_plot("min_ap", "Minimum per-AP throughput (Mbps)", "min_ap_vs_n.png")
line_plot("loss", "Phy loss ratio, policy window", "loss_vs_n.png")
line_plot("jain", "Jain fairness over per-AP throughput", "jain_vs_n.png")
line_plot("conv", "Convergence step (aggregate throughput)", "convergence_vs_n.png")
line_plot("seconds", "Run time per 1500-step run (s)", "runtime_vs_n.png")
line_plot("deassoc", "STA deassociation events per run", "deassoc_vs_n.png")

fig, ax = plt.subplots(figsize=(7, 4))
for m in ["global", "independent"]:
    ms, hs = zip(*[paired[(n, m)] for n in Ns])
    ax.errorbar(Ns, ms, yerr=np.nan_to_num(hs), marker="o", capsize=3, label=LABEL[m], color=COLOR[m])
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(Ns)
ax.set_xticklabels(["%d\n(%d STAs)" % (n, STAS[n]) for n in Ns])
ax.set_xlabel("AP count (total STAs)")
ax.set_ylabel("Paired Δ vs BEB (%)")
ax.set_title("Paired aggregate throughput difference vs BEB (mean ± 95% CI)")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(args.out, "paired_delta_vs_n.png"), dpi=150)
plt.close(fig)
print("wrote", args.out)
