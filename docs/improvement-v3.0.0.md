# v3.0.0 Beating Global-CW OSCAR: results

Status: experiment report. Branch `feature/beat-oscar`; not merged, not tagged. Trainer-only change (`OSCAR_multi_ap_train.py`, `aggregate_bench.py`); `cw.cc` unchanged, `linear-mesh` rebuilt 2026-10-25 12:45. Design decision: `docs/adr/0004-relaxed-isolation.md`. Tables: `docs/figures/v3.0.0/` (raw `results/` not committed).

## 1. Question
Can a per-AP-CW method match or beat Global-CW OSCAR (one shared CW), not just BEB?

## 2. What was added
`--mode shared`, `--obs {loss,hist}`, `--obsWindow`, `--alpha`, `--rewardScale` (now all modes), `--tag`. Defaults verified byte-identical to the old trainer for global and independent (400-step prefix).
V5 = `--mode shared --obs hist --rewardScale 100 --alpha 0 --tag V5`.

## 3. Reference check
Fixed-binary raw dirs from 2026-10-18 are not on this machine, so BEB and Global were re-run on the current binary. BEB 27.30 ± 0.63 reproduces the committed v2.2.0 value exactly; Global 36.17 ± 6.95 vs committed 36.29 ± 7.16.

## 4. 20,40 screen (15 s, aggregate Mbps)
| Variant | Settings | Seed 0 |
|---|---|---|
| BEB | | 27.25 |
| Global | | 35.07 |
| V1 | independent + hist | 20.83 |
| V2 | V1 + x100 | 15.17 |
| V3 | V2 + alpha 0.5 | 26.22 |
| V4 | shared + hist + x100 + alpha 0.5 | 35.07 |
| V5 | shared + hist + x100 + alpha 0 | 37.09 |

3 seeds (0-2): BEB 27.30 ± 0.63, Global 36.17 ± 6.95, V5 37.08 ± 0.85. V5 vs Global +2.8 ± 16.9 % (CI spans 0; above Global in 2/3 seeds); V5 vs BEB +35.8 ± 6.2 %. Phy loss V5 0.533 ± 0.002, Global 0.626 ± 0.123.

## 5. Shared-mode ablations (20,40; A2 seed 0 n=1, A1 and V5 n=3)
| Variant | Settings | Aggregate | Phy loss | Jain | CW AP1 / AP2 |
|---|---|---|---|---|---|
| A1 | shared, `--obs loss`, x100, alpha 0 | 38.48 ± 2.64 (n=3; seed 0 39.09) | 0.563 ± 0.065 | 0.911 ± 0.047 | 585 / 584 (±~800 across seeds) |
| A2 | shared, `--obs hist`, x1, alpha 0 | 37.38 | 0.537 | 0.893 | 929 / 936 |
| V5 | shared, `--obs hist`, x100, alpha 0 | 37.09 (3-seed 37.08 ± 0.85) | 0.533 | 0.909 | 946 / 940 |
| Global | seed 0 | 35.07 | | | |

A1 per seed (aggregate Mbps): 39.09, 37.25, 39.08; Global 35.07, 39.35, 34.09. A1 vs Global (paired, n=3): +2.30 ± 9.56 Mbps, +6.9 ± 26.7 %, above Global in 2/3 seeds (below at seed 1), min-AP +0.78 ± 3.37 Mbps; CI spans 0. A1 final CW differs by seed (448/463, 950/951, 358/339). Run times 1300-2020 s (A1), 1266 s (A2). Tables: `docs/figures/v3.0.0/ablation-20-40/`.

