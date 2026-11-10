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

## 12 episodes and the alpha input (run [42707429586](https://github.com/sohanroy676/mac-world/actions/runs/42707429586), 13 jobs, all PASS; one job's Python install failed and was rerun)
Tables: `docs/figures/v4.0.0-step2b/gc_sel_{s4,s5a}_a{0,1}.md`. Selection seeds 0-2, 30 s, all runs floor-feasible.

| Run (lambda 1) | S4 t0 | S4 t1 | S4 t2 | S5a t0 | S5a t1 | S5a t2 | mean |
|---|---|---|---|---|---|---|---|
| 6 episodes, alpha 1 | 0.992 | 1.023 | 0.889 | 0.656 | 0.851 | 0.817 | 0.871 |
| 12 episodes, alpha 1 | 0.839 | 0.975 | 0.929 | 0.810 | 0.864 | 0.934 | 0.892 |
| 6 episodes, evaluated at alpha 0 | 0.009 | -1.587 | 0.866 | 0.722 | 0.907 | 0.667 | |
| 12 episodes, evaluated at alpha 0 | 0.291 | -1.002 | 0.660 | 0.818 | 0.964 | 0.983 | |
| step 1 actor (alpha 1 only), at alpha 0 | -2.891 | -2.971 | -3.099 | 0.972 | 0.916 | 0.986 | |

- Decision by the rule: 12 episodes gain 0.021 (< 0.05), so **6 episodes are kept**. (Fact: 12 episodes lowered the seed spread in S5a, 0.81-0.93 vs 0.66-0.85.)
- Alpha input (fact): in S4, where the alpha-0 and alpha-1 oracles differ (64,64,64 vs 128,64,128), the alpha input moves the policy the right way: alpha-0 GC rises from about -2.9 (alpha-1 actor) to 0.0 / -1.6 / 0.87, but it is far from the oracle and unstable across seeds; S4 at alpha 0 is a narrow cell (U gap 3.5 Mbps, BEB SD 0.39). In S5a both oracles are 128,128,128 and the alpha-1-only actor is already best. Inference: the alpha-0 behaviour is RAFA's weak spot so far (CCOD reaches 1.14 there on seeds 100-109); it is reported, not tuned on selection seeds.
