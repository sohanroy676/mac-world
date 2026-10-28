# v3.1.0 Ceiling: static CW sweep

Status: experiment report. Branch `feature/v3.1.0-ceiling` (code, merged to `dev` 62d4b80) and `feature/v3.1.0-ceiling-results` (results, tables, this report). Plan: `docs/research-beat-oscar.md` §1, §5 (#1), §6. Tables: `docs/figures/v3.1.0/` (`tables.md`, `summary.csv`). Raw run dirs under `results/ceiling-v3.1.0/` and `results/multi-ap-2026102*` are not committed (see §8).

## 1. Question
Is there throughput headroom above Global-CW OSCAR that a better CW choice could reach? Static CWs (no agent) give the ceiling of what any CW policy can do at this load: if no static setting beats Global by more than the CI width, a learning method has nothing to gain at that topology.

## 2. What was added (fact)
- `cw.cc` `MyExecuteActions`: with `--apCws` set, agent actions no longer overwrite the static CWs. The cw log records the applied CW. Project code, not upstream.
- `OSCAR_multi_ap_train.py --mode static --apCws c1,..,cN`: no agent; same `trace.csv`, reward and policy window as BEB and Global.
- `ceiling_sweep_v3_1_0.py`: `run` (resumable job queue, manifest) and `table` (paired vs BEB and Global).
- Validation (previous session): BEB and Global 2,3 short traces byte-identical to the pre-change binary; static 32,512 held CW 32/512 on all 30 steps; `--check` PASS.
- This session: `linear-mesh` rebuilt (binary mtime 2026-10-27 20:14), static 2,3 short run (`--apCws 32,512 --check`) PASS, then the sweep below. The manifest has 53 rows: 50 PASS (one per job) and 3 FAIL from the earlier parallel-lane attempt (§8).

## 3. Setup (fact)
20,40 (AP1 20 STAs, AP2 40 STAs), simTime 15 s, stepTime 0.01, 150 Mbps per STA offered, policy window steps >= 300. ns-3 seed = python seed + 1. Mbps = aggregate goodput. ± = 95 % CI (Student t). One job at a time, 800-1150 s each on this laptop.

| Block | Jobs | Seeds |
|---|---|---|
| Diagonal CW {32, 64, 128, 256, 384, 512, 768, 1023} at 20,40 | 8 | 0, 1, 2 |
| D1 pair (64,512), (512,64) at 20,40 | 2 | 0, 1, 2 |
| Off-diagonal {32, 128, 512, 1023}^2 minus diagonal at 20,40 | 12 | 0 |
| Diagonal at 6 APs x 10 STAs | 8 | 0 |

References (n=3, seeds 0-2, `results/screen2-{beb,global}`): BEB 27.30 ± 0.63, Global 36.17 ± 6.95.

## 4. Diagonal at 20,40 (n=3)
| CW (both APs) | Aggregate | Per-AP | Jain | phy loss | vs BEB (paired) | vs Global (paired) |
|---|---|---|---|---|---|---|
| 32 | 12.64 ± 0.72 | 4.91 / 7.73 | 0.93 | 0.914 | -14.67 ± 1.34 | -23.54 ± 6.51 |
| 64 | 20.55 ± 2.10 | 7.79 / 12.76 | 0.94 | 0.829 | -6.76 ± 1.81 | -15.63 ± 7.42 |
| 128 | 30.38 ± 0.44 | 10.18 / 20.21 | 0.90 | 0.709 | +3.08 ± 0.34 | -5.79 ± 7.17 |
| 256 | 37.75 ± 0.18 | 12.59 / 25.16 | 0.90 | 0.610 | +10.45 ± 0.81 | +1.57 ± 6.78 |
| 384 | 38.51 ± 0.34 | 14.26 / 24.25 | 0.94 | 0.598 | +11.21 ± 0.54 | +2.34 ± 6.97 |
| **512** | **39.62 ± 0.21** | 13.23 / 26.39 | 0.90 | 0.556 | **+12.32 ± 0.84** | +3.45 ± 6.77 |
| 768 | 39.48 ± 0.14 | 14.86 / 24.62 | 0.94 | 0.549 | +12.18 ± 0.52 | +3.31 ± 7.09 |
| 1023 | 36.50 ± 0.42 | 12.48 / 24.02 | 0.91 | 0.528 | +9.20 ± 0.59 | +0.33 ± 6.92 |

Fact: aggregate rises with CW up to 512, is flat from 512 to 768 (39.62 vs 39.48, CIs overlap) and drops at 1023. Every static common CW >= 256 beats BEB with a CI that excludes 0. The static runs have small CIs (±0.1 to ±0.4); the wide CIs in the Global column come from Global's own seed spread.

## 5. Per-AP CWs at 20,40
### 5.1 D1 pair (n=3)
| AP1 \ AP2 | 64 | 512 |
|---|---|---|
| 64 | 7.79 / 12.76 | 32.51 / 2.52 |
| 512 | 0.58 / 25.09 | 13.23 / 26.39 |

(64,512): aggregate 35.03 ± 0.96, Jain 0.58, paired vs Global -1.15 ± 6.69. (512,64): 25.67 ± 0.59, Jain 0.52, vs Global -10.50 ± 6.37. Fact: each AP gains by lowering its own CW and starves the other (cell shows the low-CW AP taking 32.5 or 25.1 Mbps). Both asymmetric cells are below (512,512) in aggregate and far less fair.

### 5.2 Off-diagonal grid (seed 0 only, n=1, no CI)
Aggregate Mbps; rows = AP1 CW, columns = AP2 CW; diagonal = n=3 mean.

| AP1 \ AP2 | 32 | 128 | 512 | 1023 |
|---|---|---|---|---|
| 32 | 12.64 | 22.77 | 26.19 | 27.31 |
| 128 | 15.98 | 30.38 | 39.19 | 39.52 |
| 512 | 17.13 | 34.65 | 39.62 | 37.85 |
| 1023 | 15.23 | 35.37 | 39.15 | 36.50 |

Fact (n=1): the best asymmetric cell is (128,1023) at 39.52, 0.10 below (512,512). (128,512) 39.19 and (1023,512) 39.15 are within 0.5. These plateau cells are very unequal: (128,1023) gives 37.14 / 2.38 Mbps, (1023,512) 7.81 / 31.34. Any cell with an AP at CW 32 is below 28 Mbps.

## 6. Diagonal at 6x10 (seed 0 only, n=1, paired with BEB and Global at seed 0)
| CW (all 6 APs) | Aggregate | Jain | phy loss |
|---|---|---|---|
| 32 | 14.55 | 0.96 | 0.892 |
| 64 | 21.86 | 0.99 | 0.808 |
| 128 | 32.31 | 0.99 | 0.681 |
| 256 | 38.48 | 1.00 | 0.598 |
| 384 | 38.48 | 1.00 | 0.598 |
| 512 | 39.70 | 1.00 | 0.552 |
| 768 | 39.72 | 1.00 | 0.552 |
| 1023 | 36.62 | 1.00 | 0.528 |

Fact: same shape as 20,40: plateau at 512-768 (about 39.7), drop at 1023. Per-AP throughput is equal (about 6.6 Mbps each at 512, Jain 1.00).
Paired references added 2026-10-28 (same split `10,10,10,10,10,10`, simTime 15, stepTime 0.01, load 150, seed 0, current binary; both `--check` PASS, 836 s / 872 s; run dirs `results/bench-ref-6x10-v3.1.0`, local): BEB 27.78 Mbps, Global 36.11 Mbps (policy window, n=1 each).
Fact (n=1, no CI possible): best static 768 (39.72) is +11.94 vs BEB and +3.61 vs Global; 512 is +11.92 / +3.59. The older 2026-10-17/18 local 6x10 runs were not used: they predate the 2026-10-19 CW-start fix for agent modes.

## 7. Decision
Rule (research plan §6): is the total-throughput headroom of the best static setting over Global larger than the CI width?
- Fact (20,40, n=3): best static CW 512,512 minus Global = +3.45 ± 6.77. The headroom is smaller than the CI half-width. Rule not met: no measurable headroom over Global.
- Fact: no per-AP split beat (512,512) at 20,40 (n=1 grid, best 39.52 vs 39.62; D1 n=3 below it).
- Inference: Global-CW OSCAR is already at the level of the best fixed common CW at this load and topology (36.17 vs 39.62, difference inside Global's seed spread). Static CW 512 is at least as good with much lower variance, so a learning method has little room above Global here and the remaining gain over Global would be seed-variance reduction.
- Inference: at 20,40 the unequal STA split does not create a per-AP-CW advantage in aggregate; per-AP CWs trade fairness for no aggregate gain. v3.4.0 (per-AP scenario) therefore needs a topology where APs differ in more than STA count.
- Fact (6x10, seed 0, n=1): best static minus Global = +3.61 Mbps, same sign and size as at 20,40 (+3.45 ± 6.77). One seed gives no CI, so this does not change the decision; Global's seed spread at 20,40 (±6.95) suggests it would not be distinguishable (inference).
- Unknown: behavior at other loads.

## 8. Limits and bookkeeping
- Off-diagonal grid and 6x10 are n=1 (seed 0). Plateau differences of 0.1-0.5 Mbps there are not distinguishable.
- Pilot parallel lanes (3 lanes) failed in the earlier session, 2 of 3 trainers exited rc 0 after 4 s; cause not investigated (unknown). All runs here used one lane, one job at a time. The manifest keeps those 3 FAIL rows; their jobs were rerun and PASS.
- Committed: manifest, logs of the first 4 pilot runs, tables and summary. New run dirs (`trace.csv`, `config.json`, about 3001 lines each) are NOT committed pending approval; `table` needs them, so tables can only be regenerated on the machine that holds `results/`.
- Machine: 2 cores; jobs took 800-1150 s each (50 jobs).

## 9. Next
Per `docs/research-beat-oscar.md` §6: v3.2.0 fair protocol, v3.3.0 sensing + heuristics, v3.4.0 per-AP scenario (ask the user first), v3.5.0 optional.
