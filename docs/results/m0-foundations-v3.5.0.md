# M0 foundations (v3.5.0): lanes, new flags, GC tooling, load test

Status: code, load test and pool BEB references DONE (2026-11-01). Plan: `docs/planning/mac-world-v4-plan.html` (rev 5; rev 6 change in section 4). Branch `feature/v4`.

## 1. What was added (fact; each opt-in, defaults byte-identical)
| Item | Where | Check |
|---|---|---|
| Unseeded free port per env, unique run dir when two jobs start in the same second | `wrappers.py`, `OSCAR_multi_ap_train.py` | 2 parallel same-seed `2,3` jobs: `trace.csv` identical to serial |
| `--useRts`, `--rewardNorm Mbps`, `--extraTraces` (Retry rate, active STAs, failed data attempts per AP, per-AP delay mean/p50/p99 at the end of the run) | `cw.cc`, trainer, `multi_ap.py` | `--check` PASS; old trace columns unchanged; Retry rate in [0,1], active STAs <= BSS size; RTS changes rewards (`[18.1, 14.9]` to `[15.1, 8.7]`) |
| `--staSchedule ap:first-last:start:stop[/...]` (ADR-0006) | `cw.cc`, `scenario.h`, trainer | 2,3 dry 4 s: 17614 to 16556 packets with one STA muted |
| `--scenarioPool pool.json` (shared mode, varying AP count, ADR-0007) | trainer | 2 configs (2 and 3 APs) over 3 episodes ran |
| `gc_analysis.py` (station-weighted U_alpha, floor, GC, paired t, Holm, intersection-union) | linear-mesh | reproduces committed S4: BEB 71.63 / 1.44, Global 76.46 / 2.58, IdleSense 78.12 / 0.53, static 59.58 / 13.25 |
| Trainer leftover check per run (gym port), not any `linear-mesh` process | trainer | needed for lanes; first two training jobs failed `--check` on the other lane's process |

Regressions after the last `cw.cc` change: `--nWifi=5` dry seed 1 = 10533, `5,15` = 9000, smoke 10.59458, default `2,3` trace byte-identical. Not done: the delay histogram is per AP at the end of the run only (no per-step series); the v3.4.0 `snifferHeard` matrix has the same 4-byte A-MPDU delimiter offset that `--extraTraces` strips (not touched, inference: it only matters for data frames).

## 2. Load test (equal load, 150 vs 10 Mbps per STA, `--rewardNorm 150` at 10)
BEB, static and Global (1 training episode, `--trainSeed 0`, frozen eval), seeds 100-102 (n=3), 40 jobs, all `--check` PASS, 2 lanes. S2 = `20,40`, static 512,512. S4 = `10,10,10 --apHidden 1-3`, static 256,128,256. GC with 5 % floor slack, alpha 1 (alpha 0 in S2 gives the same picture):
| Cell | Load | BEB agg | Global agg | Static agg | GC Global (95 % CI) | mean eval job |
|---|---|---|---|---|---|---|
| S2 | 150 | 27.97 | 35.50 | 39.66 | 0.678 ± 0.062 | 1091 s |
| S2 | 10 | 27.48 | 34.15 | 39.65 | 0.593 ± 0.113 | 367 s |
| S4 | 150 | 72.19 | 76.38 | 59.65 | 0.534 ± 0.150 | 635 s |
| S4 | 10 | 71.93 | 76.88 | 59.52 | 0.491 ± 0.136 | 256 s |

Inference: at n=3 every pair of GC intervals overlaps, BEB and static aggregates agree within about 0.5 Mbps, so the lower load does not change these cells. Jobs are 2.5 to 3 times faster (two jobs ran at once at both loads).
Decision (plan rule "adopt if within the CI"): use 10 Mbps per STA with `--rewardNorm 150` for equal-load cells. Not tested and therefore not adopted: uneven-load cells (S5a `150,150,1`), where the load is the scenario. The 150-load Global GC is higher by 0.04 to 0.09 in three cells; n=3 and one training seed cannot tell a load effect from training noise.

## 3. Limits (unknown)
Global was trained for 1 episode at one training seed, so the Global numbers are for load comparison only, not a baseline result. The S4 alpha 0 cell is degenerate: the best static in this set (256,128,256, 59.7 Mbps) is below BEB (72.2), so the oracle needs the M1 grid with equal and asymmetric CWs.

## 4. Plan change (revision 6, decided 2026-11-01)
Fair floor with the rev 5 definition marks the S4 static oracle infeasible (edge APs 23.2 vs floor 23.88, 2.9 % short), so no oracle exists. Decision: feasibility is x_i >= 0.95 floor_i for every method (`gc_analysis.py --floorTol 0.05`; `0` restores rev 5). To be written into the plan page.

## 5. Training-pool BEB references
`ns-3.29/scratch/linear-mesh/scenarios/pool_v3_5_0.json` (24 configs, approved). One BEB run per config, python seed 2000+k (ns-3 seed 2001+k), 15 s, load as written in the pool file (150 Mbps; the pool was not rerun at load 10), tag `poolbeb-<name>`, driver manifest in the session scratchpad. All 24 `--check` PASS (jobs 474-1150 s, 2 lanes, about 2.2 h wall-clock). Per-AP BEB throughput and the station-weighted floors are in `docs/results/pool-beb-refs-v3.5.0.csv` (one row per config, includes the local run-dir name). Run dirs (`config.json` + `trace.csv`), manifests, job lists and logs are committed in `docs/figures/v3.5.0-pool/` and `docs/figures/v3.5.0-loadtest/` (run dirs under `ns-3.29/scratch/linear-mesh/results/`, force-added; load-test Global actors in `results/loadtest/actors/`). Sanity (fact): equal-load chains show the starved middle AP (1.0-2.2 Mbps); `150,150,1` AP3 delivers its full 10 or 5 Mbps; the half-edge-off configs lose about 8-13 Mbps of aggregate versus their full versions.
