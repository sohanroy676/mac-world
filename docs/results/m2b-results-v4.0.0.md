# M2b results: new rivals (Stage 1 drlCW, finals of dac / ucbctx / model-static)

Date: 2026-11-12. Specs and decisions: `m2b-specs-v4.0.0.md`. Labels: **fact** = measured here, **inference** = my reasoning.

## What ran (facts)
- **Actions, finals** (run 43213429631, 1.6 h wall): dac (Tc 514 us), ucbctx (c 1), model-static (Tc 257 us) on S2, S4, S5a, seeds 100-109, 18 jobs, all `--check` PASS. Data: `docs/figures/v4.0.0-m2b/finals/`. **Not scored**: the claims need BEB and the oracle statics on seeds 103-109, which belong to the M4 batch.
- **HF, drlCW:** 3 cells x 3 training seeds (300 s, python seeds 2000-2002), then frozen evals on seeds 100-102 (30 s). Reward uses the BEB-delay scaling chosen by xyz (2026-11-12).
  - First HF run (`m2b-batch2-hf`): 4 of 9 trainings passed, 5 failed `--check`. The two platform cross-check jobs (dac, ucbctx) finished; **their trace sha256 equals the Actions run's for both** (dac db9144dd..., ucbctx 766a5c38...; same args, 5 s S2, seed 100). Fact for these two runs: the non-learned dac and ucbctx are byte-identical across the Actions runner and the HF Space (CPU vendors of the Actions runners for those two jobs not checked here), so they may be run on either platform. Learner runs remain vendor-specific.
  - **Check bug, found twice (fact):** `cw.cc` (lines 498, 508) sets a history value to 0 when it is outside [-100, 100]. The raw loss goes negative when rx > tx in a step (down to -255 seen). The check compared raw loss with that zeroed observation. My first fix (clip to [0,1]) was wrong and failed every negative loss. The corrected rule (commit 245ccf7) explains all 459 failing lines of the 9 v2 trainings (0 unexplained, no other check type failed).
  - drlCW `per` is clipped to [0, 1] from commit 2eacec9 (the `m2b-batch2-hf-v2` trainings use it).
  - v2 trainings: all 9 ran 30000 steps and saved actors, but their logs still say `--check` FAIL (the old rule). Their evals (`m2b-batch2-hf-v2-eval`, 27 runs) all PASS `--check`. Trainings were not rerun to relabel them.
- Data: `docs/figures/v4.0.0-m2b/drlcw-v2/` (actors), `drlcw-v2-eval/` (eval runs), `gc_drlcw_s{2,4,5a}.md` (GC tables). Scoring: `gc_analysis.py --tagPrefix m2b-<cell>- --seeds 100-102 --alphas 0,1,4`, with the M2c BEB, IdleSense and oracle-static runs of the same seeds retagged.

## drlCW, Stage 1 (seeds 100-102, 5 % floor slack; GC = gap closed vs best feasible static)
| Cell | alpha | t0 | t1 | t2 |
|---|---|---|---|---|
| S2 | 0 | 0.892 ok | 0.979 INF | 0.624 INF |
| S2 | 1 | 0.776 ok | 0.577 INF | 0.273 INF |
| S2 | 4 | 0.638 ok | -1.948 INF | -3.156 INF |
| S4 | 0 | 2.030 INF | 1.075 ok | 1.747 INF |
| S4 | 1 | -0.523 INF | 0.369 ok | 0.034 INF |
| S4 | 4 (raw U, degenerate) | -34500 INF | -429 ok | -2401 INF |
| S5a | 0 | 1.009 INF | 1.013 INF | 1.041 INF |
| S5a | 1 | -1.537 INF | -0.744 INF | -2.175 INF |
| S5a | 4 (raw U) | -37.2 INF | -16.7 INF | -73.3 INF |

Selected seed (pre-registered rule, feasible first): S2 t0; S4 t1; S5a none feasible (infeasible at every seed and alpha).

## What the numbers say
1. **drlCW is floor-infeasible in S5a at every seed and alpha** (fact): one AP goes below 95 % of its BEB floor (min-AP 3.6 to 6.3 Mbps vs BEB 10 for the light AP).
2. **S2 and S4 have one feasible seed each**, and their GC at alpha 1 (0.776, 0.369) is below the M2c rivals (S2 Global 0.986, S4 PF 0.995; fact, different training seeds but same eval seeds).
3. Seed spread is large, as for the M2c learners (S2 alpha 1: 0.273 to 0.776).
4. Inference, untested: the paper's reward targets delay, our scaled delay reward does not penalise starving a light AP; this fits the S5a floor failures.

## Limits
- Stage 1 uses n = 3 eval seeds and no tuning (paper values), 3 training seeds. Claims use seeds 103-109 only (M4).
- drlCW trained on the HF Intel CPU, the M2c rivals on mixed Actions CPUs (effect unknown).
- BLADE not built (appendices unavailable). Tc 257 us is an inference, not measured.
- Not tagged.
