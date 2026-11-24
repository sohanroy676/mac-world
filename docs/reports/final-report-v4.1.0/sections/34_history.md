## 4. Project history and the early two-AP to ten-AP studies

### 4.1 Versions
| Versions | Dates (2026) | What was done |
|---|---|---|
| v0.1.0 to v0.2.0 | Sep 16 | Baseline OSCAR frozen and audited against the paper; multi-AP design contract (one ns-3 process, one DDPG agent per AP, strict isolation) |
| v0.3.0 to v0.9.0 | Oct 7 to 8 | Two-AP topology, per-AP statistics, per-AP CW, multi-AP ns3-gym, independent agents, Weights & Biases logging, validation tests |
| v1.0.0 | Oct 8 | Core milestone: independent per-AP agents trained and compared with BEB at 2 APs |
| v1.1.0 to v1.6.0 | Oct 15 to 16 | Benchmarks (BEB, Global-CW OSCAR, independent) and scaling from 2 to 10 APs; a seed bug (`--seed` had no effect on ns-3) found and fixed in v1.1.0 |
| v1.7.0 to v1.9.0 | Oct 16 to 17 | Central-critic design, prototype and small evaluation (negative result at 10 APs) |
| v2.0.0 to v2.5.0 | Oct 19 | Robustness batches, fix of the CW 0/0 start bug, reproducibility, final results, technical report, presentation, audit |
| v3.0.0 to v3.4.0 | Oct 26 to 31 | Attempts to beat Global-CW with per-AP agents; static ceilings; fair evaluation protocol; sensing heuristics; the hidden-chain scenario with a fairness reward |
| v3.5.0 to v3.7.0 (M0 to M2) | Nov 1 to 5 | Foundations (traces, loads, per-episode scenarios), oracle grids and gap-closed tables, new baselines (KW, UCB, CCOD, BEB with RTS/CTS) |
| v4.0.0 (M3) | Nov 8 to 10 | RAFA (shared actor) on GitHub Actions; pooled RAFA failed gate G3, so RAFA became per-scenario |
| v4.0.0 (M2b, M2c) | Nov 11 to 13 | Re-implemented DAC, drlCW, BLADE, contextual UCB, model-based static; CPU-retrained Global, PF and CCOD learners |
| v4.1.0 | Nov 14 to 24 | Max-CW study: measurement modes, ceilings, central online controllers, tournament and 760-run confirmation |

### 4.2 Two-AP comparison, 20 and 40 stations (fixed binary, 3 seeds)
The first comparison runs the three controllers of the early study on 20 and 40 saturated stations for 15 s per run (policy window after 3 s). Means with 95 % confidence intervals over 3 seeds:

Table: BEB, Global-CW OSCAR and independent per-AP OSCAR at 20 and 40 stations, 150 Mbps per station (v2.0.0 fixed-binary runs)
| Controller | Aggregate (Mbps) | AP1 / AP2 (Mbps) | Jain | PHY loss | Paired vs BEB |
|---|---|---|---|---|---|
| BEB | 27.30 ± 0.63 | 9.48 / 17.82 | 0.913 | 0.747 | n/a |
| Global-CW OSCAR | 36.29 ± 7.16 | 12.49 / 23.81 | 0.911 | 0.624 | +33.0 ± 29.0 % |
| Independent per-AP OSCAR | 25.78 ± 20.80 | 9.26 / 16.52 | 0.837 | 0.765 | -5.6 ± 76.0 % |

![Aggregate goodput of BEB, Global-CW OSCAR and independent per-AP OSCAR at 20 and 40 stations (3 seeds).](figures/legacy/main_20_40_aggregate.png){w=470}

![Goodput of each AP (20 and 40 stations): the Global-CW agent raises both BSSs.](figures/legacy/main_20_40_per_ap.png){w=420}

