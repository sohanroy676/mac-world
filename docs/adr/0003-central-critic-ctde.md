# ADR-0003: Optional central critic (CTDE, shared global-reward critic)

## Status
Proposed

## Date
2026-10-16

## Context
v1.6.0 showed independent per-AP DDPG agents degrade relative to BEB as the AP count grows, while global-CW stays above BEB. ADR-0002 deferred the central critic to an optional later phase that must never block core completion. v1.7.0 requires the design to be fixed before coding.

## Decision
Add an optional `--mode central`: N local actors (execution sees only the AP's own loss scalar) and ONE shared central critic Q(s_joint, a_joint) trained on the global goodput reward, MADDPG-style actor updates, joint replay, target networks, tau 1e-3, gamma 0.7. Full spec: `docs/central-critic-v1.7.0.md`. Timeboxed: v1.8 prototype <= 1 session, v1.9 small evaluation; if no benefit or out of time, document as optional/negative and move on.

## Alternatives considered
- N central critics, each on its local reward: keeps per-AP rewards but costs N critics and agents may still compete.
- Mixed local/global reward: adds a lambda hyperparameter.
- Do not implement, document only: lowest cost, but leaves the independent deficit unexplained.

## Consequences
- The ADR-0002 isolation invariant is relaxed for the critic during training in this mode only; execution stays local.
- Adds a joint replay buffer and a new trainer mode; existing modes unchanged.
- The result may be negative; that outcome is acceptable and documented.
