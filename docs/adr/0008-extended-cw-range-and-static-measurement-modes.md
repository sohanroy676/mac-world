# ADR-0008: Extended CW range and static measurement modes

## Status
Accepted

## Date
2026-11-14

## Context
The finalized max-CW plan (`docs/planning/max-cw-optimization-plan-2026-11-14.md`) defines the ceiling of each cell as the
best validated of three static families: F1 exact static CW per AP, F2 static CWmin with BEB doubling, F3 a two-phase
periodic schedule. Before this ADR `cw.cc` could not measure any of them fully:

- `--apCws` and agent actions were clamped to 16..1024.
- A static CW that is not 2^k - 1 was rounded down at every STA by the first beacon (EDCA parameter set carries ECW),
  so statics were octave-only (fact, `docs/results/m3-step0-checks-v4.0.0.md`). Adaptive methods rewrite the CW to
  the whole BSS every 10 ms step and keep the exact value 90-95 % of the time, so they had a mechanism the static
  reference lacked.
- `--cwMinOnly` was accepted only for agent modes.
- There was no time-varying static plan.

## Decision
Add options to `cw.cc` and `OSCAR_multi_ap_train.py`, all off by default, so every earlier run is unchanged:

- `--cwLo`, `--cwHi` (default 16, 1024; limits 1..32767): clamp for `--apCws` and multi-AP actions. 32767 = 2^15 - 1 is
  the largest CW the 4-bit ECW field can carry. The trainer accepts a non-default range in static mode only, until
  the Track B controllers are specified for it.
- `--cwHold`: in a static run, rewrite each AP's CW to its BSS at every env step, the same mechanism the adaptive
  methods use. F1 runs use it.
- `--cwMinOnly` with `--apCws`: MinCw = the given value, MaxCw = max(value, 1023). Values must be 2^k - 1 and at most
  1023, because STAs take CWmin from beacons and `--cwHold` would reset the doubled window every step.
- `--schedA`, `--schedB`, `--schedPeriodSteps`, `--schedASteps`, `--schedMuteCw`: two-phase periodic schedule. Step k
  (0-based) is in phase A when `k mod period < A steps`. An AP in the active group of the phase uses its `--apCws`
  value, every other AP uses the mute CW. The switch is applied at env-step boundaries by the same code path as
  `--cwHold`.

## Alternatives considered
- Change the STA so it ignores the beacon's EDCA parameters: touches upstream ns-3 MAC code, out of scope.
- Redraw pending backoff counters at a phase switch: a MAC change, out of scope. Consequence below.
- Schedule switches as separate ns-3 events at arbitrary times: finer than 10 ms, but the trainer's `--check` could not
  predict the CW per step. Rejected for verifiability.

## Consequences
- F1 is no longer octave-only, and F3 can be measured without new MAC behaviour.
- Fact (`txop.cc`): `SetMinCw`/`SetMaxCw` only reset the CW; a backoff counter already drawn is not redrawn. An AP
  leaving its mute phase can still hold a long counter (up to mute CW x 9 us, 295 ms at 32767), so short periods
  with a large mute CW are sluggish. The schedule search treats period and mute CW as free parameters for this
  reason; the result is a CW-only schedule, not ideal TDMA.
- `--cwHold` and the schedule need Gym stepping (the action handler applies them), so they do not work with
  `--disableGym`.
- Controllers that use CW below 16 or above 1024 need their own specification (Track B).
