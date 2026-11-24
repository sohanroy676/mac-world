# Wave 4a confirmation (seeds 103-122, 300 s, 760 runs)

Status: complete, 760/760 runs. Metric: share = (U - U_BEB)/(U_ceiling - U_BEB), BEB paired per seed, second half of each run (`thr_half2`). A seed with any AP below floor x 0.95 counts as share 0. Analysis: `ns-3.29/scratch/linear-mesh/confirm_v4_1_0.py`.

Collection: the first run (Wave 4a) and two reruns (4a2, 4a3) were cancelled by GitHub (cause unknown, not by us); the missing jobs were rerun as 4a2-4a4. Merged data has 760 unique jobs, 0 hash mismatches.

## Findings
- **Target not met.** Best online candidate kwdirect (exact CW updates) has worst-cell share 0.85 (S4, alpha 1); the target was 0.95. All other cells are 0.93-1.02.
- **Gate C (100 ms updates, 2^k-1 rounding) is much worse**: worst share 0.41; many S2 seeds infeasible (9/20, 13/20, 12/20 feasible). Cost vs exact kwdirect: S2 -0.50 to -0.56, S4 -0.09 to -0.28, S5a -0.01 to -0.19 (S2 and S5a a1/a4 clearly significant). Whether this is the 100 ms period itself or the controller not being tuned for it is not tested here.
- **kwdirect vs rivals (paired, IU non-inferiority margin 0.05, Holm):** better than DAC514 (p<0.001; DAC is infeasible on every S4 and S5a cell) and than kwdirect-gatec. Not shown non-inferior to the static F1 point (p 0.83): kwdirect is worse in 7 cells by at most 0.065 and better in 2. F1 is the tuned static ceiling reference, not an online method.
- **Learners:** PF and RAFA fail on S4 alpha 0 (about -1.9); global on S2 is good (0.97-0.98) but covers only one cell family. Learners are not a single recipe across cells.
- coord on S4 alpha 1: 0.90.

## Tables (mean (sd), feasible seeds / n)
## Share of the validated ceiling, mean (sd), feasible seeds, n seeds
| family | s2 a0 | s2 a1 | s2 a4 | s4 a0 | s4 a1 | s4 a4 | s5a a0 | s5a a1 | s5a a4 | worst |
|---|---|---|---|---|---|---|---|---|---|---|
| kwdirect | 0.98 (0.02) 20/20 | 0.97 (0.03) 20/20 | 0.97 (0.03) 20/20 | 0.99 (0.21) 20/20 | 0.85 (0.09) 20/20 | 1.00 (0.00) 20/20 | 0.94 (0.03) 20/20 | 1.02 (0.03) 20/20 | 0.93 (0.08) 20/20 | 0.85 |
| kwdirect-gatec | 0.44 (0.50) 9/20 | 0.47 (0.45) 13/20 | 0.41 (0.39) 12/20 | 0.71 (0.60) 19/20 | 0.77 (0.17) 20/20 | 0.90 (0.31) 18/20 | 0.93 (0.03) 20/20 | 0.83 (0.37) 20/20 | 0.74 (0.33) 20/20 | 0.41 |
| f1 | 1.00 (0.00) 20/20 | 1.00 (0.00) 20/20 | 1.00 (0.00) 20/20 | 0.82 (0.14) 20/20 | 0.92 (0.01) 20/20 | 1.00 (0.00) 20/20 | 1.00 (0.00) 20/20 | 1.00 (0.00) 20/20 | 1.00 (0.00) 20/20 | 0.82 |
| dac514 | 0.96 (0.02) 20/20 | 0.95 (0.04) 20/20 | 0.94 (0.07) 20/20 | 0.00 (0.00) 0/20 | 0.00 (0.00) 0/20 | 0.00 (0.00) 0/20 | 0.00 (0.00) 0/20 | 0.00 (0.00) 0/20 | 0.00 (0.00) 0/20 | 0.00 |
| coord | - | - | - | - | 0.90 (0.10) 20/20 | - | - | - | - | n/a (1 cells) |
| L-global | 0.98 (0.02) 20/20 | 0.98 (0.03) 20/20 | 0.97 (0.04) 20/20 | - | - | - | - | - | - | n/a (3 cells) |
| L-pf | - | - | - | -1.90 (0.30) 20/20 | 0.92 (0.05) 20/20 | 1.00 (0.00) 20/20 | 0.90 (0.01) 20/20 | 1.09 (0.01) 20/20 | 1.02 (0.01) 20/20 | n/a (6 cells) |
| L-rafa | - | - | - | -1.86 (0.28) 20/20 | 0.94 (0.04) 20/20 | 1.00 (0.00) 20/20 | - | - | - | n/a (3 cells) |

## Paired tests: kwdirect minus each family (share units, margin 0.05); IU = intersection-union non-inferiority over all 9 cell-alpha pairs
| family | min cell diff | IU p non-inferior (Holm) | cells better (p<0.05) | cells worse (p<0.05) |
|---|---|---|---|---|
| kwdirect-gatec | 0.013 | 0.0194 (0.0387) | 6 | 0 |
| f1 | -0.065 | 0.8312 (0.8312) | 2 | 7 |
| dac514 | 0.011 | 0.0000 (0.0001) | 8 | 0 |

## Paired tests: kwdirect-gatec minus each family (share units, margin 0.05); IU = intersection-union non-inferiority over all 9 cell-alpha pairs
| family | min cell diff | IU p non-inferior (Holm) | cells better (p<0.05) | cells worse (p<0.05) |
|---|---|---|---|---|
| kwdirect | -0.562 | 1.0000 (1.0000) | 0 | 6 |
| f1 | -0.587 | 1.0000 (1.0000) | 0 | 6 |
| dac514 | -0.529 | 1.0000 (1.0000) | 6 | 3 |

## Gate C cost: kwdirect-gatec minus kwdirect, per cell-alpha (share units, mean, 95% half-width, non-inferiority p for margin 0.05)
- s2 a0: -0.539 +- 0.233, p_noninf 0.9998 (n=20)
- s2 a1: -0.500 +- 0.212, p_noninf 0.9999 (n=20)
- s2 a4: -0.562 +- 0.185, p_noninf 1.0000 (n=20)
- s4 a0: -0.284 +- 0.295, p_noninf 0.9432 (n=20)
- s4 a1: -0.086 +- 0.081, p_noninf 0.8196 (n=20)
- s4 a4: -0.102 +- 0.143, p_noninf 0.7719 (n=20)
- s5a a0: -0.013 +- 0.018, p_noninf 0.0001 (n=20)
- s5a a1: -0.186 +- 0.179, p_noninf 0.9358 (n=20)
- s5a a4: -0.192 +- 0.134, p_noninf 0.9805 (n=20)

