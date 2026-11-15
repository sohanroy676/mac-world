# v3.3.0 Sensing + heuristics: IdleSense baseline, residual RL, idle-slot observation

Status: tooling DONE and validated. **Sections 2-3 (arms S, T, and the target-20 calibration) measure an IdleSense-style variant, not the published rule; the corrected results are in §3b.** The idle-observation arm U in §3 is unaffected and repeated at 3 policy seeds in §3b. Plan: `docs/research-beat-oscar.md` §5 #4-#6, §6. Scenario and references: `docs/results/per-ap-scenario-v3.4.0.md` (`10,10,10 --apHidden 1-3`, eval seeds 100-107).

Labels: **fact** = observed in a run or read from code; **inference** = reasoning, untested; **unknown** = needs a run.

## 1. What was added (fact, project code only; all opt-in)
- `cw.cc` sensing: each AP's own radio PHY `State` trace (connected for the AP node only, so ADR-0002 isolation holds). An IDLE interval longer than 20 µs is a backoff gap; idle slots = floor((gap - 43 µs) / 9 µs) (43 µs = AIFS of BE = SIFS + 3 slots). Mean idle slots per gap is computed once per step and held when no gap occurred. It is the 7th field of the per-AP info record (`idle` in `parse_ap_info`).
- `--idleSense`: per-AP AIMD, once per step, on its own idle mean: idle < target gives CW += `--idleEps` (6), else CW *= `--idleAlpha` (0.9375); clamped 16..1024; MinCw = MaxCw. Starts at 16. Trainer `--mode idlesense` (runs with dryRun, so agent actions are ignored).
- `--residual`: the agent action a in 0..6 maps to CW = IdleSense CW x 2^clip(a - 3, -2, 2). Trainer `--residual` (independent/shared).
- `--obsIdle`: per-AP observation = min(1, idle mean / 20) instead of the loss ratio. Trainer `--obsIdle`.
- Runner `fair_protocol_v3_2_0.py --idleOnly` (IdleSense eval jobs, no training).
- **CORRECTION (2026-10-31, after reading the paper; the section above is superseded by this):** the paper (Heusse et al., SIGCOMM 2005, Fig. 6, read from the official PDF) uses a different rule from what `--idleSense` implements. Paper: after `maxtrans` = 5 own transmissions, n̂ = mean idle slots; if n̂ < target, CW <- 1.2 x CW (multiplicative increase, 1/alpha = 1.20); otherwise CW <- 2 CW / (2 + eps CW) with eps = 0.001 (additive decrease of the attempt probability). Target = e^-z / (1 - e^-z) with 1 - z = eta e^-z, eta = 1 - Tslot/Tc (5.68 for 802.11b, 3.91 for 802.11g). This code: updates every 10 ms step, CW += 6 when n̂ < target and CW x 0.9375 otherwise, i.e. a different controller (additive increase of CW, multiplicative decrease). So arm S and the calibration below measure an **IdleSense-style variant, not Heusse's algorithm**, and the conclusion "IdleSense loses to Global and pins the middle AP at 1024" is not shown for the real algorithm. Fix and rerun are pending (needs a `cw.cc` change, so not while a batch runs). The residual arm T starts from this variant's CW, so it is affected too; the idle-observation arm U does not use the AIMD and is not.
- Other decisions (project choices, not from the paper): the 20 µs gap threshold, the idle count excluding 43 µs of AIFS, and the /20 observation scale. Bianchi / Kalman was not implemented (its 2000 paper returned 403).

Validation (fact): rebuilt `linear-mesh`; regressions unchanged: `--nWifi=5` dry seed 1 simTime 2 = 10533 packets, `5,15` = 9000, single-AP gym smoke cumulative reward 10.59458. Trainer `--check` PASS on `2,2,2 --apHidden 1-3` for beb, static `64,128,64`, idlesense, `--residual`, `--obsIdle` and both together. In the idlesense smoke the per-AP CWs moved independently (AP1 and AP3 18-36, AP2 up to 1024). Not validated: the idle count against an independent ground truth (only that the AIMD responds and the checks pass).

## 2. IdleSense target calibration of the step-based variant (fact, seed 0, n = 1 per row; superseded by §3b)
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

## 3. n = 8 frozen evaluation of the variant (fact; arms S and T superseded by §3b, arm U still valid)
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

