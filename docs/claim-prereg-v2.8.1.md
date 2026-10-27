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

## Addendum A results (added 2026-10-25 after the 4 runs; all PASS `--check`, 839-864 s)
Tables and manifest: `docs/figures/v2.8.1/dev-shared-rs100/` (seed 10 is the diagnostic row, not part of the dev mean).

| Run | Shared, `--rewardScale 100` | Shared, scale 1 (earlier) |
|---|---|---|
| Dev seed 0 | 38.97 | 37.9 |
| Dev seed 1 | 38.13 | 27.6 |
| Dev seed 2 | 38.41 | 38.4 |
| Dev mean ± 95 % CI | **38.50 ± 1.06** | 34.62 ± 15.12 |
| Seed 10 (diagnostic) | **35.77** | 3.28 |

- Rule to go on to confirmation: met (no dev run below 10 Mbps, dev mean 38.5 ≥ 30).
- Seed 10 did not collapse. The actor again saturated, but on the other side: mean action +0.96, CW about 945 on all four APs, reward 0.0040, loss 0.55 (before: action −0.96, CW 17, reward 0.0003, loss 0.99).
- What this does and does not show: scaling changed the side the actor settled on in this one seed, which fits the hypothesis (critic initialisation, not reward, set the early drift), but it is one run and the unscaled baseline collapsed in only 1 of 8 seeds (10; seeds 0-2 and 11-14 did not), so n=1 is weak evidence that the stabiliser works. The scaled actor is still saturated at the CW bound (CW 480-950 in dev seeds), so the lock-in mechanism itself is not removed; whether CW near 1000 is a good operating point for other topologies is untested.
- Dev mean 38.5 vs the unscaled dev 34.6 and global 35.6 (n=3 each, tuning seeds): no claim. The dev spread (0.9 Mbps) is much smaller than unscaled (10.8 Mbps), but this is n=3.
- Status: confirmation on seeds 20-24 not started; it needs the user's go-ahead.

## Addendum A confirmation results (added 2026-10-27, seeds 20-24, 15,15,15,15; the rule above was not changed)
All 20 runs PASS `--check` (shared ×100 5/5, independent/beb/global 15/15; 860-1103 s). Tables: `docs/figures/v2.8.2/confirm-shared-rs100/`. Raw dirs local only (`results/bench-shared-rs100-confirm`, `bench-ref-confirm-s20`). Paired 95 % t-interval, n = 5; recomputed independently from `per_seed.csv` (same values).

| Mode | Aggregate Mbps (last 300 steps), seeds 20-24 | Mean ± 95 % CI |
|---|---|---|
| BEB | 26.98 / 27.35 / 28.40 / 27.53 / 27.55 | 27.56 ± 0.65 |
| Global (centralized) | 39.37 / 29.17 / 5.46 / 5.59 / 39.25 | 23.77 ± 21.30 |
| Independent (per-AP OSCAR) | 16.14 / 17.80 / 18.84 / 17.21 / 18.74 | 17.74 ± 1.40 |
| Shared ×100 | 37.11 / 36.86 / 39.07 / 37.05 / 36.97 | 37.41 ± 1.15 |

| Comparison | Δ Mbps | Seeds above | CI lower bound > 0? |
|---|---|---|---|
| **Primary: shared ×100 − independent** | **+19.67 ± 1.31** (+111 %) | 5/5 | **Yes** |
| shared ×100 − BEB (secondary) | +9.85 ± 0.67 (+35.7 %) | 5/5 | Yes |
| shared ×100 − global (secondary) | +13.64 ± 22.01 | 3/5 | No |

- Fact: the primary rule is met; shared ×100 also exceeds BEB with CI > 0 on these seeds. It is not shown to beat `global`.
- Fact: `global` collapsed to about 5.5 Mbps on seeds 22 and 23 (2/5); shared ×100 had no collapse (min 36.86). Jain 0.994 (shared), 0.991 (BEB).
- Fact: shared ×100 settles at CW about 850 on all four APs (last-100 mean), BEB at 16. Inference, untested: much of the gain may come from a high, fixed CW rather than from learned adaptation; a static-CW baseline (e.g. CW 850 for all APs) was not run, so "learns better than OSCAR" is not shown, only "higher throughput than per-AP OSCAR".
- Limit: one topology (15,15,15,15), n = 5, one `--rewardScale` value chosen on dev seeds 0-2 and the seed-10 diagnostic.

---

# Addendum B: static-CW control for shared ×100 (written 2026-10-27 BEFORE the runs below)

Question: is shared ×100's gain over per-AP OSCAR just a high fixed CW, or does the learned policy add something? Context (fact, from the Addendum A confirmation): shared ×100's last-100-step mean CW is 940-960 on seeds 20, 21, 23, 24 and about 470 on seed 22 (grand mean about 850), versus 16 for BEB.

