# v1.5.0 — Scale to 10 APs (2026-10-16)

Branch `feature/v1.5.0-ten-aps`. No ns-3 / cw.cc / trainer change (fact: binary unchanged, `./waf build --target=linear-mesh` was a no-op, binary newer than `cw.cc`).
Topology 4,8,12,...,40 = 220 STAs + 10 APs = 230 nodes; fits the single /24 in `cw.cc:822` (254 usable).
Decision (user): the 5,10,...,50 split (275 STAs) does not fit the /24, so the 10-AP split is 4,8,...,40 (no code change). Addresses in `cw.cc` are derived from the interfaces, so widening is a later one-line change if needed.
AP spacing is 50 m, so AP1 and AP10 are 450 m apart.

## 1. Validation (seed 1, simTime 2 unless noted)

| Criterion | Command | Result |
|---|---|---|
| Single-AP regression | `--nWifi=5` dry | 10533 pkts |
| 2-AP regression | `--apStaCounts=5,15` dry | 9000 pkts |
| Gym smoke | `baseline_v0_1_0.py --smoke` | cumulative reward 10.59458 |
| 10 APs small, dry | `--apStaCounts=2,3,...,11` | association ok all 10 APs, wrongAp 0; stats + CW checks PASS; 6877 pkts; 3:36; 112 MB RSS |
| Per-AP CW | same, `--apCws=16,32,64,128,256,512,1024,16,32,64` **`--dryRun=false`** | CW check PASS; association PASS; 4926 pkts; throughput falls with CW 16..1024 (2.28 .. 0.05 Mbps); 2:56; 129 MB |
| Gym shapes | `test_multi_ap_gym.py --staCounts 2..11` two 10-entry phases | RESULT PASS; 3:02; 322 MB |
| Trainer small | `OSCAR_multi_ap_train.py --apStaCounts 2..11 ... --check` (30 steps) | PASS, 75 W&B keys/row; 3:57; 368 MB |
| Trainer full size | same flags, `4..40` (30 steps) | PASS, 75 keys/row; 13:41; 478 MB; no ZMQ/timeout lines |
| 10 APs full size, dry, simTime 2 | `--apStaCounts=4,8,...,40` | **association check FAIL** (see §3); stats + CW PASS; 4035 pkts; 10:22; 318 MB |
| same, simTime 5 | | association check **FAIL** (AP10 37/40); stats + CW PASS; 8677 pkts; 20:58; 377 MB |

Note: `--apCws` is ignored when `--dryRun=true` (v0.5.0); the CW run used `--dryRun=false`.

## 2. Long runs (4,8,...,40; seeds 0,1,2; 1500 steps; policy window = steps >= 300)
9/9 runs PASS incl. `--check`. Data: `docs/figures/v1.5.0/` (tables.md, 4 figures, manifest.csv). Raw run dirs and logs are NOT committed (`results/` stays gitignored). Mean ± 95% CI (Student t).

| Mode | Aggregate Mbps | Jain | Phy loss | Run time |
|---|---|---|---|---|
| BEB | 19.24 ± 1.85 | 0.856 ± 0.046 | 0.835 ± 0.020 | 3223-3705 s |
| Global-CW | 27.04 ± 15.20 | 0.846 ± 0.068 | 0.741 ± 0.192 | 3631-4011 s |
| Independent | 9.00 ± 6.16 | 0.634 ± 0.345 | 0.945 ± 0.053 | 4131-4315 s |

Paired vs BEB (same ns-3 seed): global +7.80 ± 16.04 Mbps (+41.0 ± 83.9 %), CI includes 0; independent -10.24 ± 4.33 Mbps (-53.5 ± 27.6 %), **CI excludes 0**.

Per seed, aggregate Mbps (steps >= 300):

| Seed | BEB | Global | Independent | Independent last-300 steps |
|---|---|---|---|---|
| 0 | 18.53 | 25.83 | 6.49 | 5.67 |
| 1 | 19.18 | 33.68 | 9.05 | 8.75 |
| 2 | 20.01 | 21.62 | 11.45 | 11.39 |

