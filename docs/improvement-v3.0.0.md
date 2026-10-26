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

## 5. Stress test (seed 0, n=1 per cell, indicative only)
| Topology | BEB | Global | V5 | V5 vs Global | Min-AP Global / V5 |
|---|---|---|---|---|---|
| 5,55 | 28.45 | 35.21 | 38.77 | +10.1 % | 3.60 / 4.02 |
| 5,5,5,45 | 27.93 | 36.88 | 38.59 | +4.6 % | 3.48 / 3.69 |
| 6x10 | 27.78 | 36.05 | 35.73 | -0.9 % | 4.76 / 4.71 |

Jain is unchanged between Global and V5 (5,55: 0.612 vs 0.614; 5,5,5,45: 0.473 vs 0.474; 6x10: 0.986 vs 0.985). V5 phy loss is lower in all three (e.g. 0.545 vs 0.631 at 6x10). Run times 1184-1592 s each; all PASS.
V5 CWs (last 100 steps): 473/474 (5,55); 394-405 (5,5,5,45); 925-959 (6x10), against Global 145, 224, 200.

## 6. Reading
- Fact: V5 aggregate is above Global in 3 of 4 topologies (20,40 mean, 5,55, 5,5,5,45) and level at 6x10 (-0.9 %), but every gap is smaller than Global's seed spread (about ±7 Mbps at 20,40). No gain is established.
- Fact: V5 seed variance at 20,40 is much lower (±0.85 vs ±6.95).
- Fact: V5's per-AP CWs do not separate even under 5 vs 55 and 5 vs 45 imbalance.
- Inference: V5 acts as a global CW with shared weights; per-AP CW is not what drives its results. Why variance drops is untested (candidate: N transitions per step into one agent).
- Inference: with independent agents, hist obs (V1), then x100 (V2) lowered throughput, and alpha 0.5 (V3) recovered part of it; only parameter sharing (V4, V5) reached Global level. V1-V4 are seed 0 only, and no ablation inside shared mode was run, so the individual contributions are unproven.
- Inference: lower loss at 6x10 came with higher CW but no extra throughput.

## 7. Limitations
n=1 for V1-V4 and all stress cells; one load (150 Mbps/STA); 15 s runs; no ablation within shared mode; V5 CW ~940 at 20,40 and 6x10 may be near the upper clip.

## 8. Conclusion
Honest outcome: a reliable Global-level controller with lower seed variance, not a proven throughput gain over Global-CW. Next step if pursued: 3 seeds on 5,55 and 5,5,5,45 (Global vs V5), and shared-mode ablations (obs=loss, scale 1).
