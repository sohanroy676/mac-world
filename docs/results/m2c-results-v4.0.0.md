# M2c results: learned rivals retrained on Actions CPU (Stage 1, n = 3)

Date: 2026-11-11. Pre-registration: `m2c-preregistration-v4.0.0.md` (written before any result). Jobs: `.github/jobs/m2c.json`
(30 jobs). Run dirs, per-cell GC tables, the selection table and the CPU of each job: `docs/figures/v4.0.0-m2c/`.
Scoring: `ns-3.29/scratch/linear-mesh/gc_analysis.py --tagPrefix m2c- --seeds 100-102 --alphas 0,1,4`
(5 % floor slack, as in M2); selection: `m2c_select.py` (new, applies the pre-registered rule).

## What ran (facts)
- 29 of 30 jobs ran in Actions run 42774734240 (2026-11-10). All `--check` PASS, all exit 0.
- `m2c-s5a-ccod-t1` failed there at apt (404). Four reruns of the failed job failed at apt (DNS) and one through `run-packs.yml` failed at the Python step (Launchpad timeout).
  It then ran in `run-packs.yml` run 43066793808 (same job spec, `lanes 1`): train 4286 s, evals 674/673/683 s, `--check` PASS.
- **Deviation (fact):** that one job used CPython 3.7.12 from conda-forge (micromamba fallback added to `run-packs.yml` because deadsnakes needs Launchpad, which timed out). The other 29 used the deadsnakes build. Torch and numpy come from the same pinned wheels in both. Whether the Python build changes a trace is **unknown**; not tested.
- **CPU (fact, from the job logs; table in `cpu_per_job.tsv`):** AMD EPYC 7763 x17, 9V74 x6 (incl. the rerun), 9V45 x4, Intel Xeon 8370C x2, Intel Xeon 8573C x1.
  Two learner jobs ran on Intel: `m2c-s2-ccod-t0` and `m2c-s4-pf-t2`. Step 0 showed learner runs are bit-identical only within one CPU vendor, so these two seeds are not reproducible on the AMD runners and the training seeds are only comparable up to that effect (effect size **unknown**).
  `m2c-s4-pf-t2` is the selected PF seed in S4 at alpha 1 and 4 (below).
- The M2 rivals were trained on the lab machine (GPU); these are CPU-trained, as the brief required.

## Selected seed per method, cell and alpha (pre-registered rule: highest mean GC over seeds 100-102, feasible first)
Score is mean GC (gap closed, 1 = best feasible static), or raw U where the cell is degenerate (S4 alpha 4: U gap 1299 vs BEB SD 562).

| Cell | alpha | Method | Selected seed | Score | min-AP Mbps | Other seeds (score, feasible) |
|---|---|---|---|---|---|---|
| S2 | 0 | CCOD | t1 | 0.953 | 13.50 | t0 0.729 ok, t2 0.733 ok |
| S2 | 0 | Global | t2 | 0.984 | 13.55 | t0 0.756 ok, t1 0.742 ok |
| S2 | 0 | PF learner | t0 | 0.989 | 19.36 | t1 0.985 INF, t2 0.995 INF |
| S2 | 1 | CCOD | t1 | 0.958 | 13.50 | t0 0.763 ok, t2 0.767 ok |
| S2 | 1 | Global | t2 | 0.986 | 13.55 | t0 0.787 ok, t1 0.775 ok |
| S2 | 1 | PF learner | t0 | 0.816 | 19.36 | t1 0.518 INF, t2 0.287 INF |
| S2 | 4 | CCOD | t1 | 0.974 | 13.50 | t0 0.852 ok, t2 0.855 ok |
| S2 | 4 | Global | t2 | 0.990 | 13.55 | t0 0.869 ok, t1 0.861 ok |
| S2 | 4 | PF learner | t0 | 0.613 | 19.36 | t1 -0.369 INF, t2 -1.643 INF |
| S4 | 0 | CCOD | t2 | 1.228 | 2.48 | t0 1.210 ok, t1 1.163 ok |
| S4 | 0 | Global | t0 | 0.972 | 2.41 | t1 -0.772 ok, t2 -2.423 ok |
| S4 | 0 | PF learner | t1 | -0.891 | 7.13 | t0 -1.736 ok, t2 -2.257 ok |
| S4 | 1 | CCOD | t1 | 0.511 | 2.72 | t0 0.474 ok, t2 0.451 ok |
| S4 | 1 | Global | t2 | 0.826 | 7.09 | t0 0.422 ok, t1 0.150 ok |
| S4 | 1 | PF learner | t2 (Intel) | 0.995 | 9.72 | t0 0.971 ok, t1 0.947 ok |
| S4 | 4 | CCOD | t1 | U -185.0 | 2.72 | t0 -236.5 ok, t2 -262.9 ok |
| S4 | 4 | Global | t2 | U -10.8 | 7.09 | t0 -258.3 ok, t1 -572.5 ok |
| S4 | 4 | PF learner | t2 (Intel) | U -4.25 | 9.72 | t0 -6.77 ok, t1 -10.85 ok |
| S5a | 0 | CCOD | t0 | 1.009 | 10.00 | t1 0.986 ok, t2 0.995 ok |
| S5a | 0 | Global | t1 | 1.001 | 10.00 | t0 0.937 ok, t2 0.762 ok |
| S5a | 0 | PF learner | t1 | 0.969 | 10.00 | t0 0.723 ok, t2 0.887 ok |
| S5a | 1 | CCOD | t0 | 1.007 | 10.00 | t1 0.983 ok, t2 1.002 ok |
| S5a | 1 | Global | t1 | 0.999 | 10.00 | t0 0.943 ok, t2 0.854 ok |
| S5a | 1 | PF learner | t1 | 0.950 | 10.00 | t0 0.891 ok, t2 0.785 ok |
| S5a | 4 | CCOD | t2 | 1.006 | 10.00 | t0 1.003 ok, t1 0.986 ok |
| S5a | 4 | Global | t1 | 0.998 | 10.00 | t0 0.963 ok, t2 0.963 ok |
| S5a | 4 | PF learner | t0 | 1.046 | 10.00 | t1 0.949 ok, t2 0.749 ok |

