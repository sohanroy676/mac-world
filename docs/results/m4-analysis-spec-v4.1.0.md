# M4 analysis spec and re-plan: per-scenario RAFA (v4.1.0) - APPROVED 2026-11-11 (D1, D2; D3 default)

Date: 2026-11-11. Status: **approved by the user on 2026-11-11: D1 = per-scenario recipe claim, D2 = tune lambda per scenario; D3 = proposed default (not explicitly confirmed).** Committed before any M4 run. Launching any batch still needs the user's go-ahead, and the Section 6 blockers must clear first.
Labels: **fact** (read from repo), **decision** (proposed here), **inference**, **unknown**.
Replaces the M4 section of `docs/planning/mac-world-v4-plan.html` (rev 10), which assumed a pooled actor.

## 1. What changed (fact)
- Gate G3 failed (`m3-step3-results-v4.0.0.md`): pooled RAFA GC S2 0.522, S4 0.553, S5a 0.610 against per-scenario 0.730 / 0.968 / 0.775. RAFA is now **one shared-actor DDPG trained separately for each scenario** (lambda 1, 6 episodes, alpha input).
- The 6 pooled final seeds (2003-2008) were never trained. The plan's "two ensembles pass" rule had pooled ensembles in mind.
- RAFA's weak cells so far: S2 alpha 1 (CW saturates at 1024, GC 0.730, all 3 seeds) and S4 alpha 0 (GC 0.01 / -1.59 / 0.87 at 6 episodes). Lambda was chosen on S4 and S5a only.
- The code has no ensemble deployment (mean of 3 actors): `--loadActor` loads one actor set (`OSCAR_multi_ap_train.py:60,219`). **Unknown:** whether it exists elsewhere; if not, it is new code (small) and needs the `2,3` reference check.
- S7 and S8 have not been run for any rival yet (`m2-baselines-v3.7.0.md` limits). S8 needs the per-AP load schedule and per-phase static schedule (plan, "code only", assigned to M2b/M2c); another thread owns M2b, so this spec treats it as a dependency.

## 2. What the claims can and cannot say now (decision)
- Old Claim 1 ("one controller with no weak cell") is **not testable for RAFA**: a per-scenario policy is not one controller. It is restated as a statement about the **recipe**: *the same RAFA recipe (inputs, reward, lambda grid, 6 episodes), retrained per scenario, has no weak cell against rivals that are also trained or tuned per scenario.* Same fairness rule as the rivals (strongest seed, shared tuning budget).
- No generalisation claim (unseen AP counts, unseen scenarios). The pooled result is reported as a negative result with its numbers.
- Claim 2 (within 0.05 GC of the best feasible rival in every conclusive core cell) is unchanged in form; the per-scenario PF learner and CCOD are now the same kind of specialist as RAFA.
- Cost to be stated in the report: RAFA needs about 25-50 lab-minutes of training per scenario and seed, so deployment needs a training run per network.

## 3. Cells (fact from plan rev 10, unchanged)
13 core cells: S2, S4, S5a at alpha 0, 1 and max-min (alpha 4 input; **the alpha-4 oracle is still undetermined**, open M3 item, see Section 6); S7 two delay configs (GC_D on ln p99); S8 at alpha 1 and max-min.

## 4. RAFA arms and training design (decision, pending D1-D3)
- One RAFA actor per **scenario** (S2, S4, S5a, S7a, S7b, S8), not per (scenario, alpha): the alpha input serves alpha 0 / 1 / 4 inside a scenario, as in step 2. Training alpha mix as in step 2 (acting alpha per episode from {0, 0.5, 1, 2, 4}, relabelled batches).
- Tuning (D2): lambda picked per scenario on selection seeds 0-2 from {1, 3, 10}, 6 episodes, same rule as step 2 (feasible, highest mean alpha-1 GC). S4 and S5a already done (lambda 1); S2, S7a, S7b, S8 are new. Floors for the penalty need 10 Mbps BEB references for those scenarios (S2, S7, S8 do not have them: **unknown**, to be generated).
- Final training: python seeds **2003-2008** (disjoint from the step 1-3 seeds 2000-2002), 6 per scenario. **Ensemble A = 2003-2005, ensemble B = 2006-2008**, each deployed as the mean of 3 actions (needs the ensemble code from Section 1). Individual seeds are also reported.
- S7 (delay) and S8: RAFA keeps the throughput PF reward (no delay term). S7 therefore tests whether a throughput-trained policy also wins on p99 delay; labelled as such (D3).
- Platform: all RAFA and every learned rival on **one CPU vendor** (the HF Space, Xeon 8559C); non-learned arms (BEB, IdleSense, statics) may run on either platform (byte-identical, measured). CPU model logged per run.

