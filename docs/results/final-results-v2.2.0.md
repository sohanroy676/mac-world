# v2.2.0 Final results

Status: analysis only. No new ns-3 runs, no `cw.cc` change, no rebuild. Everything here is regenerated from the existing fixed-binary run dirs (local `results/`, not committed).

## 1. Selected set and why

Fact: every v1.1.0–v1.9.0 agent run used the CW 0/0 start bug (`docs/results/robustness-v2.0.0.md` §E). Only the v2.0.0 `*-cwfix` runs (81, all PASS, n=3, seeds 0-2) ran on the fixed binary. The final set therefore uses only those. Default config: 15 s, step 0.01, 1500 steps, policy window = steps >= 300.

| # | Experiment | Source (local) | Runs | Figures |
|---|---|---|---|---|
| 1 | Main comparison, 20,40 at 150 Mbps/STA | `bench-v2.0.0-load150-cwfix` | 9 | `docs/figures/v2.2.0/main-20-40` |
| 2 | Scaling to 10 APs, fixed 60 STAs (N=2,4,6,10) | `bench-v2.0.0-fixed60-cwfix` | 36 | `fixed60` (per topology), `fixed60-scaling` (across N) |
| 3 | AP imbalance 5,55 and 5,5,5,45 | `bench-v2.0.0-imbalance-cwfix` | 18 | `imbalance` |
| 4 | Offered load 0.5 / 1 / 150 Mbps at 20,40 | `bench-v2.0.0-load0.5-cwfix`, `-load1-cwfix` (+ #1) | 18 (+9) | `load0.5`, `load1`, `load-sweep` |

Not regenerated, cited only, and labelled pre-fix (CW 0/0 start): v1.6.0 growing-STA scaling (`docs/results/scaling-v1.6.0.md`), v1.9.0 central critic (`docs/results/central-eval-v1.9.0.md`, negative result), v1.1.0 20,40 n=5 anchor.

## 2. Results (mean ± 95 % CI over 3 seeds; aggregate Mbps; paired vs BEB, same ns-3 seed)

### 2.1 Main comparison, 20,40 (#1)
| Mode | Aggregate | AP1 / AP2 | Jain | Phy loss | Paired vs BEB |
|---|---|---|---|---|---|
| BEB | 27.30 ± 0.63 | 9.48 / 17.82 | 0.913 | 0.747 | n/a |
| Global-CW | 36.29 ± 7.16 | 12.49 / 23.81 | 0.911 | 0.624 | +33.0 ± 29.0 % |
| Independent | 25.78 ± 20.80 | 9.26 / 16.52 | 0.837 | 0.765 | -5.6 ± 76.0 % |

### 2.2 Scaling at fixed 60 STAs (#2)
| N | BEB | Global | Global vs BEB | Independent | Independent vs BEB |
|---|---|---|---|---|---|
| 2 | 27.38 | 36.23 | +32.3 ± 26.3 % (3/3) | 28.44 | +3.8 ± 27.2 % |
| 4 | 27.55 | 35.64 | +29.5 ± 27.5 % (3/3) | 20.14 | -27.0 ± 21.8 % |
| 6 | 28.06 | 36.92 | +31.5 ± 18.9 % (3/3) | 18.07 | -35.8 ± 109.7 % |
| 10 | 27.89 | 36.87 | +32.2 ± 23.9 % (3/3) | 14.99 | -46.2 ± 12.2 % |

Full table (per-STA, per-AP, min per-AP, Jain, convergence): `fixed60-scaling/scaling_table.md`.

### 2.3 Imbalance (#3)
| Topology | BEB | Global | Global vs BEB | Independent | Independent vs BEB |
|---|---|---|---|---|---|
| 5,55 | 28.64 ± 3.03 | 37.07 ± 5.45 | +29.7 ± 29.5 % | 27.14 ± 11.62 | -5.4 ± 36.2 % |
| 5,5,5,45 | 27.25 ± 1.47 | 36.28 ± 8.05 | +33.2 ± 29.3 % | 22.81 ± 3.55 | -16.2 ± 17.3 % |

### 2.4 Load (#4), 20,40
| Load / STA (Mbps) | BEB | Global | Independent | Global vs BEB | Independent vs BEB |
|---|---|---|---|---|---|
| 0.5 | 27.90 ± 0.85 | 29.64 ± 1.36 | 28.86 ± 2.84 | +6.3 ± 8.0 % | +3.5 ± 13.3 % |
| 1 | 27.86 ± 1.60 | 38.96 ± 0.40 | 11.43 ± 13.75 | +39.9 ± 8.3 % | -58.8 ± 50.3 % |
| 150 | 27.30 ± 0.63 | 36.29 ± 7.16 | 25.78 ± 20.80 | +33.0 ± 29.0 % | -5.6 ± 76.0 % |

All numbers equal `docs/results/robustness-v2.0.0.md` §C and §F.2 (checked).

## 3. Observations (fact unless marked)
- Global-CW is +29.5 to +33.2 % over BEB in every fixed-binary topology at saturation, above BEB in all 3 seeds at N=2-10; the paired CI lower bounds are close to 0.
- Independent per-AP is negative from N=4 on (CI excludes 0 at N=4 and N=10); under imbalance its CI includes 0; at 1 Mbps it is much worse than BEB (-58.8 ± 50.3 %, CI excludes 0 by a small margin).
- BEB is flat in N at fixed total load (27.4-28.1 Mbps).
- Global-CW gain is neutral at 0.5 Mbps (+6 %).
- Reward (`reward.png`) is each mode's own per-AP normalized goodput and is small (~0.003-0.004), a known scale (`docs/results/core-v1.0.0.md` §5). Compare it within a figure, not as an absolute.
- Independent per-AP throughput and reward drift down late in the 20,40 run (`reward.png`, `convergence.png`); cause untested (inference only: non-stationarity of independent learners).

## 4. Artifacts per experiment (`docs/figures/v2.2.0/<exp>/`)
- `tables.md`, `manifest.csv` (run_dir, result, seconds per run).
- `per_seed.csv`: one row per run (aggregate, per-AP throughput, Jain, loss, reward, convergence, last-100 CW).
- `timeseries.csv`: per mode and step, mean over seeds (aggregate, per-AP throughput, Jain, reward, per-AP CW).
- Plots: `aggregate_throughput.png`, `per_ap_throughput.png`, `convergence.png`, `cw_traces.png`, `reward.png`, `fairness.png`.
- Across N: `fixed60-scaling/` (`scaling_table.md`, `scaling_per_seed.csv`, throughput, per-STA, per-AP, min-AP, loss, Jain, convergence, runtime, deassociation and paired-delta plots). Across load: `load-sweep/` (`load_sweep.png`, `load_table.md`).

Regenerate (from `ns-3.29/scratch/linear-mesh`, `../../venv/bin/python`, needs the local run dirs):
```
aggregate_bench.py results/bench-v2.0.0-load150-cwfix --title v2.2.0 --out ../../../docs/figures/v2.2.0/main-20-40
aggregate_bench.py results/bench-v2.0.0-fixed60-cwfix --title v2.2.0 --out ../../../docs/figures/v2.2.0/fixed60
aggregate_bench.py results/bench-v2.0.0-imbalance-cwfix --title v2.2.0 --out ../../../docs/figures/v2.2.0/imbalance
aggregate_bench.py results/bench-v2.0.0-load0.5-cwfix --title v2.2.0 --out ../../../docs/figures/v2.2.0/load0.5
aggregate_bench.py results/bench-v2.0.0-load1-cwfix --title v2.2.0 --out ../../../docs/figures/v2.2.0/load1
scaling_analysis.py --preset fixed60 --out ../../../docs/figures/v2.2.0/fixed60-scaling
load_sweep.py --out ../../../docs/figures/v2.2.0/load-sweep 0.5=<load0.5 dir> 1=<load1 dir> 150=<main-20-40 dir>
```
Checks run: `aggregate_bench.py` reproduces `docs/figures/v2.0.0/load/load150/tables.md` byte for byte; `scaling_analysis.py` default output equals `docs/figures/v1.6.0/scaling_table.md`; the fixed60 preset prints `CROSS-CHECK PASS` against the committed v2.0.0 per-topology tables.

## 5. Raw data and W&B
- Raw traces (`trace.csv`, `config.json`) and `.wandb` files stay local under `ns-3.29/scratch/linear-mesh/results/` (decision: not committed). 81 runs, about 73 MB traces + 236 MB `.wandb`; each `manifest.csv` maps topology/mode/seed to its `run_dir`.
- W&B: the runs were written as offline `.wandb` files and predate the v2.1.0 naming. Synced online on 2026-10-20 to entity `sohanroy676-vasavi-college-of-engineering`, project `contention_window` (private; 88 runs now, 81 of them these, 7 older). After the sync they were renamed `<topo> <mode> s<seed>` and tagged `multi-ap`, `final-v2.2.0`, `bench-<fixed60|imbalance|load0.5|load1|load150>`, `mode-<mode>` via the W&B API, using each `manifest.csv`. Run ids are the `run-<id>.wandb` file names.
- Sync note (fact, from the CLI debug log): with the pinned wandb 0.18.7, `wandb sync` printed `done` and wrote the `.synced` marker but created no run. Cause: the server answered the `ServerSettings` GraphQL introspection query with null and the client crashed in `upsert_run` (`'NoneType' object has no attribute 'get'`). Inference: the server no longer answers introspection (CoreWeave notes: SDK v0.26.0+ needed when introspection is disabled; not confirmed for this account). Workaround used: `ns-3.29/scratch/linear-mesh/wandb_sync_final.py` (`sync [--pilot]`, `tag`, `check`; run with the project venv and a W&B login), which, only when that probe fails, sets the client's own no-introspection fallback before running `wandb sync`; no package file or pin changed. A run counts as synced only when the API finds it afterwards (1500 history rows for the pilot run; `check` found 81/81 on 2026-10-20). The script was committed after the sync, from the session version that did the upload; its offline parts (manifest parse, patch fallback) were tested, and the user ran `check` from the committed script (81/81 found). `sync` and `tag` of the committed version were not re-run (everything was already on the server).

## 6. Limits
- n=3 per cell; most agent-vs-BEB CIs are wide and some include 0.
- Active sinks measured only at 20,40 / 150 Mbps, seed 0 (`docs/results/robustness-v2.0.0.md` §F.5): 19/20 and 39/40 in BEB, global and independent alike, so inactive STAs do not explain the agent gain there. Other topologies not measured.
- Traffic starts at t=0 (inherited); large-N association failures come from this (§G of the robustness doc) but were not seen in the final-set topologies (dry BEB check, §G.5, n=1); the final set was not rerun with `--trafficStart`.
- Central critic: excluded (negative, pre-fix binary, N=10 collapse cause untested).
- Raw data is not in git, so regeneration needs the local run dirs.
