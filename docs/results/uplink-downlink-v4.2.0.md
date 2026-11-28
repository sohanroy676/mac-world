# Uplink / downlink traffic (`--apDir`), validation v4.2.0

Labels: **fact** = read or measured here. Build: debug profile, GCC 13, `--disable-werror` (local sandbox only; the pinned stack is GCC 11.4, so the Actions image build is the authoritative build).

## Regression (fact)
Binary built from `feature/v4` (before the change) vs the new binary, `--dryRun=true --disableGym=true --apStaCounts=4,4 --simTime=2 --offeredLoad=10 --extraTraces=true`, all output lines except time stamps compared: **identical** apart from the one new log line `--apDir: (none, every AP uplink)`.

## Direction runs (fact, 4+4 STAs, 10 Mbps per STA, 2 s sim, dry run = BEB, seed default, n=1, not a result)
| `--apDir` | AP1 received pkts | AP2 received pkts | checks |
|---|---|---|---|
| (default) | 5034 | 5224 | PASS |
| d,d | 5373 | 5450 | PASS |
| u,d | 8717 | 1931 | PASS |
| b,b | 4318 | 5648 | PASS |
All of: association PASS, per-AP statistics (sinks match counters) PASS, per-AP CW PASS, no flow outside its own BSS. u,d shows the expected effect: the downlink AP is one contender against four uplink STAs and gets a far smaller share (1931 vs 8717), so direction mixing is a real fairness stress.

## Actions pilot (fact, run 45819182285, commit 477a6df, 16/16 jobs `--check PASS`)
S4 chain (10,10,10 hidden 1-3, 10 Mbps per STA, seed 100, 10 s BEB/static/IdleSense, 3 s shared-RAFA gym smoke) x directions uuu, ddd, bbb, u,d,b. The gym-stepped RAFA runs and the trainer's reward mirror (`--check`, including the doubled divisor for `b`) pass in all four. Mean throughput per AP over the second half (Mbps, n=1):
| dir | BEB | static 128,64,128 | IdleSense |
|---|---|---|---|
| uuu | 35.5 / 1.5 / 35.6 | 30.1 / 8.1 / 30.0 | 35.7 / 1.3 / 35.8 |
| ddd | 34.0 / 5.3 / 33.9 | 10.3 / 14.5 / 10.3 | 36.3 / 0.2 / 36.4 |
| bbb | 36.7 / 0.8 / 37.7 | 29.1 / 9.1 / 28.5 | 36.9 / 0.3 / 36.5 |
| u,d,b | 37.1 / 0.3 / 37.2 | 37.7 / 1.2 / 37.7 (job udb-static) | 37.0 / 0.1 / 36.6 |
The same static point is far from right for downlink (edge APs 10 vs 30 Mbps), so oracle grids are needed per direction cell. The middle AP starves under BEB in every direction.

## Not validated
- Gym-stepped runs with learners longer than 3 s; `kwdirect` and fair floors in the new cells.
- `--extraTraces` retry and active-STA fields in `d`/`b` (uplink only by construction).
- Any multi-seed result: none yet. Oracle grids and baselines for the new cells need a run wave.
