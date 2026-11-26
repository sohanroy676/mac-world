# ADR-0009: Graded and one-way BSS-to-BSS loss (v4.2.0)

## Status
Accepted as an opt-in extension of `--apHidden` (ADR-0005). Defaults and every earlier command line behave byte for byte as before.

## Date
2026-11-26

## Context
ADR-0005 made BSS-to-BSS audibility a yes/no switch: a listed pair gets `--hiddenLoss` (200 dB, far below the -96 dBm energy-detection threshold), every other pair keeps the 50 dB default. The mentor's scenario 2D (graded interference strengths) and the asymmetric part of scenario 7 (A hears B, B does not hear A) cannot be expressed. `docs/planning/post-report-todo.md` item 2 asks for them.

Fact: the loss model is `MatrixPropagationLossModel`; `SetLoss(a, b, dB, symmetric)` already supports a per-pair loss and a one-way entry. Fact: default TX power in this build is 16.02 dBm, so a link at loss L arrives at 16.02 - L dBm; energy detection is -96 dBm (loss 112 dB).

## Decision
Extend the `--apHidden` entry syntax in `cw.cc` (no new flags, no upstream ns-3 change):
- `a-b` : as before, symmetric, loss = `--hiddenLoss`.
- `a-b:dB` : symmetric pair with loss `dB` (0..400). Graded strength.
- `a>b:dB` : one-way. Only transmissions of BSS a received at BSS b see `dB`; b to a keeps 50 dB. This gives "a cannot hear b, b hears a" style asymmetry and hidden-node geometry in one direction.
- The loss is BSS-level (all nodes of a vs all nodes of b), as in ADR-0005. Positions, TX power, PHY and MAC are unchanged. This is a graded model of attenuation, not a geometry or fading model.
- Diagnostic: `Heard:` lines now print the directed loss. `Hidden-pair check` is PASS when every direction with loss above 112 dB decoded 0 frames and every direction with loss at or below 80 dB decoded some. Directions in between are reported only (decoding depends on the MCS, so no verdict).

## Alternatives considered
- Distance-based loss with real positions (`LogDistance`): rejected again (ADR-0005 reasons: retuning, changes every run).
- Separate `--apLoss` flag: same information, one more flag to keep in sync with the trainer and job files. The trainer passes `--apHidden` through `--trainerArgs` unchanged, so no trainer change is needed.

## Consequences
- Old results and job files are unaffected (an entry without `:` or `>` parses as before).
- Graded cells are only comparable with runs using the same entries. Oracle grids and BEB references for any new cell must be regenerated (not done in this ADR).
- Not covered: OBSS-PD or a per-AP CCA threshold (todo item 3, needs its own ADR).
