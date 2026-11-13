# Maximum contention window optimization: final plan (proposed, 2026-11-13)

Status: **proposed, not approved**. No code or runs were made for it. Full text: https://claude.ai/artifact/9GhjxwS5Men4fXNtTECVje (private). Based on `feature/v4` 6dc82ca.

## Summary
- Goal changes from "RAFA has no weak cell against rivals" to "a deployable controller reaches a measured ceiling in every cell, with the distance to a provable bound reported".
- Evidence (fact, `docs/results/`): per-scenario RAFA is 0.23-0.27 GC below the octave static oracle in S2 and S5a; DAC (no training) is 0.945 in S2 and feasible everywhere; adaptive methods exceed GC 1 (up to 1.47), so the octave oracle is not the ceiling; training-seed spread exceeds method differences.
- Design (decision, proposed): three-layer stack "ACE" = model-based anchor (Patras Eq. 18 / DAC) + constrained Kiefer-Wolfowitz on log-CW (Gaussian-process search as alternative) + fair-floor guard with change detector. RAFA stays as a tournament candidate.

## Phases (lab-hours are estimates)
| Phase | Outcome | Lab-h |
|---|---|---|
| 0 Clean base | merged docs/spec, Tc measured, compute pre-flight | ~20 |
| 1 Ceiling | analytical bounds + fine exact-CW searched ceiling per cell (Gate A) | ~400 |
| 2 Build candidates | 5 controllers pass sanity checks | ~50 |
| 3 Tournament | winner on selection seeds, ablation (Gate B) | ~600 |
| 4 Confirmation | pre-registered result on seeds 103-119 | ~350 |
| 5 Scale and robustness | 6-10 APs, unseen cells, beacon-rate control (Gate C) | ~330 |
| 6 Optional | beyond-CW track (MAC change, needs approval), report | tbd |

## Compute (estimate; only 1 GitHub account and 2 Spaces on one account are measured)
- Non-learned jobs on Actions forks (byte-identical across platforms for statics, BEB, DAC, ucbctx; KW and GP search must pass the hash check first). Learner jobs on Spaces only.
- Pool of 8 accounts + 8 Spaces: roughly 300-600 lab-h per wall-hour (unverified). Pre-flight tests are listed in the full plan.
- GitHub terms allow one free account per person; the 8 accounts should belong to different people.

## Open decisions (user)
D1 headline (ceiling share vs RAFA minimax), D2 action space, D3 beyond-CW track, D4 account ownership.