## 3b. Corrected results with the published Idle Sense rule (fact; supersedes arms S and T above)
Code: `--idleSense` now follows Heusse et al. Fig. 6 (update every `--idleMaxTrans` = 5 observed attempts, x`--idleUp` 1.2 when idle < target, else CW <- 2 CW / (2 + `--idleEps` CW), eps 0.001; state in `apPhyState`, written to the BSS once per step). Regressions unchanged (10533 / 9000 packets, smoke 10.59458). Target: the paper's formula e^-z/(1-e^-z) with 1 - z = eta e^-z, eta = 1 - T_slot/T_c. T_c is estimated for this PHY (HE, 20 MHz, HeMcs11, 0.8 us GI; data airtime + SIFS + ACK + slot, about 214 us, so T_c/T_slot about 24), range 15-24 gives 2.6-3.3; **3.3 was fixed before any result** (inference: the T_c estimate is approximate, not measured). 55 jobs, all `--check` PASS. Tables and figures: `docs/figures/v3.3.1/` (sensitivity: `docs/figures/v3.3.1-sens/`). Mean ± 95 % CI over eval seeds 100-107; exact Wilcoxon p = 0.008 unless noted.

| Arm | PF utility | min-AP | aggregate | final CW (AP1/2/3) |
|---|---|---|---|---|
| BEB | 7.48 ± 0.04 | 1.44 ± 0.07 | 71.63 ± 0.62 | 16 / 16 / 16 |
| Global-CW | 8.16 ± 0.07 | 2.58 ± 0.21 | 76.46 ± 0.34 | 64 / 64 / 64 |
| static 256,128,256 | 8.87 ± 0.00 | 13.25 ± 0.09 | 59.58 ± 0.11 | 256 / 128 / 256 |
| IdleSense (paper rule, target 3.3) | **6.68 ± 0.11** | 0.53 ± 0.06 | **78.12 ± 0.04** | 106 / 963 / 107 |
| residual PF, trainSeed 0 / 1 / 2 | 7.93 ± 0.09 / 8.19 ± 0.13 / 6.57 ± 0.12 | 2.09 / 2.99 / 0.49 | 75.36 / 72.86 / 77.00 | AP2: 242 / 371 / 1017 |
| PF + idle observation, trainSeed 0 / 1 / 2 | 8.87 ± 0.02 / 8.70 ± 0.05 / 8.92 ± 0.03 | 11.00 / 9.20 / 9.97 | 62.33 / 60.61 / 64.97 | AP2: 104 / 239 / 101 |

Paired Δ PF utility (min-AP Mbps in brackets):

| Arm | vs BEB | vs Global | vs static 256,128,256 |
|---|---|---|---|
| IdleSense | -0.80 ± 0.11 (-0.91) | -1.49 ± 0.10 (-2.05) | -2.19 ± 0.11 (-12.72) |
| residual seed 0 | +0.45 ± 0.08 (+0.65) | -0.23 ± 0.03 (-0.49) | -0.94 ± 0.09 (-11.16) |
| residual seed 1 | +0.71 ± 0.12 (+1.55) | +0.03 ± 0.06, p = 0.312 (+0.41, p = 0.016) | -0.68 ± 0.13 (-10.26) |
| residual seed 2 | **-0.91 ± 0.11** (-0.95) | -1.60 ± 0.11 (-2.09) | -2.30 ± 0.12 (-12.76) |
| idle-obs seed 0 | +1.40 ± 0.04 (+9.57) | +0.71 ± 0.05 (+8.42) | +0.01 ± 0.02, p = 0.250 (-2.25) |
| idle-obs seed 1 | +1.22 ± 0.05 (+7.77) | +0.54 ± 0.03 (+6.62) | -0.17 ± 0.05 (-4.05) |
| idle-obs seed 2 | +1.45 ± 0.04 (+8.53) | +0.76 ± 0.05 (+7.38) | +0.05 ± 0.03, p = 0.016 (-3.28) |

Target sensitivity (seed 0, n = 1 each, `docs/figures/v3.3.1-sens/`): target 2.6 gives PF 5.22 / min-AP 0.12 / aggregate 79.59; 5.68 gives 7.45 / 1.34 / 72.91 (3.3 has n = 8 only: 6.68). AP2's CW is 960-990 in all three.

