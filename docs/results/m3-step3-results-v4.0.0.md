# M3 step 3 results: pooled RAFA, gate G3 (v4.0.0)

Date: 2026-11-10. Platform: GitHub Actions CPU (ubuntu-24.04 runner, ubuntu:22.04 container).
Pre-registration: `m3-step3-preregistration-v4.0.0.md` (written before any result).
Runs: 42727383779 (S2 per-scenario reference; pooled jobs crashed, see below) and
42743507110 (pooled jobs rerun with the fix, plus regressions). Run dirs, actors and GC tables are in
`docs/figures/v4.0.0-step3/` (job list `step3b.json`).

## What ran
- Pooled RAFA: 24 episodes x 15 s, round-robin over the 24 pool configs, lambda 1, alpha input with relabelling,
  python seeds 2000-2002. It was then frozen and evaluated at alpha 1, 30 s, selection seeds 0-2 in S2, S4 and S5a.
- Per-scenario S2 reference: lambda 1, 6 episodes, seeds 2000-2002 (S4 and S5a references come from step 2).
- Every job ended with `--check` PASS.

## First run failure and fix (fact)
- In run 42727383779 all 3 pooled jobs finished training and saved their actors. They then crashed in the last
  sanity check ("reward columns identical for AP i and j"). Pool episodes vary the AP count, so the per-AP reward lists
  had different lengths (36000 vs 24000). No other check failed.
- Fix 399162f: rewards are now keyed by global step and compared only on the steps where both APs were active.
  For fixed-topology runs this is the same comparison as before.
- Regressions after the fix: the `2,3` reference trace is unchanged (sha256 `044cf770...1958`), and `det-sh` pinned
  gives `70687d59...` (the known Intel hash). Pooled actors t0 and t2 from the rerun are byte-identical to the
  crashed run's actors, while t1 differs (it ran on the other CPU vendor, as found in step 0).

## G3 (alpha 1, mean over 3 eval seeds per training seed)

| Cell | Per-scenario t0 / t1 / t2 | mean | Pooled t0 / t1 / t2 | mean | Pooled minus per-scenario |
|---|---|---|---|---|---|
| S2 | 0.730 / 0.730 / 0.730 | 0.730 | 0.602 / 0.136 / 0.829 | 0.522 | -0.208 |
| S4 | 0.992 / 1.023 / 0.889 | 0.968 | 0.852 / 0.544 / 0.262 | 0.553 | -0.415 |
| S5a | 0.656 / 0.851 / 0.817 | 0.775 | 0.759 / 0.809 / 0.262 | 0.610 | -0.165 |

All runs are feasible (fair floors met). The 95 % CIs are in the `gc_sel_*.md` tables.

**G3 FAILS.** Pooled RAFA is more than 0.05 below per-scenario RAFA in all three cells.
- Pooled worst-cell GC per seed: 0.602 / 0.136 / 0.262.
- Per-scenario worst-cell GC per seed: 0.656 / 0.730 / 0.730.

## Consequence (pre-registered kill rule)
- RAFA is reported as per-scenario (lambda 1, 6 episodes), and Claim 1 is tested on that basis.
- The 6 pooled final seeds (2003-2008) are not trained.

## Other observations
- **S2 per-scenario (fact):** at lambda 1 every seed saturates at the CW maximum (1023-1024) on both APs, so GC is 0.730.
  Step 1 at lambda 0 gave 0.967 / 0.730 / 0.950, and its seed 1 showed the same collapse.
  Lambda was chosen on S4 and S5a only, as pre-registered, so S2 is RAFA's weak cell. Changing lambda for S2 now would
  be selection after the fact.
- **Pooled seeds vary widely (inference):** S4 ranges from 0.26 to 0.85. 24 episodes give each config one episode,
  which is likely too little data per scenario. Not tested.
