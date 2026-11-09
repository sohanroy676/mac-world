# ADR-0007: Shared actor with a team reward as the main method (RAFA)

## Status
Proposed with the v4 plan. Takes effect when M3 (v4.0.0) implements RAFA. The default trainer is unchanged.

## Date
2026-11-01

## Context
ADR-0002 fixed one agent, one buffer and one reward per AP. ADR-0004 already relaxed it as an optional variant (`--mode shared`, `--alpha`). v3.3 and v3.4 results (`docs/results/sensing-heuristics-v3.3.0.md`, `per-ap-scenario-v3.4.0.md`) show that independent learners with a team PF reward reach the static oracle only for some training seeds, and that the loss scalar alone gives a shared agent no way to tell APs apart. The v4 plan's claim needs one controller that is trained across many scenarios, so it must generalise over AP count and station count.

## Decision
The v4 main method (RAFA) uses one shared DDPG actor, applied by each AP to its own local inputs (idle-slot mean, Retry-bit rate, loss, load, active-station count), trained on a team reward: a station-weighted alpha-fair utility with alpha as an input, plus a training-only fair-floor penalty. Execution stays local: no AP reads another AP's observation. Neighbour summaries only appear in a separate variant (RAFA-N). Independent per-AP agents stay as baselines. Scenarios are drawn per episode from a fixed pool (`--scenarioPool`).

## Input and reward scales (added with M3 step 0, 2026-11-09)
Inputs per AP, all from its own record, each in [0, 1]: mean idle slots / 20 (clipped), Retry-bit rate, goodput per active station / offered per-station load (clipped), active stations / 50 (clipped), own CW exponent (previous action + 1) / 2. The loss scalar is not an input (`--obs rafa`). The reward is the station-weighted PF utility, the mean over all stations of ln(max(0.01 Mbps, per-station Mbps)), mapped affinely so 0.01 Mbps gives 0 and 10 Mbps gives 1 (`--reward spf`); alpha and the fair-floor penalty come in step 2. Exploration noise is Gaussian by default; `--noiseDist gumbel|gumbel-raw` is the step 1 test. Evidence for the Retry/idle choice: M1 gate G0b. Platform note: learners are trained on CPU on GitHub Actions; same-seed reruns are identical only within a CPU vendor (`docs/results/m3-step0-checks-v4.0.0.md`).

## Alternatives considered
- Keep independent actors per AP: not stable across training seeds (v3.4.0 section 4c to 4i), and cannot be trained on varying AP counts.
- Central critic or MAPPO: collapsed at N=10 (v1.9.0) and needs more episodes than 10-minute ns-3 jobs allow.
- Residual on IdleSense, TD3, backoff-mode action: dropped on v3.3 and v3.4 evidence.

## Consequences
- Isolation checks (ADR-0002 `--check`) do not apply to the shared actor; `--scenarioPool` is allowed for `--mode shared` without `--check` only.
- Results must be labelled as relaxed isolation, as in ADR-0004.
- The kill rule in the plan applies: if step 1 cannot separate CWs across AP roles, fall back to independent actors for fixed topologies.