Reading:
- Fact: the faithful IdleSense has the **highest aggregate of any arm (78.12, +6.5 over BEB, +1.7 over Global)** and the **worst fairness**: AP2 gets 0.53 Mbps (BEB 1.44), PF is below BEB in all 8 seeds, AP2's CW sits near the 1024 limit while the edge APs run at about 106. So the §3 conclusion ("pins the middle AP, loses to Global on PF") survives the correction, but the earlier variant was gentler (PF 7.88, aggregate 55) and its target had been tuned for PF; with the paper's rule, PF depends strongly on the target (5.22 to 7.45 for 2.6 to 5.68 on one seed), unlike the paper's insensitivity claim for one collision domain.
- Inference (untested): AP2 hears both hidden edge APs, so its idle count says "heavily contended" at any CW it can choose; the heuristic reads a locally correct number and reaches a globally unfair state. This is the hidden-node failure the PF reward fixes (§4 of the per-AP report).
- Fact: residual RL on the paper's rule is unstable across policy seeds: it beats BEB in seeds 0 and 1 (+0.45, +0.71), ties Global in seed 1, and falls below BEB in seed 2 (-0.91, AP2 CW 1017, i.e. it follows the heuristic). It is below the plain loss-observation PF learner (PF 8.60-8.89, per-ap-scenario §4d) in all three seeds. Not shown to help; the heuristic prior here sets a poor starting point.
- Fact: the idle-slot observation (arm U) beats BEB and Global on PF and min-AP in all 3 policy seeds (p = 0.008), and sits at or just below the static oracle on PF (+0.01, -0.17, +0.05) with min-AP 2.3-4.1 Mbps under it. Mean PF 8.83 vs 8.78 for the loss-observation DDPG policies and min-AP 10.06 vs 9.99; the seed spread is similar, so **no advantage over the loss observation is shown**.
- Limit: 3 policy seeds per learned arm, no policy-seed test; hidden chain only; T_c estimated; sensitivity runs n = 1.

## 3c. IdleSense on a single collision domain, `20,40` (fact)
Where Idle Sense was designed to work. `--topo 20,40` (no `--apHidden`, 150 Mbps per STA, 15 s), eval seeds 100-107 (ns-3 seeds 101-108), paired by seed. IdleSense: published rule, **target 3.3 unchanged from the hidden-chain batch (no tuning here)**, no training. Global-CW: DDPG, default settings, 2 training episodes, `--trainSeed 0`, frozen. BEB on the same seeds. 25 jobs, all `--check` PASS (eval 826-860 s, Global training about 1770 s). Tables and figures: `docs/figures/v3.3.1-20-40/`. Mean ± 95 % CI; exact Wilcoxon p.

| Arm | aggregate (Mbps) | AP1 / AP2 | PF utility | min-AP | Jain | final CW |
|---|---|---|---|---|---|---|
| BEB | 27.66 ± 0.40 | 9.35 / 18.31 | 5.14 ± 0.05 | 9.35 ± 0.87 | 0.902 | 16 / 16 |
| Global-CW | 38.65 ± 0.40 | 12.79 / 25.86 | 5.80 ± 0.04 | 12.79 ± 1.06 | 0.896 | 276 / 276 |
| IdleSense (target 3.3) | **38.77 ± 0.21** | 12.84 / 25.93 | 5.80 ± 0.04 | 12.84 ± 1.06 | 0.896 | 366 / 366 |

Paired Δ (aggregate Mbps / PF utility / min-AP Mbps):

| Arm | vs BEB | vs Global-CW |
|---|---|---|
| Global-CW | +10.99 ± 0.20 (+39.7 ± 1.0 %) / +0.66 ± 0.02 / +3.44 ± 0.35 (p = 0.008) | n/a |
| IdleSense | +11.10 ± 0.35 (+40.2 ± 1.8 %) / +0.67 ± 0.03 / +3.49 ± 0.40 (p = 0.008) | +0.11 ± 0.25 (p = 0.312) / +0.01 ± 0.01 (p = 0.195) / +0.05 ± 0.09 (p = 0.250) |

Reading:
- Fact: with a single collision domain the corrected IdleSense, a decentralised non-RL heuristic with no training, **matches Global-CW within noise** on aggregate, PF and min-AP (all paired p > 0.19) and beats BEB by +40 % in all 8 seeds. Both land at nearly the same operating point (about 38.7 Mbps); the CWs end at 366 (IdleSense) vs 276 (Global-CW).
- Fact: this is the same target (3.3, derived from the paper's formula with an estimated T_c) that failed on the hidden chain, so the hidden-chain failure (§3b) is not a bad target; it is the topology. This also supports the derived target and the implementation.
- Context (inference, not paired): the v3.1.0 best static common CW (512) reached 39.62 ± 0.21 Mbps on seeds 0-2 (`docs/results/ceiling-v3.1.0.md`), about 0.9 Mbps above both arms here; different seeds, so not tested.
- Consequence for the project: the earlier claim "RL global CW beats BEB by about 30 %" (report §20-21) is also reached by a heuristic with no learning in this topology; the RL arms show an advantage only where the heuristic's assumption (one collision domain) breaks, i.e. the hidden chain with a PF reward.
- Limit: one topology and load, one Global-CW policy seed, no Bianchi baseline, T_c estimated.

## 4. Next
- Done: IdleSense on `20,40` (§3c).
- Not done: Bianchi / Kalman baseline (the 2000 paper was not retrievable); IdleSense constants other than the paper's (eps 0.001, 1/alpha 1.2, maxtrans 5).
