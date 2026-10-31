# v3.3.0 Sensing + heuristics: IdleSense baseline, residual RL, idle-slot observation

Status: tooling DONE and validated; target calibration DONE; n = 8 frozen-eval batch DONE (arms S, T, U). Plan: `docs/research-beat-oscar.md` §5 #4-#6, §6. Scenario and references: `docs/results/per-ap-scenario-v3.4.0.md` (`10,10,10 --apHidden 1-3`, eval seeds 100-107).

Labels: **fact** = observed in a run or read from code; **inference** = reasoning, untested; **unknown** = needs a run.

## 1. What was added (fact, project code only; all opt-in)
- `cw.cc` sensing: each AP's own radio PHY `State` trace (connected for the AP node only, so ADR-0002 isolation holds). An IDLE interval longer than 20 µs is a backoff gap; idle slots = floor((gap - 43 µs) / 9 µs) (43 µs = AIFS of BE = SIFS + 3 slots). Mean idle slots per gap is computed once per step and held when no gap occurred. It is the 7th field of the per-AP info record (`idle` in `parse_ap_info`).
- `--idleSense`: per-AP AIMD, once per step, on its own idle mean: idle < target gives CW += `--idleEps` (6), else CW *= `--idleAlpha` (0.9375); clamped 16..1024; MinCw = MaxCw. Starts at 16. Trainer `--mode idlesense` (runs with dryRun, so agent actions are ignored).
- `--residual`: the agent action a in 0..6 maps to CW = IdleSense CW x 2^clip(a - 3, -2, 2). Trainer `--residual` (independent/shared).
- `--obsIdle`: per-AP observation = min(1, idle mean / 20) instead of the loss ratio. Trainer `--obsIdle`.
- Runner `fair_protocol_v3_2_0.py --idleOnly` (IdleSense eval jobs, no training).
- Decision (not verified): the AIMD constants (eps 6, alpha 0.9375), the 20 µs gap threshold and the /20 observation scale are project choices. The Heusse et al. paper could not be fetched in this session (three URLs returned 404), so nothing here is claimed to match it. The target is calibrated on this PHY below instead of taken from the paper's 802.11b value 5.68. Bianchi / Kalman was not implemented.

Validation (fact): rebuilt `linear-mesh`; regressions unchanged: `--nWifi=5` dry seed 1 simTime 2 = 10533 packets, `5,15` = 9000, single-AP gym smoke cumulative reward 10.59458. Trainer `--check` PASS on `2,2,2 --apHidden 1-3` for beb, static `64,128,64`, idlesense, `--residual`, `--obsIdle` and both together. In the idlesense smoke the per-AP CWs moved independently (AP1 and AP3 18-36, AP2 up to 1024). Not validated: the idle count against an independent ground truth (only that the AIMD responds and the checks pass).

## 2. IdleSense target calibration (fact, seed 0, n = 1 per row)
`--mode idlesense`, python seed 0 (ns-3 seed 1; not one of the held-out eval seeds 100-107), 15 s. Tables: `docs/figures/v3.3.0-cal/`.

| target | aggregate | PF utility | min-AP |
|---|---|---|---|
| 3 | 79.03 | 4.83 | 0.08 |
| 5.68 | 77.80 | 6.83 | 0.62 |
| 8 | 73.75 | 7.33 | 1.15 |
| 12 | 66.65 | 7.76 | 2.27 |
| **20** | 54.74 | **7.95** | 4.50 |
| 30 | 43.88 | 7.78 | 7.03 |
| 50 | 36.77 | 7.46 | 9.12 |

Fact: PF utility peaks at target 20 (interior of the 3-50 sweep); target 20 was frozen for the batch. The paper's 5.68 gives PF 6.83, below BEB (7.48 over 8 seeds). AP2 (middle AP) ended at CW 1024 for targets 3-20 (the other two targets were not inspected).

## 3. n = 8 frozen evaluation (fact)
Same protocol as per-AP-scenario §4: eval seeds 100-107, paired by seed. Arm S: IdleSense, target 20, no training. Arms T and U: DDPG independent, `--reward pf`, 2 training episodes, `--trainSeed 0`, with `--residual --idleTarget 20` (T) or `--obsIdle` (U). 26 jobs, all `--check` PASS (train 947 s / 968 s, eval 446-698 s). Tables and figures: `docs/figures/v3.3.0/` (BEB, Global, the oracle and independent pf regenerate unchanged). Mean ± 95 % CI; exact Wilcoxon p = 0.008 unless noted.