- Fact: global is above BEB at 3/3 seeds (+7.30, +14.50, +1.61 Mbps) but the paired CI includes 0 (seed 1 dominates). No CI-supported global claim at 10 APs (n=3). Direction matches 4, 6 and 8 APs.
- Fact: independent is below BEB at 3/3 seeds (-12.04, -10.13, -8.56 Mbps) and the paired CI excludes 0. First CI-supported independent-vs-BEB result in the scaling series; at 6 and 8 APs independent was bimodal and its CI included 0.
- Fact: independent has the lowest Jain (0.634) and the highest phy loss (0.945). Per-AP throughput is low for most APs (AP1 0.19 ... AP10 0.96 Mbps) with wide spread across seeds.
- Fact (cw_traces.png, mean over seeds): global moves as one shared CW (about 2^8 at the end); the independent CWs diverge (about 2^6.5 to 2^8.3 at the end of the seed-mean plot).
- Fact: BEB CW stays at 16; BEB per-AP throughput roughly follows STA count (AP1 0.56 -> AP10 2.70 Mbps, wide CIs).
- Unknown: why independent is low at all 3 seeds (not tested; same open question as v1.3.0/v1.4.0). Not tested whether seeds beyond 3 change the independent picture.

## 3. Association and deassociation (new at 10 APs)
Fact: the full-size 10-AP dry run fails the end-of-run association check at simTime 2 and 5 (`Association check: FAIL`, wrongAp 0 throughout):

| | run end | AP6 | AP9 | AP10 |
|---|---|---|---|---|
| simTime 2 | 3.21 s | 23/24 | 28/36 | 21/40 |
| simTime 5 | 6.21 s | 24/24 | 36/36 | 37/40 |

- Fact: STAs associate late under load (passive scanning, `ActiveProbing=false`, `cw.cc:775`); the 8-AP full size (180 STAs) passed the same 2 s check.
- Fact: at simTime 5, 7 AP10 STAs deassociated at t=3.432 s; 3 were still unassociated at 6.21 s.
- Inference, not proven: the first failure is late association under a saturated channel. The cause of the burst at 3.432 s is unknown.
- Fact: nothing in the Python tooling (trainer, runner, summarizer, gym test) reads association, so `--check` and benchmark PASS do not imply every STA was associated. Decision (user, option 1): keep 4..40 and report association events per run instead.

Long-run deassociation events (deassoc == re-assoc in every run, so every STA that dropped came back; events at t=1.144 s in parentheses):

| Seed | BEB | Global | Independent |
|---|---|---|---|
| 0 | 11 (3) | 11 (11) | 27 (27) |
| 1 | 4 (0) | 16 (14) | 22 (20) |
| 2 | 3 (1) | 23 (23) | 15 (8) |

Fact: BEB has events at all 3 seeds, so this is not a trained-mode-only effect; counts are higher in the trained modes. Cause still unproven. The end-of-run association state was not recorded for the long runs (the runs use the trainer, which does not print the association summary); only drop/re-association events are in the logs.

## 4. Scaling observations (facts)
- Runtime: BEB 3223-3705 s, global 3631-4011 s, independent 4131-4315 s (54-72 min). 8 APs was 2733-3796 s, so about 1.1-1.3x for 1.22x the STAs. The 1.5-2 h per-run extrapolation was too high.
- Trainer `--check` full size: 13:41 vs 11:56 at 8 APs.
- Memory: 318 MB (dry, simTime 2), 377 MB (dry, simTime 5), 478 MB (trainer). Not a constraint.
- ZMQ: no stalls or errors in 9 x 1500 steps plus the checks.
- Metric correctness: per-AP sum == global, CW readback, gym readback and trainer `--check` PASS at 10 APs.
- Node budget: 230 of 254 usable addresses. Going beyond 10 APs / 244 STAs needs a wider subnet in `cw.cc:822`.

## 5. Open
- Cause of late association and of the t=1.144 s / t=3.432 s deassociation bursts (unproven; BEB also affected).
- Why independent is below BEB at 10 APs (and bimodal at 6/8 APs).
- End-of-run association state for the long runs is not recorded.
Next: v1.6.0 scaling analysis across 2 -> 10 APs.
