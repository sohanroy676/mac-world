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

---

# Results (added 2026-10-25, after all runs; the rule above was not changed)

All 30 new runs PASS `--check` (independent 15x4 5/5, coop 15x4 5/5, 6x10 beb/global/independent/central 20/20; 866-1146 s each). BEB, global and shared at 15,15,15,15 are the earlier confirmation runs. Tables and figures: `docs/figures/v2.8.1/confirm-15x4/`, `confirm-6x10/`. Raw run dirs are local only (`ns-3.29/scratch/linear-mesh/results/bench-{indep,coop}-confirm`, `bench-6x10-confirm`, `bench-shared-confirm`).

## Primary comparisons (paired by seed, n = 5, 95 % t-interval)
| ID | Comparison | Δ Mbps | Δ % | Seeds above independent | CI lower bound > 0? |
|---|---|---|---|---|---|
| P1 | shared − independent, 15,15,15,15 | +7.62 ± 15.84 | +40.1 ± 92.7 | 4/5 | **No** |
| P2 | coop (L=1) − independent, 15,15,15,15 | +8.10 ± 8.61 | +48.3 ± 53.9 | 5/5 | **No** (lower bound about −0.5) |
| P3 | central − independent, 6x10 | +9.29 ± 7.73 | +65.0 ± 51.0 | 5/5 | **Yes** (lower bound about +1.6) |

By the rule fixed above, one positive of three is **suggestive, not confirmed**. P3 replicates the untuned seeds-0-2 result (+15.1 ± 10.4). No multiplicity correction was applied; P2 and P3 are not separable from chance at the strength a three-way claim would need.

## Aggregate Mbps (last 300 steps), mean ± 95 % CI, seeds 10-14
| Topology | BEB | Global (centralized) | Independent (per-AP OSCAR) | Coop L=1 | Shared | Central |
|---|---|---|---|---|---|---|
| 15,15,15,15 | 27.85 ± 0.65 | 32.94 ± 11.01 | 20.14 | 28.24 | 27.76 ± 19.04 | - |
| 6x10 | 27.59 ± 0.18 | 33.53 ± 8.30 | 14.40 ± 2.51 | - | - | 23.69 ± 8.29 |

(The unlabeled spreads are in the generated `tables.md`.)

## Secondary comparisons (no claim unless CI lower bound > 0)
| Comparison | Δ Mbps | Seeds above | Claim? |
|---|---|---|---|
| 15x4 global − independent | +12.80 ± 14.03 | 4/5 | no |
| 15x4 coop − global | −4.70 ± 12.96 | 1/5 | no |
| 15x4 shared − global | −5.18 ± 25.04 | 1/5 | no |
| 15x4 coop − BEB | +0.39 ± 9.34 | 2/5 | no |
| 15x4 shared − BEB | −0.09 ± 18.50 | 3/5 | no |
| 6x10 global − independent | +19.13 ± 9.38 | 5/5 | yes (centralized beats per-AP OSCAR) |
| 6x10 global − BEB | +5.94 ± 8.21 | - | no |
| 6x10 central − global | −9.84 ± 7.43 | 0/5 | yes, in the wrong direction (central is worse) |
| 6x10 central − BEB | −3.90 ± 8.15 | 1/5 | no |
| 6x10 independent − BEB | −13.19 ± 2.53 | 0/5 | yes, independent is worse than BEB |

Collapses (< 10 Mbps aggregate): shared 1/5 at 15x4 (seed 10, 3.28 Mbps); none in any other mode or in 6x10.

## What can be said
- Fact: per-AP OSCAR (`independent`) is clearly below BEB at 6x10 (−13.2 ± 2.5) and has no gain over BEB at 15x4 (20.1 vs 27.9).
- Fact: the centralized baseline `global` beats per-AP OSCAR at 6x10 (+19.1 ± 9.4, 5/5). It does not beat BEB with CI > 0 at n=5 in either topology.
- Fact: the only coordinated decentralized-actor variant with a CI above 0 against per-AP OSCAR is central (6x10). It remains below global (−9.8 ± 7.4) and not above BEB.
- Fact: coop and shared are above independent on average at 15x4 (5/5 and 4/5 seeds) but their CIs include 0.
- Not shown: any variant beating BEB or global with CI > 0. No claim of "beats OSCAR" in the sense of the original single-agent design is supported; `global` is not original OSCAR and is not decentralized.

