# CN Major Project — Implementation Roadmap

**Roadmap version: v1.0.0**

## Objective

Complete the multi-AP OSCAR major project **as quickly as possible without skipping essential correctness, baseline, evaluation, or documentation work**.

The implementation strategy is deliberately staged:

```text
Baseline
   ↓
2-AP shared ns-3 simulation
   ↓
Per-AP statistics
   ↓
Per-AP CW control
   ↓
2 independent AP-level DDPG agents
   ↓
Validation
   ↓
W&B + baselines
   ↓
Scale to 10 APs
   ↓
Optional central critic
   ↓
Final experiments
   ↓
Report + presentation
```

The project should prefer **minimum viable scientific completeness** over unnecessary features.

---

# 0. Rules for the entire roadmap

- Preserve the working baseline before major changes.
- Use the actual code as authoritative for implementation behavior.
- Do not silently change unrelated components.
- Do not introduce per-station Actors unless explicitly required.
- Do not start with 10 APs.
- Do not add a central critic before the independent AP-level version works.
- Keep the initial PHY/MAC configuration close to the existing OSCAR baseline.
- Validate every major C++ change with a short simulation before training.
- Keep W&B experiment names/configurations reproducible.
- Prefer one shared ns-3 simulation.
- Use Cline **Plan mode** for investigation/design and **Act mode** for approved implementation.
- Each version below should have a clear completion criterion.

---

# v0.1.0 — Baseline Freeze & Reproducibility

## Goal

Create a known reference point before modifying the project.

## Implement / complete

- Record current working commit and environment.
- Record ns-3/ns3-gym/Python/PyTorch versions.
- Record current single-AP topology.
- Record current RL configuration.
- Preserve a reproducible single-AP OSCAR baseline.
- Export/record relevant W&B baseline data.
- Record throughput, reward, loss/collision rate, fairness and CW behavior.
- Document the baseline configuration.

## Do NOT

- change the RL algorithm,
- redesign the observation,
- modify the topology,
- add multi-agent functionality.

## Completion criteria

We can reproduce a short baseline run and have enough data to compare later multi-AP results.

---

# v0.2.0 — Multi-AP Design Specification

## Goal

Convert the project concept into an implementation contract.

## Define

- number of APs for initial test = 2;
- station allocation per AP;
- AP/BSS association;
- AP positions;
- station positions;
- channel/frequency;
- whether APs share the same channel;
- propagation assumptions;
- traffic model;
- AP-local observation;
- AP-local reward;
- action/CW mapping;
- joint action format;
- joint observation format;
- synchronization;
- per-AP statistics;
- global statistics;
- W&B naming;
- baseline comparison methodology.

## Architecture

Initial target:

```text
AP1 → Actor1/Critic1 → CW1
AP2 → Actor2/Critic2 → CW2
```

inside one ns-3 simulation.

## Completion criteria

There is a written specification detailed enough that Cline can implement it without inventing architecture.

---

# v0.3.0 — Two-AP ns-3 Topology

## Goal

Create the physical/logical multi-AP environment before adding RL.

## Implement

Modify the ns-3 scenario so that one simulation contains:

```text
AP1 + its STAs
AP2 + its STAs
```

with unequal station counts.

Ensure:

- APs have unique IDs;
- stations have unique IDs;
- every station is associated with exactly one AP;
- traffic flows are associated with the correct AP;
- simulation starts/stops correctly;
- no RL dependency is required to test the topology.

## Validation

Run a short non-training simulation.

Check:

- all nodes created;
- all applications installed;
- packets flow;
- AP sinks receive expected traffic;
- no segmentation faults;
- no ZMQ/RL deadlock.

## Completion criteria

A clean 2-AP ns-3 simulation runs successfully.

---

# v0.4.0 — Per-AP Statistics

## Goal

Make the simulation produce correct AP-local metrics.

## Implement

Replace the single global accounting logic where necessary with AP-aware accounting.

For each AP calculate:

```text
sent_i
received_i
loss_i
throughput_i
```

Also calculate network totals:

```text
total_sent
total_received
aggregate_throughput
```

and fairness as appropriate.

## Validation

Run the same traffic scenario and verify:

```text
aggregate throughput ≈ sum of AP throughputs
```

and:

```text
AP1 metrics do not contain AP2's traffic
AP2 metrics do not contain AP1's traffic
```

## Completion criteria

Per-AP metrics are demonstrably correct before any RL training.

---

# v0.5.0 — AP-Specific Contention Windows

## Goal

Allow every AP to have its own CW.

## Implement

