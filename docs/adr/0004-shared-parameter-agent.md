# ADR-0004: Optional shared-parameter agent (`--mode shared`)

## Status
Accepted as an optional experiment with a negative evaluation result (user-approved 2026-10-25). Confirmation on fresh seeds 10-14 (15,15,15,15): shared 27.76 ± 19.04 Mbps vs global 32.94 ± 11.01, paired -5.18 ± 25.04, above global in 1 of 5 seeds; the decision rule was not met (`docs/coop-v2.8.0.md`). Not part of the core.

## Date
2026-10-25

## Context
Independent per-AP DDPG agents lose to the centralized single-agent baseline `global` (one agent, one CW for all APs; not original OSCAR, whose per-AP generalization is `independent`) (`docs/final-results-v2.2.0.md`). Dev runs at 15,15,15,15 (seeds 0-2) showed that a team reward (`--mode coop`, lambda 1 or 0.5) and decaying exploration noise do not fix it: coop 27.9 ± 18.9 and 26.5 ± 22.1 Mbps against global 35.6 ± 6.8, below global in 2 of 3 seeds. The CW traces show each agent settling on its own near-constant CW (e.g. [951, 209, 39, 206]), while global puts every AP on one CW. Cause: untested inference, the agents have no way to agree.

## Decision
Add an optional `--mode shared`: ONE actor and ONE critic (plus targets, ONE replay buffer) used by every AP. The input is the AP's own loss scalar and its AP id (`i/(N-1)`, `--sharedApId 0` drops it); no other AP's observation is ever an input. All N transitions per step go into the buffer; the stored reward is the coop mix `(1-L)*r_i + L*r_global` (`--rewardMix`, default 1); one update per env step. Execution stays local (the actor sees only that AP's row; checked every step with a forward hook in `--check`).

## Alternatives considered
- Own-CW in the observation: still N separate policies, no agreement mechanism; out of v1 scope per CLAUDE.md.
- Stop and report negative: the fallback if shared does not beat global.

## Consequences
- ADR-0002's "one DDPG agent per AP" is relaxed in this mode only: parameters, replay and updates are shared. Default modes are unchanged (traces byte-identical).
- Training sees N-fold more samples per update than independent agents, which is part of any gain and is reported as such.
- The AP id lets the shared policy specialise per AP; `--sharedApId 0` tests whether the id matters.
- The result may be negative; that is documented either way.