Runs: new mode `--mode static --staticCw 850` (no agent; every AP gets cwMin = cwMax = 850 from step 1; `--check` on), 15,15,15,15, seeds 20-24, same settings as Addendum A. 5 runs. One CW value, fixed now (the grand mean); no sweep, no second value. Smoke (2 s, seed 20, PASS) shows cw_set = cw_ap = 850 on all APs.

Comparisons (paired by seed against the existing Addendum A runs, 95 % t-interval, n = 5):
- S1 shared ×100 − static850. Claim "the learned policy beats a fixed CW 850" only if the lower bound > 0.
- S2 static850 − independent, S3 static850 − BEB: reported; a claim only if the lower bound > 0.
- Reading rule, fixed now: if S1's CI includes 0 or is below 0, the Addendum A gain over per-AP OSCAR is not shown to need learning (a fixed CW does as well); the gain statement stays "higher throughput than per-AP OSCAR", not "better learned adaptation". If S1 > 0 with the lower bound > 0, learning adds something beyond a fixed CW 850 on this topology.

Not allowed after seeing results: other CW values presented as the baseline, dropping seeds, changing the metric. A failed `--check` may be rerun once with identical settings only for an infrastructure fault. A different static CW (e.g. 470 or 950) would be a new addendum and a new, separately reported run set.

## Addendum B results (added 2026-10-27, seeds 20-24, 15,15,15,15; the rule above was not changed)
All 5 static runs PASS `--check` (814-839 s); CW exactly 850 on every AP. Tables: `docs/figures/v2.8.2/confirm-static850/` (includes the Addendum A runs for pairing). Raw dir local only (`results/bench-static850-confirm`).

| Mode | Aggregate Mbps, seeds 20-24 | Mean ± 95 % CI |
|---|---|---|
| Static CW 850 (no agent) | 37.95 / 37.90 / 37.02 / 37.75 / 37.79 | 37.68 ± 0.47 |
| Shared ×100 (Addendum A) | 37.11 / 36.86 / 39.07 / 37.05 / 36.97 | 37.41 ± 1.15 |

| Comparison | Δ Mbps | Seeds above | CI lower bound > 0? |
|---|---|---|---|
| S1 shared ×100 − static850 | −0.27 ± 1.61 | 1/5 | No (CI includes 0) |
| S2 static850 − independent | +19.94 ± 1.73 | 5/5 | Yes |
| S3 static850 − BEB | +10.12 ± 1.10 | 5/5 | Yes |

- Fact: a fixed CW 850 with no agent matches shared ×100 (difference −0.27 ± 1.61) and also beats per-AP OSCAR and BEB on every seed. Static850 Jain 0.995, phy loss 0.533 (shared 0.994, 0.539).
- By the reading rule fixed above: S1's CI includes 0, so the Addendum A gain over per-AP OSCAR is **not shown to need learning**. The learned shared policy did not beat a fixed CW on this topology.
- Fact: shared ×100 settled on a per-seed CW of 940-960 (seeds 20, 21, 23, 24) and about 470 (seed 22); seed 22 was shared's best run (39.07) and the only seed where it beat static850 (+2.05 Mbps, single seed, not a claim).
- Limits: one topology, n = 5, one static value (850, the grand mean); other fixed CWs were not run, so the best fixed CW is unknown and could be higher or lower than 850. This addendum does not test whether a better-chosen fixed CW would beat shared.

---

# Addendum C: fixed-CW sweep (written 2026-10-27 BEFORE the runs below)

Question: after Addendum B (static 850 = shared ×100), is there a fixed CW that does better, i.e. is shared ×100 even near the best fixed operating point?

Runs: `--mode static` with `--staticCw` in {470, 650, 1024} (850 already run in Addendum B), 15,15,15,15, seeds 20-24, same settings and `--check`; 15 new runs, about 3.5 h. Values are fixed now: 470 ≈ shared's seed-22 CW, 650 and 1024 bracket the range (1024 is the trainer's upper clamp). No other values, no second round inside this addendum.

Comparisons (paired by seed with the existing shared ×100 and BEB runs, 95 % t-interval, n = 5), each static CW c ∈ {470, 650, 850, 1024}:
- C1(c) static c − shared ×100. "A fixed CW beats shared" only if a lower bound > 0. "Shared ×100 beats fixed CW c" only if an upper bound < 0.
- C2(c) static c − BEB, reported.
Four C1 comparisons, no multiplicity correction; all reported whatever the outcome. The best fixed CW is picked after seeing seeds 20-24, so its advantage is optimistic (selection on the same seeds); the sweep only characterizes the throughput-vs-CW curve on this topology and is not a confirmation of a tuned fixed CW. A confirmation of any best value would need fresh seeds.

