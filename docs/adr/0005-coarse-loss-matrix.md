# ADR-0005: Coarse BSS-level loss matrix, per-AP loads and a proportional-fair reward (v3.4.0)

## Status
Accepted as an opt-in scenario and trainer variant. Defaults reproduce the earlier scenario and trainer byte for byte.

## Date
2026-10-28

## Context
`set_phy` in `cw.cc` builds a `MatrixPropagationLossModel` with `SetDefaultLoss(50)` and no `SetLoss` call, so every node hears every other node and the network is one collision domain. v3.1.0 (`docs/results/ceiling-v3.1.0.md`) showed that in this domain the best fixed common CW is at Global-CW level and per-AP CWs give no aggregate headroom. A per-AP method can only show an advantage in a scenario where the best CW differs per AP.

CLAUDE.md lists "detailed interference modelling" as out of scope for v1. This ADR records the user's decision (2026-10-28) to accept one coarse exception.

## Decision
Opt-in flags; nothing is enabled by default.
- `cw.cc --apHidden a-b[,c-d]` (1-based AP pairs) and `--hiddenLoss dB` (default 200): after mobility is installed, every node of BSS a and every node of BSS b get `SetLoss(.., hiddenLoss, symmetric)`. The model is BSS-level only: a pair is either audible (50 dB) or deaf (200 dB, far below the -96 dBm energy-detection threshold). Positions, TX power, PHY and MAC are unchanged. No upstream ns-3 code is touched.
- Diagnostic with `--apHidden`: frames decoded per (receiving BSS, sending BSS) from the MAC header; `Hidden-pair check` is PASS when hidden pairs decode 0 frames and every other pair decodes some.
- `cw.cc --apLoads l1,l2,..`: per-AP per-STA offered load. The per-AP reward normalisation uses it.
- Trainer `--reward pf` (independent/shared): every agent's replay reward is `1 + mean_i log(1e-3 + r_i) / -log(1e-3)`, clamped to [0, 1], with r_i the existing per-AP normalised goodput. This relaxes reward isolation in the same way as `--alpha` (ADR-0004): at execution time every AP still acts on its own local observation. Global keeps OSCAR's reward.

## Alternatives considered
- Geometry-based loss (`LogDistance` plus real positions): closer to a real deployment but needs power and threshold tuning and changes every existing run. Rejected for v3.4.0.
- Per-pair partial attenuation (a few dB, "partial" overlap): not needed to create hidden-node asymmetry and adds a free parameter.
- A different agent algorithm: does not address the ceiling.

## Consequences
- Results in this scenario are only comparable with other runs that use the same flags. Old results are unaffected.
- A hidden pair removes carrier sensing between those BSSs, so frames can collide at the middle BSS without the senders deferring. This is the intended hidden-node effect, not a model of any real building.
- `--reward pf` results are labelled as relaxed (not ADR-0002 isolated).