Replace the current global/wildcard CW configuration with AP-specific configuration.

Conceptually:

```text
CW1 → AP1-associated stations
CW2 → AP2-associated stations
```

Preserve the OSCAR power-of-two CW mapping unless there is a justified reason to change it.

## Validation

Before RL, manually provide different CW values:

```text
AP1 = CW_A
AP2 = CW_B
```

and verify through logs/traces that:

- AP1 stations receive CW_A;
- AP2 stations receive CW_B;
- changing AP1 does not change AP2;
- CW remains stable until another action is applied.

## Completion criteria

AP-specific CW control is proven independently of RL.

---

# v0.6.0 — Multi-AP ns3-gym Interface

## Goal

Transfer multiple observations/actions/rewards between ns-3 and Python.

## Implement

Design the interface as a joint simulation step.

At each decision:

```text
ns-3 → [obs1, obs2, ..., obsN]
Python → [action1, action2, ..., actionN]
ns-3 → [reward1, reward2, ..., rewardN]
```

Keep the simulation step synchronized.

## Validate

Use deterministic/test actions rather than trained policies.

Example:

```text
AP1 action → CW 64
AP2 action → CW 512
```

Verify the correct CWs are applied.

## Completion criteria

A Python test can perform repeated joint actions on a 2-AP simulation without deadlocks or incorrect AP mapping.

---

# v0.7.0 — Two Independent AP-Level DDPG Agents

## Goal

Introduce the actual multi-agent RL system.

## Architecture

```text
Agent1:
Actor1
Critic1
Target Actor1
Target Critic1
Replay1

Agent2:
Actor2
Critic2
Target Actor2
Target Critic2
Replay2
```

Each Actor receives only its own observation.

Each agent produces only its own CW action.

## Training loop

At every simulation step:

```text
obs1, obs2
   ↓
Actor1(obs1) → action1
Actor2(obs2) → action2
   ↓
joint action
   ↓
ns-3
   ↓
reward1, reward2
   ↓
replay buffers
   ↓
local DDPG updates
```

## Completion criteria

Two independent AP agents can train in the same simulation for a short run without errors.

---

# v0.8.0 — Multi-Agent W&B Logging

## Goal

Make experiments measurable and debuggable.

## Log

For each AP:

```text
AP_i/Observation
AP_i/Reward
AP_i/CW
AP_i/Throughput
AP_i/LossRate
AP_i/ActorLoss
AP_i/CriticLoss
```

Global:

```text
Global/AggregateThroughput
Global/Fairness
Global/LossRate
Global/CumulativeReward
```

Also log:

```text
AP_Count
Stations_Per_AP
Episode
Step
```

## Important

Do not average AP metrics into one scalar when the AP-specific values matter.

## Completion criteria

A W&B run clearly shows each AP's learning behavior and the overall network behavior.

---

# v0.9.0 — Two-AP Validation & Debugging

## Goal

Prove that the implementation actually behaves as intended.

## Tests

### Test A — Independent observations

Change AP1 conditions and verify AP2's observation is not directly altered by information leakage.

### Test B — Independent CW

Force:

```text
AP1 = 64
AP2 = 512
```

and verify both remain correctly assigned.

### Test C — Station association

Verify every station is counted only under its AP.

### Test D — Reward

Verify each AP receives its intended local reward.

### Test E — Reset

Run multiple episodes and ensure all AP state/CW/statistics reset correctly.

### Test F — Repeated runs

Run several short seeds/runs to detect instability.

## Completion criteria

The 2-AP system is trusted enough for longer training.

---

# v1.0.0 — Core Project Milestone

## Goal

Have a complete, defensible multi-AP OSCAR implementation.

## Required

- one ns-3 simulation;
- 2 APs;
- unequal station counts;
- one AP-level Actor-Critic per AP;
- AP-local observation;
- AP-local reward;
- AP-specific CW;
- decentralized actors;
- W&B logging;
- reproducible training;
- baseline comparison.

## This is the minimum complete project implementation.

If the project deadline becomes critical, **v1.0.0 is the point at which the core system must already be working**.

Do not delay core completion while implementing advanced features.

---

# v1.1.0 — Baseline Benchmarking

## Goal

Create scientifically meaningful comparisons.

Run:

### Baseline A

Standard IEEE 802.11.

### Baseline B

Single/global-CW OSCAR-style baseline.

### Proposed

Independent multi-AP OSCAR.

Use matched:

- topology;
- station distribution;
- traffic;
- PHY;
- simulation duration;
- seeds.

## Metrics

Primary:

