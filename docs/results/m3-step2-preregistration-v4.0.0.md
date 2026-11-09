# M3 step 2 pre-registration (written before any step 2 result)

Date: 2026-11-09. Code: `--mode shared --obs rafa --reward fair --alphaInput --floorLambda L --floors ...` on `feature/v4`. Jobs: `.github/jobs/step2.json` (18 jobs, GitHub Actions CPU).

## Design
- Reward: station-weighted alpha-fair team reward, mapped through the certainty-equivalent per-station throughput (ln M_alpha, 0.01 Mbps -> 0, 10 Mbps -> 1; identical to step 1's `spf` at alpha 1), minus lambda * sum_i max(0, floor_i - xbar_i) / sum_i floor_i, xbar = EMA of AP Mbps (time constant 50 steps). Floors from the 10 Mbps pool BEB references: S4 24.40, 0.30, 24.40; S5a 15.10, 11.53, 10.00.
- Alpha: input alpha/4; one acting alpha per training episode from {0, 0.5, 1, 2, 4}; every replay batch is relabelled with fresh alphas from the same set (reward recomputed from stored per-AP Mbps; the penalty is stored).
- Training: S4 and S5a, 6 episodes x 15 s, python seeds 2000-2002, lambda in {1, 3, 10}; evaluation frozen at alpha 1, 30 s, selection seeds 0-2. References: the step 1 BEB / IdleSense / oracle runs on the same seeds.

## Decision rules (fixed now)
- Lambda: for each lambda, a cell is feasible if all 3 training seeds are floor-feasible (5 % slack) at alpha 1. Among lambdas feasible in both S4 and S5a, pick the highest mean alpha-1 GC over the 6 (cell, seed) runs. Ties within 0.01: the smaller lambda. If no lambda is feasible in both, pick the one with the fewest infeasible runs, then the highest mean GC.
- Then 12 episodes for that lambda (same seeds and cells). Keep 12 only if its mean alpha-1 GC is at least 0.05 above the 6-episode value; else keep 6.
- Step 1 (no alpha input, no penalty) is the comparison point; step 2 is kept even if its alpha-1 GC is slightly lower, because it adds the alpha input needed for the alpha-0 and max-min cells. If step 2's mean alpha-1 GC is more than 0.05 below step 1's on S4 + S5a, the alpha input is reported as a cost and the relabelling is re-checked before step 3.
