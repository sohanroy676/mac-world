# v2.8.1 pre-registration: do coordinated variants beat per-AP OSCAR?

Written 2026-10-25, BEFORE any run in this document. Branch `feature/v2.8.0-coop-reward`. Definitions: `docs/coop-v2.8.0.md` §0 (per-AP OSCAR = `independent`; `global` = centralized single-agent baseline).

## Claim under test
A coordinated variant (shared-parameter, cooperative reward, central critic) gives higher aggregate throughput than vanilla OSCAR deployed per AP (`independent`).

## Data
- Seeds 10-14 only (never used for tuning). Same settings as the existing confirmation: simTime 15, step 0.01, 1500 steps, 150 Mbps per STA, metric = last-300-step aggregate Mbps (`tot_policy`), every run must pass `--check`.
- Reused, already run on seeds 10-14 at 15,15,15,15: beb, global, shared (`results/bench-shared-confirm`, `docs/figures/v2.8.0/confirm`). New runs: independent and coop at 15,15,15,15; beb, global, independent, central at 6x10 (`6,6,6,6,6,6,6,6,6,6`).
- Fixed settings: shared as in the confirmation; coop `--rewardMix 1` (best dev setting, default noise); central default reward scale (as in the 6x10 dev run).

## Primary comparisons (paired by seed, n = 5, 95 % t-interval, df = 4)
| ID | Topology | Delta |
|---|---|---|
| P1 | 15,15,15,15 | shared - independent |
| P2 | 15,15,15,15 | coop (L=1) - independent |
| P3 | 6x10 | central - independent |

Rule: a claim is made for a comparison only if the lower bound of its CI is > 0. Each is judged on its own; no multiplicity correction, so all three are reported whatever the outcome, and a single positive among three is called suggestive, not confirmed.

## Secondary (reported, no claim unless the CI lower bound > 0)
Each variant vs BEB and vs `global` on the same seeds. Also reported: seeds above independent (k/5), Jain index, minimum AP throughput, and collapses (< 10 Mbps aggregate).

## Not allowed after seeing results
Rerunning, replacing or dropping seeds, changing any parameter above, or switching metric. A failed `--check` run is reported and may be rerun once with the same seed and settings only for an infrastructure fault; the original failure is documented.

## Known limits
Only these two topologies; n = 5; shared collapsed at seed 10 in the earlier confirmation; `independent` has no seed 10-14 data yet; results may not transfer to other topologies.
