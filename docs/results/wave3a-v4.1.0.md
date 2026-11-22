# Wave 3a: tournament on seeds 300-309 (v4.1.0)

- 430 runs (BEB, static F1/F2, DAC514, BLADE, IdleSense, KW, UCB, kwdirect at its per-alpha setting, coord on S4 alpha 1), 60 s, seeds 300-309, 430/430 complete, 0 hash mismatches, run 44973233383 (about 2 h wall, 172 lab-h). Learners are the Wave 2l evals (best Wave 2k training seed per cell and learner).
- Scoring: 30-60 s window (`thr_half2`), station-weighted alpha-fair utility, share = (U - U_BEB) / (U_ceiling - U_BEB) with BEB paired per seed; ceilings are the validated values on seeds 200-209 (not rerun); an infeasible seed (any AP below 0.95 x BEB floor) counts as share 0. Script `ns-3.29/scratch/linear-mesh/tournament_v4_1_0.py`; full per-cell tables in [wave3a-tables-v4.1.0.md](wave3a-tables-v4.1.0.md).
- Fact: this is the first run of the online controller on tournament seeds. Inference: scoring on `thr_all` instead of `thr_half2` changes kwdirect S2 alpha 0 from 0.98 to 0.73 (the controller needs about 30 s to converge), so the window matters.

## Worst cell per method (primary metric: worst-cell share of the best online candidate, target 0.95 = a hypothesis)
| family | s2 a0 | s2 a1 | s2 a4 | s4 a0 | s4 a1 | s4 a4 | s5a a0 | s5a a1 | s5a a4 | worst |
|---|---|---|---|---|---|---|---|---|---|---|
| kwdirect | 0.98 | 0.98 | 0.97 | 1.04 | 0.90 | 1.00 | 0.94 | 1.04 | 0.94 | 0.90 |
| static-F1 | 1.00 | 1.00 | 1.00 | 0.80 | 0.91 | 0.90 | 1.00 | 0.99 | 1.00 | 0.80 |
| static-F2 | 0.99 | 0.98 | 0.99 | 0.95 | 0.88 | 1.00 | - | - | - | n/a (6 cells) |
| blade | 0.72 | 0.75 | 0.80 | -0.53 | -0.03 | 0.02 | 0.00 | 0.00 | 0.00 | -0.53 |
| dac514 | 0.89 | 0.88 | 0.87 | 0.85 | 0.04 | -0.14 | 0.00 | 0.00 | 0.00 | -0.14 |
| idlesense | 0.83 | 0.84 | 0.86 | -0.06 | -0.06 | -0.34 | 0.00 | 0.00 | 0.00 | -0.34 |
| kw | 0.45 | 0.49 | 0.60 | -0.72 | 0.13 | 0.20 | 0.77 | 0.98 | 0.98 | -0.72 |
| ucbctx | 0.00 | 0.00 | 0.00 | -3.76 | 0.59 | 0.99 | -0.26 | -0.06 | 0.20 | -3.76 |
| global | 0.90 | 0.89 | 0.89 | 0.62 | 0.60 | 0.93 | 0.97 | 0.99 | 0.86 | 0.60 |
| pf | 0.99 | 0.93 | 0.88 | -2.11 | 0.92 | 1.00 | 0.90 | 1.09 | 1.02 | -2.11 |
| rafa-a1 | 0.60 | 0.63 | 0.70 | -2.07 | 0.94 | 1.00 | 0.87 | 0.98 | 0.92 | -2.07 |
| rafa-alphamatched | 0.60 | 0.63 | 0.70 | -1.91 | 0.94 | 0.99 | 0.91 | 0.98 | 0.87 | -1.91 |


## Paired tests
Non-inferiority (kwdirect not worse by more than the margin) must hold in all 9 cell-alpha pairs: intersection-union p (Holm over families).
| family | min cell diff | IU p non-inferior | cells where kwdirect is better (paired t, p<0.05) | cells where family is better |
|---|---|---|---|---|
| static-F1 | -0.061 | 0.6996 (Holm 1.0000) | 2 | 3 |
| blade | 0.171 | 0.0221 (Holm 0.1985) | 8 | 0 |
| dac514 | 0.089 | 0.1611 (Holm 0.9663) | 5 | 0 |
| idlesense | 0.113 | 0.0704 (Holm 0.5632) | 6 | 0 |
| kw | -0.040 | 0.3481 (Holm 1.0000) | 8 | 0 |
| ucbctx | 0.006 | 0.0000 (Holm 0.0000) | 9 | 0 |
| global | -0.027 | 0.1153 (Holm 0.8073) | 5 | 1 |
| pf | -0.079 | 0.8488 (Holm 1.0000) | 4 | 2 |
| rafa-a1 | -0.041 | 0.1813 (Holm 0.9663) | 6 | 1 |
| rafa-alphamatched | -0.041 | 0.1813 (Holm 0.9663) | 8 | 1 |

## Reading (n = 10 seeds)
- **kwdirect (online) has the best worst-cell share of every method with all 9 cells: 0.90** (S4 alpha 1; every other cell 0.94 to 1.04). The 0.95 target is NOT met, by 0.05. Coord on S4 alpha 1 scores 0.91 (a tie with kwdirect, 0.90).
- Learners (class B, best Wave 2k seed): Global worst 0.60 (S4 alpha 1), PF -2.1 and RAFA -1.9 to -2.1 (both S4 alpha 0, where they lose throughput to BEB at alpha 0). RAFA S2 is 0.60 to 0.70 at all alphas (saturates at CW 1024 and is feasible on only 8 of 10 seeds).
- The static F1 plan (validated on seeds 200-209) has worst share 0.80 on S4 alpha 0; static F2 0.88 (S4 alpha 1). So an online controller beats a fixed plan in the worst cell.
- Rivals: DAC worst -0.14 (S5a, S4 alpha 4), BLADE -0.53, IdleSense -0.34, KW -0.72, UCB -3.8. DAC at Tc 514 us is the strongest rival on S2 and S4 alpha 0 (0.85 to 0.89) but is infeasible on S5a and weak on S4 alpha 1/4.
- Tests: kwdirect is significantly better than each rival in several cells and significantly worse in few (static F1: better in 2, worse in 3; Global: 5/1; PF: 4/2; RAFA alpha-matched: 8/1). The intersection-union non-inferiority test across all 9 cells is NOT rejected for any family except UCB (Holm-adjusted p 0.00; others 0.20 to 1.0), because several rivals have infeasible seeds (large SD) and n = 10 with margin 0.05 is low powered. So no all-cell non-inferiority claim yet; this is what Wave 4 (20 seeds, 300 s) is for.

## Caveats
- BEB itself is infeasible on 1 to 2 of 10 seeds in S2/S4 against floors fixed from the validation seeds; its share is 0 by definition so this does not change the shares, only the floor definition.
- Ceilings are from seeds 200-209; shares above 1.0 mean the 300-309 run beat the validated ceiling point.
- Learner seeds were chosen on eval seeds 0-2 (Wave 2k); seed 300-309 numbers are out-of-sample.
- DAC and the other rivals were tuned once on seeds 0-3 (Wave 2g) because they do not take alpha; kwdirect has per-alpha settings. That favours kwdirect slightly.
