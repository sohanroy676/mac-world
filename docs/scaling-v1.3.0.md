# v1.3.0 — Scale to 6 APs (2026-10-15)

Branch `feature/v1.3.0-six-aps`. No ns-3 / cw.cc / trainer change: the code was already N-generic (fact, verified by the runs below).
Binary unchanged since Oct 12 (waf reported up to date). Topology 5,10,15,20,25,30 = 105 STAs + 6 APs = 111 nodes; fits the single /24 in `cw.cc:822`.
AP spacing is 50 m (`cw.cc:796-809`), so AP1 and AP6 are 250 m apart.

## 1. Validation (all PASS; seed 1, simTime 2 unless noted)

| Criterion | Command | Result |
|---|---|---|
| Single-AP regression | `--nWifi=5` dry | 10533 pkts |
| 2-AP regression | `--apStaCounts=5,15` dry | 9000 pkts |
| Gym smoke | `baseline_v0_1_0.py --smoke` | cumulative reward 10.59458 |
| 6 APs associate, per-AP stats | `--apStaCounts=2,3,4,5,6,7` dry | ok 2/3/4/5/6/7, wrongAp 0, Σ per-AP == global (8526 pkts), 75 s, 89 MB RSS |
| same, full size | `--apStaCounts=5,10,15,20,25,30` dry | all checks PASS, 6028 pkts, 278 s, 138 MB RSS |
| Per-AP CW | `2,3,4,5,6,7 --apCws=16,32,64,256,512,1024` | CW check PASS; throughput 13.8 / 10.9 / 7.2 / 2.2 / 1.3 / 0.59 Mbps (falls with CW) |
| Gym shapes | `test_multi_ap_gym.py --staCounts 2,3,4,5,6,7 --phases "0,1,2,4,5,6;6,5,4,2,1,0"` | readback == action per AP, both phases, RESULT PASS |
| Trainer small | `OSCAR_multi_ap_train.py --apStaCounts 2,3,4,5,6,7 ... --check` (30 steps) | PASS, 47 W&B keys/row, 110 s |
| Trainer full size | same flags, `5,10,15,20,25,30` | PASS, 47 keys/row, 6:19 wall, 365 MB RSS, no ZMQ stalls |

## 2. Long runs (5,10,15,20,25,30; seeds 0,1,2; 1500 steps; policy window = steps >= 300)
9/9 runs PASS incl. `--check`. Data: `docs/figures/v1.3.0/` (seed 0 only, n=1), `docs/figures/v1.3.0-b2/` (n=3, tables.md, 4 figures, manifest.csv).
Raw run dirs are NOT committed (`results/` stays gitignored). Mean ± 95% CI (Student t).

| Mode | Aggregate Mbps | Jain | Phy loss | Run time |
|---|---|---|---|---|
| BEB | 23.83 ± 1.15 | 0.865 ± 0.003 | 0.785 ± 0.012 | 1514-1631 s |
| Global-CW | 32.53 ± 12.48 | 0.784 ± 0.151 | 0.675 ± 0.173 | 1558-1631 s |
| Independent | 18.72 ± 19.75 | 0.678 ± 0.135 | 0.846 ± 0.236 | 1652-2617 s |

Paired vs BEB (same ns-3 seed): global +8.70 ± 12.00 Mbps (+36.4 ± 49.3 %), CI includes 0; independent -5.11 ± 19.38 Mbps (-21.6 ± 81.0 %), CI includes 0.

Per seed, aggregate Mbps (steps >= 300):

| Seed | BEB | Global | Independent | Independent last-300 steps |
|---|---|---|---|---|
| 0 | 23.33 | 29.50 | 17.84 | 10.42 |
| 1 | 24.06 | 36.10 | 27.36 | 26.45 |
| 2 | 24.15 | 28.75 | 15.56 | 9.97 |

- Fact: global beats BEB at all 3 seeds (+6.2, +12.0, +4.6 Mbps), but the paired t-CI includes 0 because seed 1's gap is much larger. No CI-supported global claim at 6 APs (n=3). Direction is consistent with 4 APs, 20,20 and 20,40.
- Fact: independent is bimodal across seeds. Seeds 0 and 2 decay to ~10 Mbps by step ~1100 and stay there (below BEB); seed 1 holds ~26 Mbps (above BEB). No claim vs BEB is supported.
- Fact (seed-0 CW traces): the six independent CWs diverge (final 25 / 96 / 540 / 17 / 47 / 111); global moves as one shared CW (~170 at the end).
- Fact: both trained modes have lower mean Jain than BEB; intervals are wide and overlap BEB's (unpaired, trend only).
- Unknown: why independent decays in 2 of 3 seeds; the "pinned near CW 16, more collisions" idea from v1.2.0 does not describe seed 0 (CWs diverge, not pinned). Untested.
- Unknown: why independent seed 1 took 2617 s vs ~1650 s for every other run; not investigated.

## 3. Scaling observations (facts)
- Runtime: ~26-28 min per 1500-step run, ~2.1x the 4-AP runs (716-850 s) for ~2.1x the STAs (105 vs 50). Predicted from the 4-AP ratio before the runs; matched.
- Memory: peak 365 MB RSS (full-size trainer check), 138 MB (dry run). Not a constraint.
- ZMQ: no stalls or errors in 9 x 1500 steps plus the checks.
- Metric correctness: per-AP Σ == global, CW readback and trainer `--check` PASS at 6 APs.

## 4. Open
t=1.144 s deassociation (deassoc count == re-assoc count in every run, every STA re-associates):

| Seed | BEB | Global | Independent |
|---|---|---|---|
| 0 | 2 | 2 | 5 |
| 1 | 0 | 1 | 0 |
| 2 | 3 | 2 | 0 |

Fact: BEB has events at 2 of 3 seeds, so at 6 APs this is not a trained-mode-only effect (as at 20,40 in v1.1.0). Cause still unproven.
Next: v1.4.0 (8 APs). Runtime extrapolation, unmeasured: ~35-40 min per run at ~140 STAs. Subnet budget: ~253 nodes total.