Not allowed after seeing results: dropping CWs or seeds, relabeling the metric, adding CW values to this addendum. A failed `--check` may be rerun once, same settings, only for an infrastructure fault.

## Addendum C results (added 2026-10-27, seeds 20-24, 15,15,15,15; the rule above was not changed)
All 15 new runs PASS `--check` (821-957 s). CW 850 is the Addendum B set. Each CW's tables (paired against the Addendum A shared ×100 and BEB runs): `docs/figures/v2.8.2/confirm-static{470,650,850,1024}/`. Raw dirs local only (`results/bench-static{470,650,1024}-confirm`). Intervals recomputed from `per_seed.csv` (same values).

| Fixed CW | Aggregate Mbps (mean ± 95 % CI) | C1: static − shared ×100 | Seeds above shared | C2: static − BEB |
|---|---|---|---|---|
| 470 | 39.76 ± 0.09 | **+2.35 ± 1.22** | 5/5 | +12.20 ± 0.72 |
| 650 | 38.98 ± 0.27 | +1.57 ± 1.41 | 4/5 | +11.42 ± 0.91 |
| 850 | 37.68 ± 0.47 | +0.27 ± 1.61 | 4/5 | +10.12 ± 1.10 |
| 1024 | 36.28 ± 0.51 | −1.13 ± 1.66 | 0/5 | +8.72 ± 1.13 |

(Shared ×100: 37.41 ± 1.15; BEB 27.56 ± 0.65; per-AP OSCAR 17.74 ± 1.40. Addendum B printed shared − static850 as −0.27 ± 1.61 with 1/5 seeds above; the 4/5 here is the same comparison with the sign flipped, static − shared.)

- Fact: throughput falls monotonically with the fixed CW over 470-1024 (39.76 → 36.28), and every tested fixed CW beats BEB on all seeds (lower bound > 0) and per-AP OSCAR by a wide margin.
- Fact: the rule's threshold is met for one value: fixed CW 470 beats shared ×100 (+2.35 ± 1.22, 5/5, lower bound > 0). Fixed 650 and 850 are indistinguishable from shared; fixed 1024 is below it on 0/5 seeds (CI includes 0).
- Fact: no tested CW is shown to be worse than shared ×100 (the upper bound of C1 is above 0 everywhere).
- Fact: static 470 has the narrowest spread (±0.09) of any mode tested.
- Caveat: 470 is the lowest value tested, so the curve's optimum could lie below 470 (between 16 and 470); the sweep says nothing there. The best-of-four selection is on the same seeds, so +2.35 is optimistic and is not a confirmed result for tuned CW; confirming "fixed 470 > shared ×100" would need fresh seeds.
- Reading: on this topology a well-chosen fixed CW does at least as well as shared ×100 and beats it at CW 470, so the learned policy is not shown to add anything and its seed-to-seed CW (470-960) was not an optimized operating point. One topology, n = 5.

---

# Addendum D: fixed-CW sweep below 470 (written 2026-10-27 BEFORE the runs below)

Question: Addendum C found throughput rising as the fixed CW falls from 1024 to 470 (36.28 → 39.76 Mbps), with 470 the lowest value tested. Where is the optimum, and is it clearly above 470?

Runs: `--mode static --staticCw` in {100, 200, 300}, 15,15,15,15, seeds 20-24, same settings and `--check` as Addenda B/C; 15 new runs, about 3.5 h. Values fixed now; no other values and no second round inside this addendum.

Comparisons (paired by seed with the existing runs, 95 % t-interval, n = 5), for c ∈ {100, 200, 300}:
- D1(c) static c − static 470 (Addendum C). "A lower CW is better than 470" only if the lower bound > 0; "worse" only if the upper bound < 0.
- D2(c) static c − shared ×100. A fixed CW "beats the learned agent" only if the lower bound > 0 (as in Addendum C).
- D3(c) static c − BEB, reported.
Six primary-style comparisons (D1, D2 for three CWs) with no multiplicity correction; all are reported whatever the outcome.

Reading rule, fixed now: the sweep (100, 200, 300, 470, 650, 850, 1024) characterizes the throughput-vs-CW curve on this topology and seeds. The best value is picked on the same seeds, so its advantage is optimistic; any "tuned fixed CW beats shared ×100" statement needs a new, separately pre-registered confirmation on fresh seeds (not started, needs the user's go-ahead). If throughput keeps rising as CW falls to 100, the optimum is below 100 and is untested; no claim is made about CW values below the lowest one run.

Not allowed after seeing results: dropping CWs or seeds, changing the metric, adding CW values to this addendum. A failed `--check` may be rerun once, same settings, only for an infrastructure fault.