| Arm | aggregate | PF utility | min-AP | Jain | final CW (AP1/2/3) |
|---|---|---|---|---|---|
| BEB | 71.63 ± 0.62 | 7.48 ± 0.04 | 1.44 ± 0.07 | 0.694 | 16 / 16 / 16 |
| Global-CW | 76.46 ± 0.34 | 8.16 ± 0.07 | 2.58 ± 0.21 | 0.712 | 64 / 64 / 64 |
| static 256,128,256 | 59.58 ± 0.11 | 8.87 ± 0.00 | 13.25 ± 0.09 | 0.948 | 256 / 128 / 256 |
| independent pf, loss obs (§4, seed 0) | 62.82 ± 1.18 | 8.84 ± 0.01 | 9.99 ± 0.54 | 0.877 | 208 / 41 / 77 |
| S: IdleSense, target 20 | 55.18 ± 0.37 | 7.88 ± 0.08 | 4.07 ± 0.42 | 0.768 | 420 / 1024 / 420 |
| T: residual pf | 55.05 ± 1.00 | 8.55 ± 0.01 | 10.98 ± 1.18 | 0.905 | 556 / 256 / 256 |
| U: pf, idle obs | 62.33 ± 0.73 | 8.87 ± 0.02 | 11.00 ± 0.76 | 0.893 | 137 / 104 / 303 |

Paired Δ (PF utility / min-AP Mbps / aggregate Mbps):

| Arm | vs BEB | vs Global | vs static 256,128,256 |
|---|---|---|---|
| S IdleSense | +0.40 ± 0.07 / +2.64 ± 0.39 / -16.45 ± 0.68 | **-0.29 ± 0.02** / +1.49 ± 0.22 / -21.28 ± 0.11 | -0.99 ± 0.08 / -9.18 ± 0.39 / -4.40 ± 0.33 |
| T residual pf | +1.07 ± 0.04 / +9.54 ± 1.16 / -16.58 ± 1.23 | +0.38 ± 0.06 / +8.39 ± 0.99 / -21.41 ± 0.69 | -0.32 ± 0.01 / -2.28 ± 1.17 / -4.54 ± 0.95 |
| U pf, idle obs | +1.40 ± 0.04 / +9.57 ± 0.74 / -9.30 ± 0.93 | +0.71 ± 0.05 / +8.42 ± 0.56 / -14.14 ± 0.41 | +0.01 ± 0.02 (p = 0.250) / -2.25 ± 0.74 / +2.74 ± 0.69 |

Reading:
- Fact: IdleSense, a decentralised non-RL heuristic, beats BEB on PF (+0.40) and min-AP (+2.64) in all 8 seeds, but is worse than Global-CW on PF (-0.29), far below the static oracle and far below the PF-reward learner, with the lowest aggregate except the static settings. It drives the middle AP's CW to the 1024 clamp (AP2 sees both edge APs and so little idle time, so its idle mean stays under the target at any target tried), the opposite of what the oracle does (low CW for the middle AP).
- Inference: an idle-slot regulator assumes one collision domain; in a hidden chain the middle AP's local idle count says "busy" for reasons that raising its CW cannot fix. So IdleSense is a reasonable baseline against BEB, not a competitor to the PF learner in this scenario. Not tested on a single-domain topology in this version.
- Fact: residual RL (T) is worse than the plain independent pf learner of the same policy seed on PF (8.55 vs 8.84) and has low aggregate. Final CWs are 556 / 256 / 256. Inference (untested): the +-2 range around the IdleSense CW, which pushes AP2 toward 1024 on its own, limits what the agent can do. It still beats BEB and Global on PF and min-AP in all 8 seeds. The residual claim "removes the random warm-up and shrinks the search space" was not shown to help here.
- Fact: idle-slot observation (U) gives PF 8.87 ± 0.02, level with the static 256,128,256 oracle (+0.01 ± 0.02, p = 0.250) and min-AP 11.00. These values lie inside the spread of the loss-observation DDPG policies over three policy seeds (PF 8.60-8.89, min-AP 8.4-11.6, per-ap-scenario §4d). Not shown to be better.
- Limit: one policy seed per learned arm; policy-seed spread exceeds the eval-seed CIs, so T vs U vs loss-observation ordering is not established. Calibration of the target used n = 1. One topology, one load, 2 training episodes.
- Unknown: whether `--obsIdle` helps in single-domain topologies or under uneven loads; the effect of eps / alpha; Bianchi.

## 4. Next
- Optional: `--trainSeed 1`, `2` for T and U (about 1.4 h per arm) before any ranking; IdleSense on a single-domain topology (20,40) as the case it was designed for.