```text
Aggregate throughput
```

Secondary:

```text
Per-AP throughput
Loss/collision rate
Fairness
CW
Reward
Convergence
```

## Completion criteria

We have tables/plots showing whether the proposed system improves or changes performance relative to the baselines.

---

# v1.2.0 — Scaling to 4 APs

## Goal

Prove the architecture is not hard-coded for two APs.

## Implement/test

```text
4 APs
```

with unequal station distributions.

## Validate

- correct AP indexing;
- correct per-AP observations;
- correct per-AP actions;
- correct per-AP rewards;
- correct CW assignment;
- W&B logging;
- stable training.

## Completion criteria

The same code handles 4 APs through configuration rather than duplicated logic.

---

# v1.3.0 — Scaling to 6 APs

Repeat the same validation at:

```text
6 APs
```

Focus on:

- runtime;
- memory;
- ZMQ reliability;
- training stability;
- metric correctness.

---

# v1.4.0 — Scaling to 8 APs

Run the same framework for:

```text
8 APs
```

Record:

- aggregate throughput;
- throughput/AP;
- loss;
- fairness;
- convergence;
- training time.

---

# v1.5.0 — Scaling to 10 APs

## Goal

Meet the project's scalability target.

Run:

```text
10 APs
```

with unequal station counts.

## Completion criteria

The system can complete at least a meaningful evaluation run without architecture-specific manual changes.

This should be treated as a major milestone.

---

# v1.6.0 — Scaling Analysis

## Goal

Turn scaling runs into a research result.

Compare:

```text
AP count: 2, 4, 6, 8, 10
```

Plot:

- aggregate throughput vs AP count;
- throughput per AP vs AP count;
- loss/collision vs AP count;
- fairness vs AP count;
- convergence vs AP count;
- training time vs AP count.

## Completion criteria

There is a clear explanation of how performance and computational cost scale with the number of APs.

---

# v1.7.0 — Central Critic Design

## Goal

Only now decide whether the central critic is worth implementing.

## Before coding

Specify:

- central state;
- joint action;
- global reward;
- local reward;
- central critic input;
- critic architecture;
- actor update;
- replay format;
- target networks;
- training frequency.

Do not let the implementation invent these details.

---

# v1.8.0 — Central Critic Prototype

## Goal

Implement the smallest working centralized critic.

Conceptually:

```text
Actor1(s1) ─┐
Actor2(s2) ─┼──> joint information → Central Critic
...         │
ActorN(sN) ─┘
```

Actors continue using local states.

The central critic can use joint/global information during training.

## Completion criteria

A short training run works and the central critic produces valid losses/Q estimates.

---

# v1.9.0 — Central Critic Evaluation

## Compare

```text
Independent local critics
vs
Local actors + central critic
```

using identical conditions.

Measure:

- aggregate throughput;
- per-AP throughput;
- fairness;
- loss;
- convergence;
- training time;
- stability.

## Decision

If the central critic does not provide a meaningful benefit and threatens the deadline, document it as an optional/negative-result experiment rather than allowing it to delay project completion.

---

# v2.0.0 — Robustness Experiments

Only after the core project is complete.

## Experiments

### Station-density variation

Different station counts per AP.

### Traffic-load variation

Different offered loads.

### AP imbalance

One AP heavily loaded, another lightly loaded.

### Optional channel/interference variations

Only if consistent with the project's defined scope.

## Completion criteria

We understand whether the method works only for one carefully selected topology or generalizes to different conditions.

---

# v2.1.0 — Reproducibility & Cleanup

## Tasks

- remove accidental debug output;
- clean configuration handling;
- make experiment parameters configurable;
- remove hard-coded AP/station assumptions;
- verify reset behavior;
- verify seeds;
- document dependencies;
- ensure no accidental machine-specific paths;
- ensure W&B experiment names are meaningful.

Do not upgrade dependencies unless necessary.

---

# v2.2.0 — Final Results

## Generate

For the final selected experiments:

- raw metric data;
- W&B runs;
- CSV exports where useful;
- throughput plots;
- reward plots;
- CW plots;
- fairness plots;
- scaling plots;
- convergence plots.

Run multiple seeds where computationally feasible.

If compute is limited, prioritize:

1. reproducible main comparison;
2. 2-AP vs baseline;
3. 10-AP scaling;
4. one or two additional robustness experiments.

Do not waste time running dozens of nearly identical experiments.

---

# v2.3.0 — Final Technical Report

## Report structure

