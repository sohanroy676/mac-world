# v1.4.0 — Scale to 8 APs (2026-10-16)

Branch `feature/v1.4.0-eight-aps`. No ns-3 / cw.cc / trainer change (fact: all checks below pass on the unchanged binary).
Topology 5,10,15,20,25,30,35,40 = 180 STAs + 8 APs = 188 nodes; fits the single /24 in `cw.cc:822` (254 usable).
AP spacing is 50 m (`cw.cc:796-809`), so AP1 and AP8 are 350 m apart.

## 1. Validation (all PASS; seed 1, simTime 2 unless noted)

| Criterion | Command | Result |
|---|---|---|
| Single-AP regression | `--nWifi=5` dry | 10533 pkts |
| 2-AP regression | `--apStaCounts=5,15` dry | 9000 pkts (2520 + 6480) |
| Gym smoke | `baseline_v0_1_0.py --smoke` | cumulative reward 10.59458 |
| 8 APs associate, per-AP stats | `--apStaCounts=2,3,4,5,6,7,8,9` dry | ok 2/3/.../9, wrongAp 0, all checks PASS, 7723 pkts, 2:08, 100 MB RSS |
| same, full size | `--apStaCounts=5,10,...,40` dry | all checks PASS, 4724 pkts, 9:07, 211 MB RSS |
| Per-AP CW | `2..9 --apCws=16,32,64,128,256,512,1024,16` **`--dryRun=false`** | CW check PASS; pkts 768 / 641 / 503 / 259 / 128 / 65 / 28 for CW 16..512; AP8 (CW 16) 3403 |
| Gym shapes | `test_multi_ap_gym.py --staCounts 2..9 --phases "0,1,2,3,4,5,6,0;6,5,4,3,2,1,0,6"` | readback == action per AP, both phases, RESULT PASS, 2:25, 322 MB |
| Trainer small | `OSCAR_multi_ap_train.py --apStaCounts 2..9 ... --check` (30 steps) | PASS, 61 W&B keys/row, 3:05, 367 MB |
| Trainer full size | same flags, `5..40` | PASS, 61 keys/row, 11:56, 367 MB, no ZMQ/timeout lines |

Note: `--apCws` is ignored when `--dryRun=true` (v0.5.0). An initial CW run with dryRun produced the default-CW packet counts and was discarded.

## 2. Long runs (5,10,...,40; seeds 0,1,2; 1500 steps; policy window = steps >= 300)
9/9 runs PASS incl. `--check`. Data: `docs/figures/v1.4.0/` (tables.md, 4 figures, manifest in `docs/figures/v1.4.0/`).
Raw run dirs and logs are NOT committed (`results/` stays gitignored). Mean ± 95% CI (Student t).

| Mode | Aggregate Mbps | Jain | Phy loss | Run time |
|---|---|---|---|---|
| BEB | 20.05 ± 0.94 | 0.855 ± 0.130 | 0.827 ± 0.012 | 2733-3068 s |
| Global-CW | 27.99 ± 17.20 | 0.815 ± 0.053 | 0.732 ± 0.219 | 2924-3796 s |
| Independent | 12.54 ± 18.74 | 0.674 ± 0.104 | 0.907 ± 0.197 | 3006-3326 s |

Paired vs BEB (same ns-3 seed): global +7.94 ± 18.08 Mbps (+40.1 ± 92.7 %), CI includes 0; independent -7.51 ± 19.48 Mbps (-37.1 ± 96.8 %), CI includes 0.

Per seed, aggregate Mbps (steps >= 300):

| Seed | BEB | Global | Independent | Independent last-300 steps |
|---|---|---|---|---|
| 0 | 20.06 | 24.66 | 6.82 | 6.09 |
| 1 | 19.66 | 35.95 | 21.09 | 20.55 |
| 2 | 20.42 | 23.36 | 9.71 | 10.44 |

- Fact: global beats BEB at 3/3 seeds (+4.6, +16.3, +2.9 Mbps) but the paired CI includes 0 (seed 1 dominates). No CI-supported global claim at 8 APs (n=3). Direction matches 4 and 6 APs.
- Fact: independent is below BEB at seeds 0 and 2 and slightly above at seed 1 (+1.4 Mbps); no claim vs BEB is supported. As at 6 APs, seed 1 is the good seed for independent.
- Fact: BEB per-AP throughput rises with STA count (AP1 0.84 -> AP8 3.90 Mbps), i.e. the per-AP share is roughly proportional to its STAs, while per-STA it is flat/declining. CW stays at 16.
- Fact (cw_traces.png, mean over seeds): global moves as one shared CW, ending ~2^8; the independent CWs diverge (AP4 rises to ~2^9, AP1/AP2/AP7/AP8 sit near 2^6).
- Fact: both trained modes have lower mean Jain than BEB; intervals overlap BEB's (unpaired, trend only).
- Fact: the per-seed spread of global (23.4-36.0) is far larger than BEB's (19.7-20.4).
- Unknown: why independent is low in 2 of 3 seeds (not tested; same open question as v1.3.0).

## 3. Scaling observations (facts)
- Runtime: BEB 2733-3068 s, global 2924-3796 s, independent 3006-3326 s (46-63 min). 6 APs was 1514-1676 s (2617 s once), so ~1.8-2.3x for 1.7x the STAs. The ~50 min extrapolation held. No outlier run beyond global seed 0 (3796 s, unexplained).
- Trainer `--check` full size: 11:56 vs 6:19 at 6 APs.
- Memory: 211 MB (dry), 367 MB (trainer). Not a constraint.
- ZMQ: no stalls or errors in 9 x 1500 steps plus the checks.
- Metric correctness: per-AP sum == global, CW readback, gym readback and trainer `--check` PASS at 8 APs.
- Node budget: 188 of 254 usable addresses; 10 APs need re-checking in v1.5.0 (e.g. 5..50 would be 275 STAs, over the /24).

## 4. Open
t=1.144 s deassociation (deassoc count == re-assoc count in every run, every STA re-associates; events at t=1.144 s in parentheses):

| Seed | BEB | Global | Independent |
|---|---|---|---|
| 0 | 2 (2) | 4 (4) | 8 (8) |
| 1 | 5 (3) | 14 (13) | 9 (7) |
| 2 | 1 (0) | 4 (4) | 5 (5) |

Fact: BEB has events at all 3 seeds, so this is not a trained-mode-only effect; counts are higher in trained modes and scale up from 6 APs (BEB 2/0/3 there). Cause still unproven.
Next: v1.5.0 (10 APs). Node budget must be checked before choosing a split (the /24 limit is ~253 nodes).
