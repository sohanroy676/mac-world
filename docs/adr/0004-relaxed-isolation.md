# ADR-0004: Relaxed per-AP isolation (mixed reward, parameter sharing, richer local obs)

## Status
Accepted as an optional trainer variant (not the default). Default flags reproduce the v2.x trainer.

## Date
2026-10-26

## Context
ADR-0002 fixed strict per-AP isolation: one raw local loss scalar per AP, per-AP normalized goodput reward, one agent and replay buffer per AP. Independent agents fall below BEB as N grows (`docs/results/final-results-v2.2.0.md`), while Global-CW OSCAR stays about +30 % over BEB. The v3.0.0 work (`docs/results/improvement-v3.0.0.md`) asked whether per-AP agents can reach Global-CW performance. Candidate causes (inference, only partly tested): noisy one-sample observation, tiny reward scale, selfish rewards, one transition per step per agent.

## Decision
Add opt-in trainer flags in `OSCAR_multi_ap_train.py`; no `cw.cc` change:
- `--obs hist`: state = [mean, std of the AP's own loss history window, its own previous action]. Still local to the AP.
- `--alpha a`: replay reward = a * local reward + (1 - a) * global reward. This lets the learner see network-wide reward (relaxes reward isolation).
- `--mode shared`: one actor-critic and one replay buffer shared by all APs; each AP still acts on its own local state and applies its own CW (relaxes agent/buffer isolation).
- `--rewardScale`, `--tag` for all modes / run labelling.
Execution-time observations stay local: no AP reads another AP's state when choosing its CW. The relaxation applies to training signals and parameters only.

## Alternatives considered
- Keep strict isolation: already known to degrade with N.
- Central critic (ADR-0003): negative result, needs global state at training.
- Global-CW: already the reference, but a single CW cannot differ per AP.

## Consequences
- Isolation checks in `--check` do not apply to `shared` (parameter distinctness skipped by design); other checks kept.
- Results with these flags are not comparable to ADR-0002 "isolated" claims and must be labelled as relaxed.
- Measured outcome: the best variant (V5) behaves like a Global-level controller with lower seed variance, not a proven throughput gain; its per-AP CWs do not separate.
