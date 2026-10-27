# v3.1.0 Ceiling: static CW sweep (PARTIAL, handoff)

Status: **in progress.** Pilot 4 of 10 jobs done (20,40, seed 0, n=1). No CI, no decision yet. Plan: `docs/research-beat-oscar.md` section 1 and 5 (#1).

## What was built (fact)
- `cw.cc` `MyExecuteActions`: with `--apCws` set, agent actions no longer overwrite the static CWs (project code, not upstream). The cw log now records the applied CW.
- `OSCAR_multi_ap_train.py --mode static --apCws c1,c2`: no agent; same `trace.csv`, reward and policy window as BEB/Global.
- `ceiling_sweep_v3_1_0.py`: `run` (job queue, resumable manifest) and `table` (paired vs BEB/Global).
- Validation: rebuilt binary; BEB and Global 2,3 short traces byte-identical to the pre-change binary; static 32,512 held CW 32/512 on all 30 steps, `--check` PASS.

## Pilot results (fact, n=1, seed 0, ns-3 seed 1, aggregate Mbps over steps >= 300)
| CW (both APs) | aggregate | AP1 / AP2 | phy loss |
|---|---|---|---|
| 32 | 12.80 | 3.99 / 8.81 | 0.912 |
| 64 | 19.66 | 7.03 / 12.63 | 0.839 |
| 128 | 30.25 | 10.01 / 20.24 | 0.710 |
| 256 | 37.75 | 12.56 / 25.18 | 0.610 |

References (n=3, same binary family, reproduced from committed run dirs): BEB 27.30 +- 0.63, Global 36.17 +- 6.95.
Seed 0 pairing: 256,256 is +10.50 over BEB and +2.68 over Global.

## Reading (inference, unverified)
Throughput rises with CW up to at least 256, so the best static common CW may be at or above Global's level. Whether per-AP CWs add anything over the best common CW is not tested yet (needs 384..1023 and the off-diagonal/D1 runs).

## Open
CW 384, 512, 768, 1023 and D1 at seed 0; seeds 1-2; off-diagonal grid; 6x10 diagonal; decision. Parallel sweep lanes failed for an uninvestigated reason (unknown); run serially. See `sessionPrompt.md`.
