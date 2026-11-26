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

## Not validated
- Gym-stepped run with an agent (reward under `b`, trainer `--check` mirror): not run locally (no Python 3.7 venv here).
- `--extraTraces` retry and active-STA fields in `d`/`b` (uplink only by construction).
- Any multi-seed result: none yet. Oracle grids and baselines for the new cells need a run wave.