## 6. Stress test
### 6.1 Imbalance, 3 seeds (0-2); BEB seed 0 only
| Topology | Global agg | V5 agg | V5 - Global (Mbps) | V5 - Global (%) | Seeds above | Min-AP delta (Mbps) | Seeds above |
|---|---|---|---|---|---|---|---|
| 5,55 | 37.09 ± 5.35 | 38.86 ± 0.58 | +1.77 ± 4.86 | +5.0 ± 13.6 | 2/3 | +0.37 ± 0.57 | 3/3 |
| 5,5,5,45 | 36.31 ± 8.06 | 37.61 ± 4.88 | +1.30 ± 3.68 | +3.8 ± 10.8 | 2/3 | +0.10 ± 0.51 | 2/3 |

Per seed (aggregate Mbps, Global / V5): 5,55: 35.21/38.77, 39.44/39.12, 36.63/38.68; 5,5,5,45: 36.88/38.59, 39.24/38.89, 32.82/35.35. V5 is below Global at seed 1 in both. Jain is unchanged (5,55: 0.617 vs 0.623; 5,5,5,45: 0.455 vs 0.450). Phy loss V5 0.553 vs 0.611 and 0.564 vs 0.619. Seed-0 BEB: 28.45 and 27.93.

### 6.2 6x10, seed 0 only (n=1)
BEB 27.78, Global 36.05, V5 35.73 (-0.9 %); min-AP 4.76 (Global) / 4.71 (V5); Jain 0.986 / 0.985; phy loss 0.631 / 0.545. V5 CWs 925-959, Global 200.

Final CW (last 100 steps), V5: 421/415 (5,55, 3-seed mean), 585-599 (5,5,5,45, mean; spread across seeds ±750), 925-959 (6x10 seed 0). Run times 1184-1592 s, all PASS (`--check`). Tables: `docs/figures/v3.0.0/stress-*/`.

## 7. Reading
- Fact: at 20,40 V5 is at Global level (+2.8 ± 16.9 %, CI spans 0). In both 3-seed imbalance topologies the V5 - Global CI also spans 0 (aggregate and min-AP). No throughput gain over Global is established. The seed-0 stress gains (+10.1 %, +4.6 %) were mostly seed noise.
- Fact: V5 seed variance is lower at 20,40 (±0.85 vs ±6.95) and at 5,55 (±0.58 vs ±5.35); weaker at 5,5,5,45 (±4.88 vs ±8.06).
- Fact: V5's per-AP CWs do not separate under 5 vs 55 or 5 vs 45 imbalance.
- Inference: V5 acts as a global CW with shared weights; per-AP CW is not what drives its results. Cause of the variance reduction is untested (candidate: N transitions per step into one agent).
- Inference (one seed each): with independent agents, hist obs (V1), then x100 (V2) lowered throughput, and alpha 0.5 (V3) recovered part of it; only parameter sharing (V4, V5) reached Global level. In shared mode, neither hist obs nor x100 is needed (A1 39.09, A2 37.38 vs V5 37.09 seed 0). Hist obs changes the CW level (~940 vs ~450) and not throughput. With 3 seeds A1 (38.48 ± 2.64) and V5 (37.08 ± 0.85) overlap, and A1 vs Global has a CI spanning 0 (fact), so the seed-0 A1 lead was mostly seed noise. A1 seed spread is larger than V5's; the CW level of A1 is not stable across seeds (inference: loss-only obs does not pin the CW as hist obs does).
- Inference: lower phy loss at higher CW did not give extra throughput at 6x10.

## 8. Limitations
n=1 for V1-V4, A2 and 6x10; n=3 elsewhere (A1 n=3); one load (150 Mbps/STA); 15 s runs; BEB at seed 0 only in the stress topologies; CWs near 940 may be close to the upper clip.

## 9. Conclusion
A reliable Global-level controller with lower seed variance in some topologies, not a proven throughput gain over Global-CW. Parameter sharing appears to be the useful ingredient; per-AP CWs do not differentiate. The simplest shared variant (A1, 3 seeds) is also Global-level (+6.9 ± 26.7 %, CI spans 0). Open if pursued: a test of why variance drops, and a setting where the optimal CWs truly differ per AP.