(S2 PF learner: only seed t0 is floor-feasible at every alpha; t1 and t2 are infeasible, so t0 is selected even though t1/t2 score higher at alpha 0.)
References on the same seeds: BEB GC 0 by definition; IdleSense is infeasible in S4 and S5a at all three alphas, feasible in S2 (GC 0.94 at alpha 1).
Oracles (best feasible static): S2 512,512; S4 alpha 0 64,64,64 and alpha 1 and 4 128,64,128; S5a 128,128,128.

## What the numbers say (facts unless marked)
1. **Seed variance is large for the learners.** Global S4 alpha 1 ranges 0.150 to 0.826 and Global S4 alpha 0 ranges -2.42 to 0.97 over three training seeds. The M2 single-seed numbers (Global 0.33, CCOD 0.54 at S4 alpha 1) are inside that spread.
2. **The strongest rivals, by cell at alpha 1:** S2 Global t2 0.986 and CCOD t1 0.958; S4 PF learner t2 0.995, Global t2 0.826, CCOD t1 0.511; S5a all three at 0.95 to 1.01.
3. **RAFA's weak cell is now compared to stronger rivals.** M3 per-scenario RAFA had GC 0.730 in S2 (selection seeds 0-2, not these seeds). Global t2 and CCOD t1 reach 0.986 and 0.958 here on seeds 100-102. Different seed sets, so this is a pointer, not a test; M4 settles it on seeds 103-109.
4. **In S4 the rival bar went up.** The PF learner t2 reaches 0.995 at alpha 1 (feasible, min-AP 9.72 Mbps). M3 RAFA scored 0.968 in S4 (selection seeds). The bar for Claim 1 in S4 is therefore at the ceiling.
5. **S5a is saturated** at GC about 1 for all methods: a rival that matches the static oracle leaves RAFA no headroom there.
6. **S4 alpha 0 / alpha 4:** the PF learner is weak at alpha 0 (-0.89) and strongest at alpha 4 (U -4.25); CCOD is best at alpha 0 (1.228, above the best static). Alpha-4 cells in S4 are degenerate, so only raw U is comparable.

## Limits and what is not done
- Stage 1 uses n = 3 eval seeds, so CIs are wide and the selection of the strongest seed is noisy (it picks the seed with the highest mean on the same 3 seeds it is judged on). **Claims must use seeds 103-109 only** (plan: Stage 1 seeds 100-102 select, claims on 103-109); the n = 10 run in M4 should therefore evaluate the selected actors on 103-109.
- The selected actors are saved under `docs/figures/v4.0.0-m2c/<job>/actors/` for that run.
- Mixed CPU vendors and one Python-build change (above). A same-vendor rerun of `m2c-s4-pf-t2` and `m2c-s2-ccod-t0` was not done.
- CCOD, Global and PF learner got no tuning sweep (as in M2); RAFA had one for lambda.
- Not tagged. No tag was requested.