1. Abstract
2. Introduction
3. Problem Statement
4. Objectives
5. Background
6. IEEE 802.11 Contention Window
7. Original OSCAR
8. Related Work
9. Proposed Multi-AP Architecture
10. System Design
11. RL Formulation
12. Observation
13. Action/CW Mapping
14. Reward
15. ns-3 Implementation
16. Multi-Agent Architecture
17. W&B Experiment Tracking
18. Experimental Setup
19. Baselines
20. Results
21. Scaling Analysis
22. Discussion
23. Limitations
24. Future Work
25. Conclusion
26. References

Be explicit about what is inherited from OSCAR and what is newly proposed.

---

# v2.4.0 — Final Presentation & Demo

## Prepare

### Architecture slide

```text
Multiple APs
    ↓
Local Actors/Critics
    ↓
AP-specific CW
    ↓
Shared ns-3 environment
```

### Comparison slide

Original OSCAR vs proposed system.

### Results slide

Throughput improvement and scaling.

### Demo

If practical:

```text
2 AP simulation
→ agents choose different CWs
→ throughput changes
→ W&B records metrics
```

Keep the demo short and reliable.

---

# v2.5.0 — Final Audit

Before submission, verify:

## Implementation

- [ ] 2 AP works.
- [ ] 10 AP works.
- [ ] AP-specific CW works.
- [ ] Per-AP observations work.
- [ ] Per-AP rewards work.
- [ ] Agents are decentralized.
- [ ] No accidental cross-AP state leakage.
- [ ] Reset works.
- [ ] Seeds/configuration are documented.
- [ ] W&B works.

## Evaluation

- [ ] Standard baseline.
- [ ] OSCAR/global-CW baseline.
- [ ] Proposed method.
- [ ] 2 AP evaluation.
- [ ] 10 AP evaluation.
- [ ] Scaling analysis.
- [ ] Important metrics recorded.
- [ ] Results reproducible.

## Documentation

- [ ] README.
- [ ] Setup instructions.
- [ ] Architecture documentation.
- [ ] Experiment configuration.
- [ ] Final report.
- [ ] References.
- [ ] Presentation.
- [ ] Demo instructions.

---

# Fast-Track Execution Strategy

If time is very limited, follow this priority order.

## Tier 1 — Absolutely required

```text
v0.1 → v0.2 → v0.3 → v0.4 → v0.5 → v0.6 → v0.7 → v0.8 → v0.9 → v1.0
```

This gives the complete 2-AP project.

## Tier 2 — Required for strong project evaluation

```text
v1.1 → v1.2 → v1.3 → v1.4 → v1.5 → v1.6
```

This gives baseline comparison and 2→10 AP scaling.

## Tier 3 — Advanced contribution

```text
v1.7 → v1.8 → v1.9
```

Central critic.

## Tier 4 — Extra robustness

```text
v2.0
```

Additional traffic/station/interference experiments.

## Tier 5 — Finalization

```text
v2.1 → v2.2 → v2.3 → v2.4 → v2.5
```

Cleanup, results, report, presentation, final audit.

---

# Critical Time-Management Rule

Do **not** wait for every advanced feature before preparing results.

As soon as v1.0.0 works:

1. freeze a working tag/commit;
2. run baseline experiments;
3. collect 2-AP results;
4. start scaling;
5. only then experiment with the central critic.

This ensures that an unfinished central-critic experiment cannot make the entire project incomplete.

---

# Recommended Cline Workflow

For every major version:

### Step 1 — Plan mode

Ask Cline to inspect the relevant existing code and produce an implementation plan.

### Step 2 — Review the plan

Check:
- files to change;
- assumptions;
- API usage;
- topology;
- data flow;
- test strategy.

### Step 3 — Act mode

Only after the plan is accepted.

### Step 4 — Test

Run the smallest possible validation.

### Step 5 — Inspect

Check logs, metrics, and generated behavior.

### Step 6 — Commit

Create a meaningful Git commit after the milestone is verified.

Never ask Cline to simultaneously redesign, implement, debug, and optimize the entire project.

---

# Definition of Done

The project is considered complete when:

```text
ONE SHARED NS-3 SIMULATION
          |
     2–10 APs
          |
   unequal STAs/AP
          |
 LOCAL AP-LEVEL DDPG AGENTS
          |
    AP-SPECIFIC CWs
          |
   CORRECT LOCAL STATS
          |
       W&B
          |
 BASELINE COMPARISON
          |
  SCALING EVALUATION
          |
 FINAL REPORT + DEMO
```

The central critic is an optional advanced milestone and must never be allowed to block completion of the core multi-AP OSCAR system.
