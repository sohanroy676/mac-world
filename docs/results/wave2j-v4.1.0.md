# Wave 2j (v4.1.0): class B learner pilot

- Date: 2026-11-20. Image sha256:4149e56b..., 9 jobs (RAFA, Global, PF learner x S2/S4/S5a), 1 training seed (2000), one 60 s eval (seed 0). Runner CPU: Intel Xeon 6975P-C on pack 0 (others not checked).
- Outcome: Global and PF learner ran end to end (6/6 PASS). RAFA trained (3/3 PASS) but all 3 evals failed at start: the eval args carried `--floorLambda 1` without `--floors`, and the trainer asserts against that (fact, log: AssertionError at OSCAR_multi_ap_train.py:363). Cause was my batch, not the trainer. Fixed in `w2j_batch.py` (floors and lambda in training only); RAFA retrained and evaluated in Wave 2j2 (3 jobs, 3 lab-h), because the actors were not kept.

## Wall time (fact, one lane of a 4-lane runner)
| learner | train (sim s) | train wall | 60 s eval wall |
|---|---|---|---|
| Global (12 eps x 15 s) | 180 | 2,726 / 3,224 / 2,909 s (S2 / S4 / S5a) | 681 / 792 / 808 s |
| PF learner (12 x 15 s) | 180 | 2,615 / 2,109 / 4,958 s | 744 / 522 / 1,281 s |
| RAFA (6 x 15 s) | 90 | 1,442 / 1,054 / 2,781 s | not run (failed) |

Total for the 12 Global/PF steps: 6.5 lane-hours, against 6.2 predicted by the plan's w = 1.1 x sim seconds at 14 s per w. The cost model holds within about 5 % (fact), with PF S5a train (4,958 s) the one slow outlier.

## 1-seed eval (60 s, seed 0, alpha 1; thr_all in Mbps; floor check tol 0.05)
| cell | method | per-AP Mbps | U1 | feasible |
|---|---|---|---|---|
| S2 | Global | 13.38, 24.83 | -27.12 | yes |
| S2 | PF learner | 26.31, 13.22 | -38.80 | NO (AP2 13.22 < 17.19) |
| S4 | Global | 37.51, 2.05, 37.54 | 10.61 | yes |
| S4 | PF learner | 30.77, 7.88, 28.80 | 19.44 | yes |
| S5a | Global | 26.07, 13.65, 10.00 | 12.69 | yes |
| S5a | PF learner | 17.87, 20.91, 10.00 | 13.18 | yes |

One seed, no BEB or ceiling pairing in this wave: these are run-check numbers, not rankings (decision).

## Class B re-cost (inference from measured wall times)
- Plan cost stays about 800-1,000 lab-h (the rate check above supports it). At 1 lab-h = about 2,300 lane-seconds, that is roughly 580 lane-hours; with 3 packs x 4 lanes in parallel on one account that is about 48 h wall, plus queueing.
- Each learner job is long (0.7 to 2.4 h per lane). Jobs per pack must be kept at about 3 (as in the pilot) to fit a 6 h GitHub job limit with margin.
- Not yet decided: full class B scope (12 seeds each, best seed and top-3 mean per plan D4). Decision after RAFA results from 2j2.

## Wave 2j2 (RAFA rerun, 2026-11-20): all 3 evals PASS
| cell | per-AP Mbps (60 s, seed 0) | U1 | feasible | eval wall | train wall |
|---|---|---|---|---|---|
| S2 | 12.74, 23.65 (CW 1024, 1024) | -30.04 | yes | 776 s | 1,456 s |
| S4 | 36.49, 3.21, 36.48 | 14.53 | yes | 759 s | 1,066 s |
| S5a | 25.44, 13.89, 10.00 | 12.62 | yes | 818 s | 1,728 s |

- All 9 pilot jobs now train and evaluate (fact). Pilot goal met: trainers run at 60 s, actors reload, wall times measured.
- RAFA S2 saturates both CWs at 1024 (as M3 found); Global S2 U1 -27.12 and PF infeasible. Single seed, no ranking.
- Actors are kept in the pack bundle (release assets), so later tournament evals can reuse them (fact: run_job.py copies the actor dir into the bundle).

## Class B scope decision (2026-11-20, mine, within xyz's standing authorization)
- Follow plan D4 in stages. Stage 1 (Wave 2k): 12 training seeds (2000-2011) x 3 learners x S2/S4/S5a at alpha 1, each evaluated on 3 selection seeds (0-2, 60 s). 108 jobs, 237.6 lab-h by the w model (the pilot shows the model is within about 5 %), 6 packs in parallel, about 8 h wall.
- Stage 2 (later): pick best seed and top-3 per learner and cell on selection seeds; evaluate them on tournament seeds 300-309 (RAFA also at alpha 0 and 4 by `--fairAlpha`). Global/PF at alpha 0 and 4 need their own training (different reward), decided after stage 1.
- Correction: my earlier "about 56 lab-h" mental estimate was wrong; the batch generator's 237.6 is the figure.
