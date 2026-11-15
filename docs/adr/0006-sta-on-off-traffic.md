# ADR-0006: Per-STA on/off traffic windows

## Status
Accepted as an opt-in simulator flag (`--staSchedule`). Default flags reproduce all earlier runs byte-for-byte.

## Date
2026-11-01

## Context
CLAUDE.md lists "dynamic STAs" as out of scope for v1. The v4 plan (`docs/planning/mac-world-v4-plan.html`, scenario S8) needs a controller to be tested when the load changes during one run (for example half of the edge stations stop). Traffic in `scenario.h` is a constant-rate UDP `OnOffHelper` per STA, started at `--trafficStart` and stopped at the end of the run, so the only change needed is per-STA start and stop times.

## Decision
`cw.cc --staSchedule=ap:first-last:start:stop[/...]` (0-based AP index, inclusive STA range inside that AP, simulated seconds). Matching STAs get their source and sink start at `start` and stop at `stop`. All other STAs are unchanged. STAs stay associated; only their traffic changes. No mobility, no association or de-association, no PHY or MAC change. The trainer passes the flag through (`--staSchedule`) and can also set it per scenario in a `--scenarioPool` JSON.

## Alternatives considered
- Vary the offered load over time with a rate schedule: needs a new application class.
- Re-launch the simulation between phases: loses queue and CW state, and breaks the gym step loop.
- Keep dynamic STAs out of scope: S8 (adaptation) could not be measured.

## Consequences
- Times are absolute simulated seconds (they include the warm-up); scenario files must account for it.
- Scope change recorded: "dynamic STAs" is now limited to traffic on/off windows, nothing else.
- Checked: `--staSchedule=0:0-0:1:3` on `2,3` lowers the received packet count (17614 to 16556, 4 s run), and regressions (dry 10533, 9000, smoke 10.59458) are unchanged.
