# M3 step 2 results (v4.0.0): alpha input, relabelling, floor penalty

## Lambda batch (6 episodes)
Run [42688026722](https://github.com/sohanroy676/mac-world/actions/runs/42688026722), 18 jobs on Actions CPU, all `--check` PASS. Rules: `m3-step2-preregistration-v4.0.0.md`. Evaluation frozen at alpha 1, 30 s, selection seeds 0-2; references as in step 1. Tables: `docs/figures/v4.0.0-step2/gc_sel_{s4,s5a}.md`. GC at alpha 1, mean ± 95 % CI over 3 eval seeds; every run is floor-feasible (5 % slack).

| lambda | S4 t0 | S4 t1 | S4 t2 | S5a t0 | S5a t1 | S5a t2 | mean of 6 |
|---|---|---|---|---|---|---|---|
| 1 | 0.992 ± 0.160 | 1.023 ± 0.209 | 0.889 ± 0.049 | 0.656 ± 0.119 | 0.851 ± 0.026 | 0.817 ± 0.070 | **0.871** |
| 3 | 0.764 ± 0.041 | 0.664 ± 0.456 | 0.672 ± 0.019 | 0.709 ± 0.107 | 0.862 ± 0.010 | 0.701 ± 0.123 | 0.729 |
| 10 | 0.831 ± 0.081 | 0.888 ± 0.052 | 0.459 ± 0.052 | 0.376 ± 0.098 | 0.766 ± 0.032 | 0.569 ± 0.091 | 0.648 |
| step 1 (no alpha input, no penalty) | 0.956 | 0.795 | 0.867 | 0.905 | 0.845 | 0.949 | 0.886 |

Decision by the pre-registered rule: **lambda = 1** (feasible in both cells, highest mean). Step 2 at lambda 1 is 0.015 below step 1 on S4 + S5a (within the 0.05 tolerance), better in S4 (0.97 vs 0.87 mean) and worse in S5a (0.77 vs 0.90). Larger lambda costs GC without being needed for feasibility (no run was infeasible). Next: 12 episodes at lambda 1, and evaluation at alpha 0 to test the alpha input.