## 5. Evaluation protocol (decision; stats unchanged from plan rev 10)
- Frozen actors, 30 s runs, 10 Mbps load. Stage 1 seeds 100-102 only select (strongest seed per rival, weakest cell). Confirmation seeds **103-109** (n = 7), extended to 110-119 where Stage-1 power < 80 %. RAFA's own selection stays on seeds 0-2.
- Rival strongest seeds come from M2c Stage 1 (`m2c-preregistration-v4.0.0.md`); M2b rivals (drlCW, Patras DAC, model-based static, contextual UCB) enter the same way. M4 does not start until M2b and M2c results are committed (dependency on the other thread).
- Metrics: GC per cell; fair floor 0.95 x min(BEB_i, BEB aggregate n_i / sum n); feasibility on the seed mean; degenerate-cell rule (gap < 3 BEB seed SDs -> raw U, 1 % margin, excluded from the worst-cell headline); S8 per-phase references summed over phases.
- Claim 1 test: for each rival, in that rival's weakest cell, one-sided paired t of RAFA minus rival, Holm over rivals, plus RAFA worst-cell GC above the rival's. Required for **both ensembles A and B**. Claim 2: intersection-union at 0.05 per cell. Wilcoxon shown unadjusted, descriptive only.
- Floor-slack sensitivity 0 / 5 / 10 % for every claim; threshold-dependent conclusions labelled so.
- Pre-registered expectation (written before any result): RAFA's weakest cells are S2 alpha 1 and S4 alpha 0 (Section 1). If after D2 tuning RAFA's worst-cell GC is below the best feasible rival's worst-cell GC, Claim 1 is reported as **not supported**, with the cell table.
- Kill/stop rules: any job failing `--check` (non-shared arms) or the per-AP CW readback is rerun, never dropped; a cell with a missing arm is not scored.

## 6. Open items that block M4 (fact / unknown)
1. S8 load schedule + per-phase static schedule code (ADR-0006 amendment); owner: M2b thread. **Unknown** if started.
2. Alpha-4 (max-min) oracle for S2, S4, S5a: needs a static grid on selection seeds (no RAFA code, cheap, non-learned, goes to Actions).
3. 10 Mbps BEB floors for S2, S7a, S7b, S8 for the penalty term.
4. Ensemble deployment code.
5. M2b and M2c results committed.

## 7. Compute (E = estimate from measured cell times; nothing here is measured for RAFA jobs on HF)
- Tuning (D2): lambda 3 and 10 for S2, and lambda x3 for S7a, S7b, S8 at 3 seeds: about 30 jobs x 0.6 h = about 18 lab-h (E).
- Final training: 6 scenarios x 6 seeds = 36 jobs x 0.6 h = about 22 lab-h (E; S8 episodes need 30 s to cover three phases, so it is heavier).
- Frozen evaluation: 2 ensembles x 13 cells x 7-17 seeds at about 12 min = about 36-88 lab-h (E; the plan's 32 h looks low once ensembles A and B are counted separately), plus individual seeds on S2, S4 at n = 3 (about 7 h).
- S7 and S8 for every rival: about 60 lab-h (plan), non-learned rivals on Actions, learned rivals on HF.
- Reserve for the power rule: about 10 lab-h.
- Total about 150-205 lab-h (E). At the measured combined rate of about 81 lab-h per wall-hour (E, learner cells at 16 on HF still **untested**) that is about 2-3 wall-hours, plus gating steps, so about 6-10 h wall in practice.

## 8. Decisions needed from the user
- **D1** Claim framing: restate Claim 1 as the per-scenario recipe (proposed), or first retrain a pooled RAFA with more episodes to keep the one-controller claim.
- **D2** Per-scenario lambda tuning on selection seeds for the new scenarios (proposed, same budget as rivals), or keep lambda 1 everywhere.
- **D3** S7/S8: RAFA keeps the throughput reward and is scored on delay (proposed), or add a delay reward for S7.
