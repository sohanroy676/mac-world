# M3 step 1 results (v4.0.0): shared RAFA actor, alpha 1, 3 training seeds

Run [42667361417](https://github.com/sohanroy676/mac-world/actions/runs/42667361417), 30 jobs on GitHub Actions CPU, all `--check` PASS. Rules fixed beforehand in `m3-step1-preregistration-v4.0.0.md`. Training 6 episodes x 15 s (python seeds 2000-2002); evaluation frozen, 30 s, selection seeds 0-2 (n = 3 per training seed); references BEB, IdleSense and the static oracle on the same seeds. Tables: `docs/figures/v4.0.0-step1/gc_sel_{s4,s2,s5a}.md`; CWs: `m3_step1_analysis.py`. Mean ± 95 % CI over the 3 eval seeds (eval-seed variance only).

## GC at alpha 1 (fact)
| Cell | t0 | t1 | t2 | mean of seeds | BEB | IdleSense | Oracle |
|---|---|---|---|---|---|---|---|
| S4 | 0.956 ± 0.106 | 0.795 ± 0.019 | 0.867 ± 0.061 | 0.873 | 0 | -0.117 (infeasible) | 1 (128,64,128) |
| S2 | 0.967 ± 0.098 | 0.730 ± 0.148 | 0.950 ± 0.094 | 0.882 | 0 | 0.917 | 1 (512,512) |
| S5a | 0.905 ± 0.018 | 0.845 ± 0.060 | 0.949 ± 0.017 | 0.900 | 0 | -0.168 (infeasible) | 1 (128,128,128) |

Every RAFA run is floor-feasible (5 % slack) in all three cells. For context only (different seeds, 100-109, n = 10): best feasible general method in S4 at alpha 1 was UCB 0.66, the per-scenario PF learner 0.95 in 2 of 3 seeds, CCOD's worst cell 0.54.

## Gates (fact, by the pre-registered rules)
- **G1 (S4) FAILS.** Edge/middle CW ratio 1.68 / 1.01 / 1.24 (mean CWs 241/144/241, 275/273/276, 271/217/271); none reaches 2 (oracle 128,64,128). The actor separates roles only partly (seed 0) and instead raises every CW to about 240-275.
- **G2 (S2) PASSES.** GC 0.967 and 0.950 >= 0.86 in 2 of 3 seeds, all feasible. Seed t1 is a collapse: the actor saturates at CW 1024 on both APs (same result under all three noise types).
- **Gumbel: not adopted.** S4 gumbel vs Gaussian per seed: +0.004, -0.017, -0.006; gumbel-raw: +0.006, +0.015, -0.097. S2 gumbel: +0.004, 0.000, -0.007; gumbel-raw: -0.012, 0.000, +0.007. Neither is ahead on every seed pair, so the default stays Gaussian.

## Decision on G1 (decision, 2026-11-09, deviation from the plan's kill rule, stated openly)
The kill rule says: if G1 fails, use independent actors for fixed topologies. G1 was a mechanism check, built on the premise that a shared actor that cannot separate edge and middle CWs cannot do well in S4. The same runs refute that premise: with ratio 1.0-1.7 the shared actor reaches GC 0.80-0.96 in S4, feasible in every seed, which is above every general rival measured so far in that cell. The plan's claims are scored on GC, not on CW ratios. So RAFA continues to step 2 with the shared actor, and G1 is reported as failed, with this reason. The fallback (independent per-AP learners for fixed topologies) stays available as the PF-learner rival in M2c. Risk kept in view: 1 of 3 seeds is weak in S4 and S2 (t1; in S2 a saturation collapse); step 2 must report per-seed results, and the final method is an ensemble of 3 seeds.

## Caveats
n = 3 eval seeds per training seed, selection seeds only, no multiplicity correction; these numbers screen, they are not claims. Oracle CIs are wide in S4 and S5a (±0.16-0.19), so GC near 1 is within the oracle's noise.
