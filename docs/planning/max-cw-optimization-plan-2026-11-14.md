# Maximum contention window optimization: finalized plan (2026-11-14)

Status: **approved, implementation started 2026-11-14** (Track A on `claude/project-thread-o7nshg`, based on `feature/v4` 6dc82ca).
Full text: https://claude.ai/artifact/9GhjxwS5Men4fXNtTECVje, tab "Finalized plan" (private). The revision 1-3 tabs are superseded.
This file is the repo summary; where it and the full text differ, the full text wins.

## Goal
A deployable (online) controller reaches a measured ceiling in every cell; the distance to a bound is reported. Primary
metric: worst-cell ceiling share of the best online candidate, target 0.95 (hypothesis, not a guarantee).

## Ceiling (measured, per cell and alpha)
Best validated of three static families (ADR-0008):
- F1 exact static CW per AP, 4..32767, Gaussian-process batch search in 3 rounds.
- F2 static CWmin with doubling (`--cwMinOnly`); kept only if it beats F1 by 0.05 of the BEB-to-F1 gap on fresh seeds.
- F3 two-phase periodic schedule with a mute CW; kept only if Gate S passes.
Bounds: scheduled-access and independent-set bound per cell (self-check: 2:1:2 shares for the ideal chain).

## Controller (one writer per variable)
- L1 DAC loop writes CW. L2 "KW+" (common level + shrunk per-AP offsets, SPSA, accept/revert guard) writes L1 targets.
- L3 max-weight coordinator with virtual queues picks the active AP group, the others are muted (only if Gate S). Q-CSMA = local-information variant.
- L0 learned anchor: small attention model over AP tokens, trained on ceiling data (only if Gate L).

## Tournament
- Class A online: DAC, KW+ direct, Cascade, Coordinated, Q-CSMA, Anchored.
- Class B offline: static/schedule plan (reference), RAFA, PF learner, Global-CW; 12 seeds each, best seed and top-3 mean.
- Rivals: BEB, IdleSense, BLADE, original KW, contextual UCB, CCOD, drlCW, per-AP OSCAR, model-based static.

## Methodology
- Seeds: 0-3 search and tuning, 200-209 ceiling validation, 300-309 tournament, 103-122 (up to 142) confirmation.
- 60 s runs scored on 30-60 s (S8 whole run); the winner also at 300 s.
- Paired tests, margin 0.05 of the BEB-to-ceiling gap, Holm correction for rivals, n from tournament variance (min 20).
- Reproducibility: one pinned container image per commit, SHA-256 of every trace, 5 % replay on another account.

## Gates (fixed)
S schedule beats static on S4 by > 3 seed SDs and >= 0.05 of the gap, floor-feasible · A a cell is at its ceiling ·
Sanity per candidate · B selection rule (ties within 0.02 go to less shared information) · L the anchor helps S8 or
unseen-cell convergence · C the result holds at 102.4 ms updates with 2^k - 1 rounding.

## Build tracks and waves (lab-hours are estimates)
| Track | Contents | Ready before |
|---|---|---|
| A | pinned image, dispatcher, short packs, collector, exact-CW static mode, schedule mode, bounds script, search driver, Tc measurement | Wave 0 |
| B | controllers L1-L3, Q-CSMA, guard, change detector | Wave 2 |
| C | learned anchor, analysis and report code | Wave 3 |

| Wave | Purpose | Lab-h |
|---|---|---|
| 0 | rehearsal at about 1 % scale on every account | ~30 |
| 1 | ceilings, bounds, anchor training data | ~2,450 |
| 2 | sanity checks, tuning, learner training | 1,700-2,200 |
| 3 | tournament | ~700 |
| 4 | confirmation, scale, robustness | ~2,400 |
| 5 | reserve | <= 500 |

Decision (user, 2026-11-14): each wave is approved once with a lab-hour cap; batches inside an approved wave chain automatically.

## Compute
7 forks on other people's GitHub accounts carry the non-learned load; the main account dispatches and collects; Hugging
Face Spaces run learner work. Only one GitHub account and two Spaces on one account have been measured.

## Track A status
See `docs/design/measurement-modes-v4.1.0.md`.
