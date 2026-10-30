# v3.4.0 Per-AP scenario: hidden-chain scenario and static gate

Status: scenario and tooling DONE and validated; static gate DONE (PASSED); n = 8 frozen-eval batch DONE (§4); paired static oracle at eval seeds 100-107 DONE (§4b). Plan: `docs/research-beat-oscar.md` §5 #7, #14, §6. Decision record: `docs/adr/0005-coarse-loss-matrix.md`.

Labels: **fact** = observed in a run or read from code; **inference** = reasoning, untested; **unknown** = needs a run.

## 1. Scenario (fact)
`10,10,10` with `--apHidden 1-3`: BSS1 and BSS3 cannot hear each other (200 dB between all their nodes), every other pair keeps 50 dB. BSS2 (middle) hears both. Equal load (150 Mbps per STA), simTime 15, stepTime 0.01, policy window = steps >= 300.

Validation (all runs, rebuilt binary):
- Regressions: `--nWifi=5` dry seed 1 = 10533 packets, `5,15` = 9000, gym smoke 10.59458. Traces of beb / global / independent / shared / static on `2,3` short are byte-identical to pre-change runs. `ceiling_sweep` v3.1.0 table and default `aggregate_bench` output regenerate unchanged.
- `10,10,10 --apHidden 1-3`, dry, 5 s: Association PASS (AP2's STAs finish by 1.55 s), Per-AP statistics PASS, Hidden-pair check PASS (hidden pair decoded 0 frames in both directions; BSS1 decoded 1947 frames from BSS2, BSS3 decoded 1782).
- Trainer `--check` PASS on `2,2,2 --apHidden 1-3` for beb, global, independent `--alpha 0`, independent / shared `--reward pf`, static, `--cwMinOnly`, `--apLoads 150,150,5`. `--reward pf --alpha 0.5` is rejected.
- `--apLoads 150,50,5`: app tx counts in ratio 150:50:5.
- Job time: one 15 s job at `10,10,10` takes about 430-545 s.

## 2. BEB in the scenario (fact, seed 0, n=1, no CI)
Per-AP 33.36 / 1.53 / 35.39 Mbps, aggregate 70.29, Jain 0.695. The middle AP is starved (hidden-node effect). Reference: the same 30 STAs in one collision domain are far lower in aggregate (not run at this size; the 2,2,2 control gave about 38 Mbps total vs 76 hidden).

## 3. Static gate (fact)
Static per-AP CWs, no learning (`ceiling_sweep_v3_1_0.py --grid chain3`, 14 settings, seed 0; then 4 settings at seeds 1 and 2). Tables: `docs/figures/v3.4.0-gate/`. Mean ± 95 % CI (Student t), n=3 unless noted.

| CW (AP1,AP2,AP3) | n | aggregate | per-AP | Jain | PF utility | min-AP |
|---|---|---|---|---|---|---|
| 64,64,64 | 1 | 75.91 | 36.56 / 2.85 / 36.49 | 0.72 | 8.25 | 2.85 |
| 256,256,256 | 3 | 62.86 ± 0.21 | 27.37 / 8.12 / 27.37 | 0.84 | 8.71 ± 0.01 | 8.12 ± 0.17 |
| 512,512,512 | 3 | 50.08 ± 0.14 | 20.18 / 9.71 / 20.20 | 0.92 | 8.28 ± 0.01 | 9.71 ± 0.10 |
| 256,128,256 | 3 | 59.46 ± 0.06 | 23.11 / 13.28 / 23.07 | 0.95 | 8.87 ± 0.01 | 13.28 ± 0.25 |
| 256,64,256 | 3 | 53.87 ± 0.37 | 17.33 / 19.17 / 17.37 | 1.00 | 8.66 ± 0.02 | 17.33 ± 0.29 |

Gate (paired by seed; best asymmetric minus best common, selected on the 3-seed means among settings run on all seeds):
- PF utility: 256,128,256 minus 256,256,256 = **+0.15 ± 0.02** (n=3).
- min-AP: 256,64,256 minus 512,512,512 = **+7.62 ± 0.27 Mbps** (n=3).

Decision rule (plan): asymmetric must beat the best common CW by more than the CI on PF utility or min-AP. **Met on both** (CIs exclude 0).

Limits and caveats:
- Fact: aggregate throughput is highest at a LOW common CW (64: 75.9, one seed) because the two hidden edges transmit freely, but that starves the middle AP (2.85 Mbps). The asymmetric gain is a fairness gain: aggregate falls from 62.9 (256 common) to 53.9-59.5.
- The PF gain is small in absolute terms (+0.15 in summed log-Mbps) and the static CIs are narrow because static runs have low seed variance (n=3). These intervals do not carry over to learned agents.
- The best settings were chosen from seed-0 data and then confirmed on seeds 1 and 2 (so the three-seed numbers are not fully free of selection). The grid is coarse (edges equal, 3 x 3 pairs); the true static optimum may be better.
- 64,64,64 and the other seed-0-only rows are n=1 (no CI).
- Inference: the best static asymmetric setting is an oracle upper reference for a per-AP learner on PF / min-AP. Global-CW cannot reach it with one CW (not yet measured here).
- Unknown: whether learned per-AP agents (independent, shared) find an asymmetric setting; whether they beat BEB and Global at n >= 8.

## 4. Frozen-eval batch, n = 8 (fact)
Protocol (`fair_protocol_v3_2_0.py`, `--topo 10,10,10 --trainerArgs "--apHidden 1-3"`): one policy per arm trained for **2** episodes (ns-3 seeds 1 and 1001, `--trainSeed 0`; 2 instead of 3 because of the time budget, the same as the 20,40 pilot), then evaluated frozen (noise 0, no training) on held-out python seeds 100-107 (ns-3 seeds 101-108). BEB ran on the same 8 seeds, so every comparison is paired by seed. Learner: DDPG, default settings, no `--rewardScale`. All 8 + 8 + 8 + 8 + 8 (BEB) eval jobs and 4 training jobs `--check` PASS. Policy window = steps >= 300. Tables, manifests, log: `docs/figures/v3.4.0/`. Mean ± 95 % CI (Student t); p = exact two-sided Wilcoxon signed-rank (n=8: the smallest possible p is 0.0078, reached when all 8 differences share a sign).

| Arm (frozen) | aggregate | AP1 / AP2 / AP3 | Jain | PF utility | min-AP | final CW (AP1/2/3) |
|---|---|---|---|---|---|---|
| BEB | 71.63 ± 0.62 | 34.95 / 1.44 / 35.24 | 0.694 | 7.48 ± 0.04 | 1.44 ± 0.07 | 16 / 16 / 16 |
| Global-CW | 76.46 ± 0.34 | 36.93 / 2.58 / 36.94 | 0.712 | 8.16 ± 0.07 | 2.58 ± 0.21 | 64 / 64 / 64 |
| independent `--alpha 0` | 68.77 ± 0.15 | 38.50 / 1.26 / 29.01 | 0.678 | 7.25 ± 0.05 | 1.26 ± 0.07 | 75 / 110 / 16 |
| independent `--reward pf` | 62.82 ± 1.18 | 24.76 / 9.99 / 28.07 | 0.877 | 8.84 ± 0.01 | 9.99 ± 0.54 | 208 / 41 / 77 |
| shared `--reward pf` | 73.43 ± 0.47 | 34.46 / 4.49 / 34.48 | 0.750 | 8.58 ± 0.06 | 4.49 ± 0.35 | 126 / 130 / 126 |

Paired differences (same seed), all p = 0.008, n = 8:

| Arm | vs BEB: Δ PF / Δ min-AP / Δ aggregate | vs Global: Δ PF / Δ min-AP / Δ aggregate |
|---|---|---|
| Global-CW | +0.69 ± 0.06 / +1.15 ± 0.19 / +4.84 ± 0.70 | n/a |
| independent `--alpha 0` | -0.23 ± 0.06 / -0.18 ± 0.08 / -2.86 ± 0.58 | -0.92 ± 0.05 / -1.32 ± 0.17 / -7.69 ± 0.24 |
| independent `--reward pf` | **+1.36 ± 0.04 / +8.56 ± 0.52** / -8.81 ± 1.31 | **+0.68 ± 0.08 / +7.41 ± 0.35** / -13.64 ± 0.87 |
| shared `--reward pf` | +1.10 ± 0.05 / +3.05 ± 0.32 / +1.80 ± 0.67 | +0.41 ± 0.02 / +1.90 ± 0.16 / -3.03 ± 0.21 |

Reading (fact unless marked):
- Frozen independent and shared agents trained with the cooperative PF reward beat BEB and Global-CW on PF utility and on the weakest AP, in all 8 seeds. Independent `--reward pf` lifts the starved middle AP from 1.44 (BEB) to 9.99 Mbps and its PF utility (8.84) is at the static oracle level (8.87 for the best static pair at 256,128,256; paired gap in §4b: -0.03 ± 0.01).
- The price is aggregate throughput. Independent pf is -8.8 Mbps vs BEB and -13.6 vs Global; shared pf is +1.8 vs BEB and -3.0 vs Global. Global-CW has the highest aggregate (76.46, same level as the static common CW 64: 75.91, n=1) but leaves the middle AP at 2.6 Mbps. Which arm is "better" depends on the objective: aggregate favours Global, PF and min-AP favour independent pf.
- Independent with the strictly local reward (`--alpha 0` here = network-goodput reward in this mode, as in the repo's earlier definition) is worse than BEB on all four metrics. A pure aggregate reward cannot see the starved AP (inference, consistent with the aggregate being highest at low CW).
- The independent-pf CWs separate per AP (208 / 41 / 77): the middle AP gets the lowest CW and the edge APs back off, qualitatively like the static asymmetric optimum (edges high, middle low), but the learned values differ from 256,64,256 (fact) and the AP1/AP3 CWs are not equal (fact).
- Frozen CWs are constant per run (CI ± 0 on the last-100 CW): the actor output is a function of a state that stays near-constant, so the frozen policy behaves like a fixed per-AP CW choice (inference).

Limits:
- Fact: one trained policy per arm (one `--trainSeed`, 2 training episodes). Policy-seed variance is NOT in these CIs; the CIs measure only variance over evaluation seeds. The very small CIs on frozen policies partly reflect that.
- Fact: `--reward pf` and the PF/min-AP metrics are aligned (the reward is a PF utility), so the PF advantage is expected; it is not a result about aggregate throughput. The reported claim is on fairness / PF, where per-AP agents with a cooperative reward beat the single common CW.
- Fact: no hyper-parameter tuning, no `--rewardScale`, no TD3 or `--cwMinOnly` arm were run (time budget). The static oracle was added later at eval seeds 100-107 (§4b).
- Fact: the scenario is one coarse topology (hidden edges, equal load); `--apLoads` was validated but not used in a batch.
- The "Global" arm here is the repo's Global-CW OSCAR with OSCAR's own reward (not PF).

## 4b. Paired static oracle at eval seeds 100-107 (fact)
Static per-AP CWs (`--mode static`, no learning) on the same 8 ns-3 seeds (101-108) as §4, so every comparison is paired by seed. 16 jobs (2 settings x 8 seeds), all `--check` PASS, 456-606 s each. Tables, manifest, log: `docs/figures/v3.4.0-oracle/` (the §4 numbers regenerate unchanged). The two settings were picked from the seed 0-2 gate (§3), so they are not selected on the eval seeds. Mean ± 95 % CI (Student t), exact Wilcoxon p = 0.008 for every row (n=8).

| Arm | aggregate | AP1 / AP2 / AP3 | Jain | PF utility | min-AP |
|---|---|---|---|---|---|
| static 256,128,256 | 59.58 ± 0.11 | 23.18 / 13.25 / 23.15 | 0.948 | 8.87 ± 0.00 | 13.25 ± 0.09 |
| static 256,64,256 | 53.90 ± 0.09 | 17.39 / 19.12 / 17.39 | 0.998 | 8.66 ± 0.01 | 17.37 ± 0.05 |

Paired gap, learned arm minus oracle (Δ PF utility / Δ min-AP Mbps / Δ aggregate Mbps):

| Arm | vs static 256,128,256 | vs static 256,64,256 |
|---|---|---|
| BEB | -1.39 ± 0.04 / -11.82 ± 0.06 / +12.04 ± 0.62 | -1.18 ± 0.04 / -15.93 ± 0.09 / +17.72 ± 0.64 |
| Global-CW | -0.71 ± 0.07 / -10.67 ± 0.20 / +16.88 ± 0.32 | -0.50 ± 0.07 / -14.78 ± 0.21 / +22.56 ± 0.37 |
| independent `--reward pf` | **-0.03 ± 0.01** / -3.26 ± 0.51 / +3.23 ± 1.13 | **+0.18 ± 0.01** / -7.37 ± 0.53 / +8.92 ± 1.22 |
| shared `--reward pf` | -0.29 ± 0.06 / -8.77 ± 0.32 / +13.85 ± 0.43 | -0.09 ± 0.06 / -12.88 ± 0.35 / +19.53 ± 0.52 |
| independent `--alpha 0` | -1.62 ± 0.05 / -11.99 ± 0.10 / +9.19 ± 0.18 | -1.41 ± 0.05 / -16.11 ± 0.08 / +14.87 ± 0.20 |

Reading (fact unless marked):
- The static oracle holds under paired evaluation: both asymmetric settings beat BEB and Global-CW on PF utility and min-AP in all 8 seeds. 256,128,256 is +1.39 ± 0.04 PF and +11.82 ± 0.06 Mbps min-AP over BEB, and +0.71 ± 0.07 PF and +10.67 ± 0.20 min-AP over Global. The price is aggregate throughput (-12.0 vs BEB, -16.9 vs Global).
- Independent `--reward pf` closes almost the whole PF gap: it is 0.03 ± 0.01 PF below 256,128,256 (small but nonzero, p = 0.008) and 0.18 ± 0.01 above 256,64,256. It does not reach the oracle's min-AP: -3.3 Mbps vs 256,128,256 and -7.4 vs 256,64,256. Its aggregate is higher than either oracle's (+3.2 / +8.9 Mbps), so it sits between the oracle and BEB on the fairness / throughput trade-off.
- Shared `--reward pf` is below the 256,128,256 oracle on PF (-0.29) and about level with 256,64,256 (-0.09 ± 0.06) but far lower on min-AP (-8.8 / -12.9 Mbps).
- Independent `--alpha 0` is far below both oracles on every fairness metric, consistent with §4.
- Inference: a PF reward gives per-AP learners an objective that the static asymmetric optimum also maximizes, so reaching about the oracle PF is expected. The best asymmetric static pair is an upper reference on PF only for this coarse grid (edges equal, 3 x 3 pairs, §3); it is not a proven global optimum, and a learned policy could in principle exceed it.
- Limit: the frozen-policy CIs still contain only evaluation-seed variance (one `--trainSeed`, §4 Limits). The static CIs are narrow because static runs have low seed variance.

## 4c. Second policy seed (`--trainSeed 1`) (fact)
Independent and shared `--reward pf` were retrained with `--trainSeed 1` (2 episodes, ns-3 seeds 2 and 1002, otherwise identical to §4) and evaluated frozen on the same 8 seeds (100-107). Train + 8 eval jobs per arm, all `--check` PASS (arms E, F; train 1087 s / 1072 s, eval 484-609 s). Tables and figures for all arms: `docs/figures/v3.4.0-seeds/` (the §4 and §4b numbers regenerate unchanged). Mean ± 95 % CI over the 8 eval seeds, exact Wilcoxon p = 0.008 unless noted.

| Arm | trainSeed | PF utility | min-AP | aggregate | final CW (AP1/2/3) |
|---|---|---|---|---|---|
| independent pf | 0 | 8.84 ± 0.01 | 9.99 ± 0.54 | 62.82 ± 1.18 | 208 / 41 / 77 |
| independent pf | 1 | 8.89 ± 0.02 | 11.62 ± 0.82 | 61.78 ± 0.68 | 218 / 123 / 251 |
| shared pf | 0 | 8.58 ± 0.06 | 4.49 ± 0.35 | 73.43 ± 0.47 | 126 / 130 / 126 |
| shared pf | 1 | 8.69 ± 0.05 | 7.30 ± 0.59 | 64.48 ± 0.40 | 241 / 242 / 240 |

Paired Δ (PF utility / min-AP Mbps) of trainSeed 1 against each reference:

| Arm (trainSeed 1) | vs BEB | vs Global | vs static 256,128,256 |
|---|---|---|---|
| independent pf | +1.41 ± 0.04 / +10.18 ± 0.80 | +0.73 ± 0.06 / +9.04 ± 0.62 | +0.02 ± 0.02 (p = 0.078) / -1.63 ± 0.80 |
| shared pf | +1.21 ± 0.05 / +5.86 ± 0.57 | +0.53 ± 0.03 / +4.71 ± 0.39 | -0.18 ± 0.05 / -5.96 ± 0.57 |

Policy-seed difference (trainSeed 1 minus 0, paired by eval seed; ΔPF / Δmin-AP / Δaggregate): independent pf +0.05 ± 0.02 / +1.63 ± 0.30 / -1.04 ± 0.51; shared pf +0.11 ± 0.02 / +2.81 ± 0.28 / -8.95 ± 0.15.

Reading:
- Fact: the ordering from §4 holds for both policy seeds. Both seeds of both PF arms beat BEB and Global on PF and min-AP in all 8 eval seeds, and independent pf stays above shared pf.
- Fact: the two policies differ. The final CWs are very different (independent: 208/41/77 vs 218/123/251; shared: 126 vs 241) and the policy-seed gaps (ΔPF, Δmin-AP) are larger than the eval-seed CIs. So the §4 CIs understate total uncertainty.
- Fact: independent pf with trainSeed 1 is level with the 256,128,256 oracle on PF (+0.02, p = 0.078) and closer on min-AP (-1.6 vs -3.3 Mbps for seed 0). The seed-0 "slightly below the oracle on PF" is therefore not stable across policy seeds.
- Fact: shared pf trainSeed 1 raised min-AP and PF but gave up 9 Mbps of aggregate versus seed 0 (it ends at about 241 on all three APs).
- Limit: two policy seeds are not a policy-seed CI. No statistics across trainSeeds are claimed; the eval-seed CIs above condition on one policy per row. A third seed was added in §4d.

## 4d. Third policy seed (`--trainSeed 2`) (fact)
Independent and shared `--reward pf` retrained with `--trainSeed 2` (2 episodes, ns-3 seeds 3 and 1003, otherwise identical to §4c; arms G, H) and evaluated frozen on eval seeds 100-107. 18 jobs, all `--check` PASS (train 1243 s / 953 s, eval 455-588 s). Tables and figures: `docs/figures/v3.4.0-seeds/` (log `batch-t2.log`); the existing A-F and oracle rows regenerate unchanged. Mean ± 95 % CI over the 8 eval seeds, exact Wilcoxon p = 0.008 unless noted.

| Arm | trainSeed | PF utility | min-AP | aggregate | final CW (AP1/2/3, last-100 mean) |
|---|---|---|---|---|---|
| independent pf | 2 | 8.60 ± 0.05 | 8.37 ± 0.66 | 59.49 ± 0.28 | 286 / 311 / 347 |
| shared pf | 2 | 8.71 ± 0.05 | 7.77 ± 0.63 | 63.68 ± 0.35 | 248 / 236 / 249 |

Paired Δ (PF utility / min-AP Mbps / aggregate Mbps) of trainSeed 2:

| Arm (trainSeed 2) | vs BEB | vs Global | vs static 256,128,256 |
|---|---|---|---|
| independent pf | +1.12 ± 0.05 / +6.93 ± 0.65 / -12.13 ± 0.69 | +0.44 ± 0.03 / +5.78 ± 0.47 / -16.97 ± 0.13 | -0.27 ± 0.05 / -4.89 ± 0.64 / -0.09 ± 0.25 (p = 0.383) |
| shared pf | +1.23 ± 0.05 / +6.33 ± 0.61 / -7.95 ± 0.73 | +0.54 ± 0.03 / +5.19 ± 0.43 / -12.78 ± 0.10 | -0.16 ± 0.06 / -5.48 ± 0.60 / +4.09 ± 0.31 |

Three policy seeds (descriptive; mean of the per-policy eval means, sample SD across the three policies, range; the t-interval with n = 3 uses t = 4.303 and is very wide):

| Arm | PF utility | min-AP (Mbps) | aggregate (Mbps) |
|---|---|---|---|
| independent pf | 8.78, SD 0.16, range 8.60-8.89 (t-CI ± 0.39) | 9.99, SD 1.63, range 8.37-11.62 (± 4.04) | 61.36, SD 1.70, range 59.49-62.82 (± 4.23) |
| shared pf | 8.66, SD 0.07, range 8.58-8.71 (± 0.17) | 6.52, SD 1.77, range 4.49-7.77 (± 4.41) | 67.20, SD 5.41, range 63.68-73.43 (± 13.45) |

Reading:
- Fact: for all three policy seeds, both PF arms beat BEB and Global on PF utility and min-AP in all 8 eval seeds (p = 0.008), and both stay below Global on aggregate throughput (Global 76.46). Against BEB (71.63) the aggregate is lower for every policy except shared pf trainSeed 0 (73.43).
- Fact: trainSeed 2 independent pf is the weakest independent policy: PF -0.27 ± 0.05 and min-AP -4.9 Mbps against the 256,128,256 oracle (p = 0.008). Its CWs ended high on all APs (286/311/347). So the trainSeed 0/1 result "close to or level with the oracle on PF" does not hold for every policy seed; only seed 1 was level (§4c).
- Fact: the independent-vs-shared ordering is not stable. On PF, independent beats shared for trainSeeds 0 and 1 (8.84 vs 8.58, 8.89 vs 8.69) but not for trainSeed 2 (8.60 vs 8.71, shared higher). On min-AP independent is higher for all three seeds (9.99 / 11.62 / 8.37 vs 4.49 / 7.30 / 7.77).
- Fact: policy-to-policy variation is larger than the eval-seed CIs for both arms. Independent min-AP spans 8.4-11.6 and shared aggregate spans 63.7-73.4.
- Inference: a claim about "independent beats shared" or "independent matches the oracle" needs more than three policies. The claim that survives all three is "PF reward beats BEB and Global on fairness, at an aggregate cost".
- Limit: three policies per arm, no policy-seed hypothesis test. One topology, one training length (2 episodes).

## 4e. TD3 and `--cwMinOnly` arms (`--trainSeed 0`) (fact)
Independent `--reward pf`, 2 training episodes, ns-3 seeds 1 and 1001, frozen eval on seeds 100-107. Arm I = `--algo td3`, arm J = `--cwMinOnly` (agent action sets CWmin only, CWmax stays 1023, BEB doubling kept). 18 jobs, all `--check` PASS (train 1029 s / 1006 s, eval 454-600 s). Tables and figures: `docs/figures/v3.4.0-algo/` (arms A, B, C, I, J and the oracle; the existing rows regenerate unchanged). Mean ± 95 % CI over 8 eval seeds; exact Wilcoxon p = 0.008 unless noted.

| Arm | PF utility | min-AP | aggregate | Jain | final CW (AP1/2/3) |
|---|---|---|---|---|---|
| independent pf, DDPG (arm B) | 8.84 ± 0.01 | 9.99 ± 0.54 | 62.82 ± 1.18 | 0.877 | 208 / 41 / 77 |
| independent pf, TD3 (arm I) | 8.78 ± 0.03 | 13.75 ± 0.69 | 57.66 ± 1.04 | 0.946 | 350 / 58 / 104 |
| independent pf, `--cwMinOnly` (arm J) | 8.39 ± 0.11 | 4.38 ± 0.61 | 68.42 ± 1.39 | 0.754 | 116 / 59 / 16 |

Paired Δ (PF utility / min-AP Mbps / aggregate Mbps):

| Arm | vs BEB | vs Global | vs static 256,128,256 |
|---|---|---|---|
| DDPG (B) | +1.36 ± 0.04 / +8.56 ± 0.52 / -8.81 ± 1.31 | +0.68 ± 0.08 / +7.41 ± 0.35 / -13.64 ± 0.87 | -0.03 ± 0.01 / -3.26 ± 0.51 / +3.23 ± 1.13 |
| TD3 (I) | +1.30 ± 0.06 / +12.31 ± 0.66 / -13.97 ± 1.14 | +0.61 ± 0.10 / +11.16 ± 0.49 / -18.81 ± 0.74 | -0.09 ± 0.03 / +0.49 ± 0.66 (p = 0.195) / -1.93 ± 1.01 (p = 0.016) |
| `--cwMinOnly` (J) | +0.92 ± 0.10 / +2.94 ± 0.58 / -3.21 ± 1.42 | +0.23 ± 0.05 / +1.80 ± 0.42 / -8.04 ± 1.09 | -0.48 ± 0.11 / -8.87 ± 0.57 / +8.83 ± 1.36 |

Reading:
- Fact: both variants beat BEB and Global on PF utility and min-AP in all 8 eval seeds (p = 0.008).
- Fact: TD3 reaches the oracle's min-AP (+0.49 ± 0.66, p = 0.195) and its Jain index (0.946 vs 0.948, p = 0.641) but sits 0.09 ± 0.03 PF below it; DDPG is closer on PF (-0.03) and lower on min-AP (-3.3). Different trade-off, not a uniform win.
- Fact: `--cwMinOnly` is the weakest PF arm: its outcome sits closest to BEB (aggregate -3.2 vs BEB, Jain 0.754, AP2 4.4 Mbps). Its last-100 CWmin is 116 / 59 ± 63 / 16 (AP3 at the floor, AP2 widely spread across eval seeds) and its convergence step is 660 ± 357 (the fixed-CW policies converge at 0). Why it is weaker was not tested.
- Limit: one `--trainSeed` per arm. §4c/§4d show policy-seed spread larger than these CIs (DDPG independent min-AP spans 8.4-11.6 over three seeds), so the TD3-vs-DDPG gaps above (min-AP +3.8, PF -0.06) are not shown to exceed policy-seed variation. The `--cwMinOnly` gap vs DDPG (-0.45 PF, -5.6 min-AP) is larger than any DDPG seed gap seen so far, but that is not a test.

## 4f. Uneven loads, `--apLoads 150,150,20` (fact, but it does NOT test what was intended)
Topology `10,10,10 --apHidden 1-3` with `--apLoads 150,150,20` (per-STA offered load in Mbps, so AP3 offers 10 x 20 = 200 Mbps). Arm K: BEB + independent pf (`--trainSeed 0`, 2 episodes, trained and evaluated in this load); static 256,128,256 as an a-priori reference (picked on the equal-load gate, not tuned here); eval seeds 100-107. 17 + 8 jobs, all PASS (eval 366-426 s). Tables: `docs/figures/v3.4.0-apload/`.

| Arm | aggregate | AP1 / AP2 / AP3 | PF utility | min-AP |
|---|---|---|---|---|
| BEB | 71.76 ± 0.42 | 35.28 / 1.36 / 35.12 | 7.42 ± 0.09 | 1.36 ± 0.13 |
| static 256,128,256 | 59.55 ± 0.08 | 23.15 / 13.26 / 23.13 | 8.87 ± 0.00 | 13.26 ± 0.09 |
| independent pf | 65.45 ± 1.61 | 30.66 / 5.03 / 29.75 | 8.43 ± 0.01 | 5.03 ± 0.35 |

- Fact: the BEB per-AP split (35.3 / 1.4 / 35.1) is the same as at equal load 150 (35.0 / 1.4 / 35.2, §2). AP3 still carries ~35 Mbps, so 20 Mbps per STA still saturates it. The load asymmetry is not binding, and this run is effectively a second equal-load replicate (different training and ns-3 randomness), not an uneven-load test.
- Fact: independent pf trained here gives PF +1.00 ± 0.09 and min-AP +3.67 ± 0.32 over BEB (p = 0.008), but -0.44 PF and -8.2 min-AP vs the static oracle. These numbers are within the policy-seed spread of §4c/§4d for the equal-load case, so they do not show a load effect.
- Inference: a real uneven-load check needs an AP that is not saturated, e.g. `--apLoads 150,150,1` (AP3 offers 10 Mbps in total). Not run.

## 5. Next
- Done: policy seeds 0-2 (§4c, §4d), TD3 and `--cwMinOnly` (§4e), `--apLoads` 150,150,20 (§4f, not informative).
- Open: a real uneven-load check with an unsaturated AP (e.g. `--apLoads 150,150,1`); a second policy seed for the TD3 / `--cwMinOnly` arms; v3.3.0 sensing + heuristics (IdleSense) as a non-RL baseline.
