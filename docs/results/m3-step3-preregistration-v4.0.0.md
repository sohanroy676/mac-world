# M3 step 3 pre-registration (written before any step 3 result)

Date: 2026-11-10. Jobs: `.github/jobs/step3.json` (6 jobs, GitHub Actions CPU).

## Design
- Pooled RAFA: `--scenarioPool scenarios/pool_v4_0_0.json --poolRR` (the 24 v3.5.0 configs; equal-load ones at 10 Mbps per STA with `--rewardNorm 150`, `apLoads` ones as written; per-config floors from `pool-beb-refs-10mbps-v4.0.0.csv`), 24 episodes x 15 s, each config once in a seeded random order, `--varySeeds`, alpha input with relabelling, lambda 1 (step 2 choice), python seeds 2000-2002, `--check` on.
- Per-scenario reference: step 2 at lambda 1, 6 episodes, on S4 and S5a (done) and S2 (run here, floors 9.35, 16.90 from pool config 0).
- Evaluation: frozen at alpha 1, 30 s, selection seeds 0-2, in S2, S4 and S5a (none of the three is a pool config at its evaluation seeds; S4 and S5a match pool configs 8 and 14 in topology and load).

## Decision rule (fixed now)
- G3: per cell, mean alpha-1 GC over the 3 training seeds (each the mean over 3 eval seeds). G3 passes if pooled RAFA is at most 0.05 below the per-scenario RAFA in each of S2, S4 and S5a.
- If G3 passes: the pooled form is RAFA; 6 final seeds (2003-2008) are trained the same way and form two ensembles of 3. If G3 fails: RAFA is reported as per-scenario and Claim 1 is tested on that basis (plan kill rule).
