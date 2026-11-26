#!/usr/bin/env python3
"""Copies the committed figures of earlier versions that the report reuses into figures/legacy/ (so the report folder is self-contained)."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import REPO, FIGS

USE = {
    "main_20_40_aggregate.png": "docs/figures/v2.2.0/main-20-40/aggregate_throughput.png",
    "main_20_40_per_ap.png": "docs/figures/v2.2.0/main-20-40/per_ap_throughput.png",
    "main_20_40_cw_traces.png": "docs/figures/v2.2.0/main-20-40/cw_traces.png",
    "fixed60_aggregate_vs_n.png": "docs/figures/v2.2.0/fixed60-scaling/aggregate_vs_n.png",
    "fixed60_jain_vs_n.png": "docs/figures/v2.2.0/fixed60-scaling/jain_vs_n.png",
    "fixed60_min_ap_vs_n.png": "docs/figures/v2.2.0/fixed60-scaling/min_ap_vs_n.png",
    "fixed60_paired_delta_vs_n.png": "docs/figures/v2.2.0/fixed60-scaling/paired_delta_vs_n.png",
    "load_sweep.png": "docs/figures/v2.2.0/load-sweep/load_sweep.png",
    "imbalance_aggregate.png": "docs/figures/v2.2.0/imbalance/aggregate_throughput.png",
    "imbalance_per_ap.png": "docs/figures/v2.2.0/imbalance/per_ap_throughput.png",
    "hidden_chain_per_ap.png": "docs/figures/v3.4.0/per_ap_throughput.png",
    "hidden_chain_fairness.png": "docs/figures/v3.4.0/fairness.png",
}
dst = os.path.join(FIGS, "legacy")
os.makedirs(dst, exist_ok=True)
for name, src in USE.items():
    p = os.path.join(REPO, src)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(dst, name))
    else:
        print("missing", src)
print("copied", len(USE))
