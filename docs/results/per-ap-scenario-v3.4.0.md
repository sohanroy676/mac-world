# v3.4.0 Per-AP scenario: hidden-chain scenario and static gate

Status: scenario and tooling DONE and validated; static gate DONE (PASSED). The n >= 8 frozen-eval batch is NOT run yet (needs approval). Plan: `docs/research-beat-oscar.md` §5 #7, #14, §6. Decision record: `docs/adr/0005-coarse-loss-matrix.md`.

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

## 4. Next
n >= 8 frozen-eval batch (`fair_protocol_v3_2_0.py --topo 10,10,10 --trainerArgs "--apHidden 1-3"`, eval seeds 100-107), split by arm: BEB, Global, independent `--alpha 0`, independent `--reward pf`, shared `--reward pf`, static oracle 256,64,256 / 256,128,256. Estimated about 7.5 h total (job time 430-545 s measured; training 3 episodes per learned arm). Needs approval per arm.