## Shared seed-10 collapse (read-only inspection of `trace.csv`, Task 4)
- Fact: the warm-up (steps 1-300) looks the same in seeds 10, 12 and 14 (mean CW about 230, reward about 0.0035, loss about 0.69).
- Fact: after learning starts at step 300, in seed 10 the shared actor moves steadily down: mean action −0.22 (step 301-320), −0.53, −0.74, −0.85, −0.92, then stays at about −0.96 (CW about 17, all four APs) until step 1500. Reward falls from 0.0036 to 0.0003 and loss rises to 0.99. In seeds 12 and 14 the actor moves up (+0.10 to +0.68 and +0.27) and reward stays about 0.0043.
- Fact: in seed 10 about 70 % of actions have |a| > 0.95 after step 350; critic loss is about 1e-5 and actor loss about ±0.003 from step 400, so there is almost no learning signal left. The exploration noise (std 0.1, clipped to [−1, 1]) is one-sided at the boundary.
- Inference, untested: the sign of the first actor updates differs by seed and decides which side of the action range the actor ends in. Once in the low-CW region the observed loss is about 0.99 for every step, so the one-scalar state carries no information and the critic cannot show a better action; the policy stays there. Whether a larger reward scale or a lower actor learning rate would avoid it is unknown; no run tests this. Shared logs no Q values, so the critic direction was not measured.
- Consequence for any stabiliser: it would be designed after looking at seed 10, so seeds 10-14 would no longer be untouched. Tuning would need seeds 0-2 and a new confirmation on fresh seeds (for example 20-24), including new independent runs on those seeds.

## Limits
Two topologies; n = 5; central only at 6x10 (central collapsed at 4..40 and 22x10 in earlier runs); the 15x4 independent mean of 20.14 is the same as the dev-seed mean by coincidence; one run per cell; 15 s simulated; single channel.

---

# Addendum A: stabiliser test for shared (written 2026-10-25 BEFORE the runs below)

Hypothesis (inference, untested): replay rewards are about 0.004, so Q differences are about 0.01 while a fresh critic's output varies by about 0.1; early actor gradients are then dominated by critic initialisation, which would explain why the first actor drift goes up or down depending on the seed (shared seed 10 locked at CW 17). Test: scale the replay reward by 100 (`--mode shared --rewardScale 100`; one value fixed now, no sweep; the same value stopped the central collapse at 22x10 in n=1..3).

Code: `--rewardScale` now also multiplies the replay reward of coop/shared (default 1: shared short-run trace byte-identical to before, `--check` PASS with 100).

## Runs now (15,15,15,15, 4 runs, about 1 h)
- **Dev, seeds 0-2** (tuning seeds). Reference: shared x1 dev 37.9 / 27.6 / 38.4 (34.62 ± 15.12).
- **Mechanism check, seed 10, one run.** Seed 10 was already inspected, so this is a diagnostic only and never counts as confirmation. Reported either way: does the actor avoid the CW-17 lock-in (last-300 mean action above −0.9 and aggregate above 10 Mbps)?

## Rule to go on to confirmation
Proceed only if no dev run is below 10 Mbps AND the dev mean is at least 30 Mbps. Otherwise stop and record a negative result.

## Confirmation (needs the user's go-ahead, not started)
Fresh seeds 20-24, 15,15,15,15: shared x100, independent, beb, global (20 runs, about 5 h). Primary: shared x100 − independent, paired 95 % t-interval, n = 5, claim only if the lower bound is above 0. Secondary (no claim unless CI > 0): vs beb and vs global. Nothing else may be changed after seeing seeds 20-24.
