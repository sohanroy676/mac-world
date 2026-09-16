# ADR-0002: Accept v0.2.0 Multi-AP Defaults

## Status
Accepted

## Date
2026-09-16

## Context
The project is extending OSCAR from one AP, one DDPG agent, and one global CW into a multi-AP system. The forensic audit identified six mentor-level design decisions that block implementation if left open. The user accepted the audit's recommended defaults for v0.2.0 so the project can move from baseline freeze to the first two-AP implementation.

## Decision
Use one shared ns-3 process containing all APs and STAs. Implement one OSCAR-style AP-level DDPG Actor-Critic agent per AP, with local critics only for the core v1 path. Use AP-local normalized goodput rewards, AP-local latest loss-ratio scalar observations, and synchronous sequential joint stepping through ns3-gym.

The accepted D1-D6 choices are:

| Decision | Accepted choice |
|---|---|
| D1. Multi-AP process shape | One ns-3 process, N APs |
| D2. Agent granularity | Per-AP Actor-Critic agent |
| D3. Central critic | Not in core v1; optional later extension |
| D4. Reward | Per-AP goodput reward |
| D5. Observation | One raw local loss scalar per AP initially |
| D6. Stepping semantics | Sequential joint stepping |

## Alternatives considered
- N independent ns-3 processes, one AP each: rejected for the core system because isolated processes cannot model a shared wireless simulation.
- Per-station actors: rejected for v1 because it changes OSCAR's AP-level control granularity and greatly increases the C++ attribution and CW-control surface.
- Central critic in the first implementation: deferred because it requires global-state/joint-action replay, new critic logic, and additional validation after the local multi-AP system works.
- Paper-style windowed mean/std observation immediately: deferred to preserve the known v0.1.0 behavior while AP isolation is introduced.
- Parallel ports/threaded stepping: deferred because sequential joint stepping matches the current synchronous ns3-gym flow with less ZMQ complexity.

## Consequences
The next milestones can be implemented in a narrow order: two-AP topology, per-AP statistics, per-AP CW, joint ns3-gym interface, then independent agents. The design intentionally optimizes for a working and scientifically inspectable v1 before adding central training or richer observations.