With n = 3 the intervals are wide, and the independent agents show a large seed spread. A static CW sweep (v3.1.0) puts the ceiling for this topology at the best common static CW of 512 for both APs: 39.62 ± 0.21 Mbps, +12.32 ± 0.84 Mbps over BEB and +3.45 ± 6.77 Mbps over Global-CW (the interval spans zero). So the Global-CW agent reaches most of what any fixed CW can give.

### 4.3 From 2 to 10 APs at a fixed 60 stations
To separate the effect of the number of APs from the effect of load (an earlier sweep changed both), the total number of stations was fixed at 60 and split equally.

Table: aggregate goodput at a fixed 60 stations (v2.0.0 fixed-binary runs, 3 seeds)
| APs | BEB (Mbps) | Global-CW | Global vs BEB | Independent | Independent vs BEB |
|---|---|---|---|---|---|
| 2 | 27.38 | 36.23 | +32.3 ± 26.3 % | 28.44 | +3.8 ± 27.2 % |
| 4 | 27.55 | 35.64 | +29.5 ± 27.5 % | 20.14 | -27.0 ± 21.8 % |
| 6 | 28.06 | 36.92 | +31.5 ± 18.9 % | 18.07 | -35.8 ± 109.7 % |
| 10 | 27.89 | 36.87 | +32.2 ± 23.9 % | 14.99 | -46.2 ± 12.2 % |

![Aggregate goodput against the number of APs at a fixed 60 stations.](figures/legacy/fixed60_aggregate_vs_n.png){w=430}

![Jain fairness index against the number of APs at a fixed 60 stations.](figures/legacy/fixed60_jain_vs_n.png){w=400}

- BEB is flat in the number of APs at fixed total load (27.4 to 28.1 Mbps).
- Global-CW OSCAR gains +29.5 % to +33.2 % in every topology and is above BEB in all three seeds.
- Independent per-AP OSCAR drops from equal to BEB at 2 APs to -46 % at 10 APs. The confidence interval excludes zero at 4 and 10 APs. The likely explanation, which is an inference and was not isolated experimentally, is a selfish game: every agent maximizes its own goodput without BEB's safety net, and its reward changes whenever another agent moves.

### 4.4 Imbalance and load
Table: unbalanced BSSs and light load (v2.0.0 fixed-binary runs, 3 seeds)
| Case | BEB | Global-CW | Global vs BEB | Independent | Independent vs BEB |
|---|---|---|---|---|---|
| 5 and 55 stations | 28.64 ± 3.03 | 37.07 ± 5.45 | +29.7 ± 29.5 % | 27.14 ± 11.62 | -5.4 ± 36.2 % |
| 5,5,5 and 45 stations | 27.25 ± 1.47 | 36.28 ± 8.05 | +33.2 ± 29.3 % | 22.81 ± 3.55 | -16.2 ± 17.3 % |
| 20,40 at 0.5 Mbps per station | 27.90 ± 0.85 | 29.64 ± 1.36 | +6.3 ± 8.0 % | 28.86 ± 2.84 | +3.5 ± 13.3 % |
| 20,40 at 1 Mbps per station | 27.86 ± 1.60 | 38.96 ± 0.40 | +39.9 ± 8.3 % | 11.43 ± 13.75 | -58.8 ± 50.3 % |

![Aggregate goodput against the offered load per station at 20 and 40 stations.](figures/legacy/load_sweep.png){w=430}

At 0.5 Mbps per station the network is unsaturated and no controller has much to gain (+6 %). At 1 Mbps the Global-CW agent gains +40 %, and the independent agents are far below BEB.

### 4.5 Central critic (negative result)
A prototype with one actor per AP and one shared critic (centralized training with decentralized execution) was evaluated at 4 and 10 APs (3 seeds, run before the CW 0/0 fix, so the absolute values are pre-fix): at 4 APs it reached 38.96 Mbps against 28.63 for BEB (+36 %), but at 10 APs it collapsed to 3.20 Mbps against 19.24 for BEB (-83 %). The cause of the collapse was not isolated. It is not used for conclusions, and the central critic was dropped from the later plan.
