# CN Major Project — Multi-AP OSCAR

## 1. Project Overview

This project is a college Computer Networks (CN) major project that extends **OSCAR**, a deep-reinforcement-learning approach for contention-window (CW) optimization in IEEE 802.11 WLANs.

The core objective is to move from OSCAR's original **single-AP, single-agent, single-CW** setting to a **multi-AP WLAN in one shared ns-3 simulation**, where each AP has its own local DRL agent and can learn an AP-specific contention window for its associated stations.

The project should preserve the central idea of OSCAR wherever practical, while introducing decentralized multi-AP decision-making and, if time and the finalized project specification justify it, a centralized critic as a later extension.

The implementation is intended for a college major project, so the final outcome must include:
- a working implementation,
- reproducible experiments,
- meaningful comparison with the original OSCAR/baseline,
- W&B tracking,
- scaling experiments up to at least 10 APs,
- analysis of throughput and other relevant networking/RL metrics,
- and complete technical documentation.

**Priority:** finish the project as quickly as possible without skipping work that is necessary for correctness, reproducibility, evaluation, or the final academic deliverables.

---

## 2. Original OSCAR

### 2.1 Problem

In IEEE 802.11 WLANs, stations contend for access to the wireless medium. The contention window affects how stations back off after contention events.

A poorly selected CW can cause:
- excessive collisions when the CW is too small,
- excessive waiting/backoff when the CW is too large,
- and therefore reduced network throughput.

OSCAR formulates CW selection as a reinforcement-learning problem.

### 2.2 Original architecture

The original OSCAR paper uses:

```text
                 ONE AP
                   |
             OSCAR DRL Agent
              Actor + Critic
                   |
                ONE CW
                   |
        +----------+----------+
        |          |          |
       STA        STA        STA
```

There is **one AP-level Actor-Critic/DDPG agent**. The Actor and Critic are components of the same RL agent; they are not two independent agents.

The AP's agent selects a CW that is applied to the stations associated with that AP.

### 2.3 RL algorithm

Original OSCAR uses **Deep Deterministic Policy Gradient (DDPG)**, an Actor-Critic algorithm.

Conceptually:

```text
Observation -> Actor -> CW action
                  |
                  v
               Network
                  |
              Reward
                  |
                  v
                Critic
```

The original paper reports a 10 ms decision epoch and convergence around 300 decision epochs (approximately 3 seconds).

Reported OSCAR DDPG hyperparameters include:

| Parameter | Original OSCAR |
|---|---:|
| Actor hidden layers | 128, 128 |
| Critic hidden layers | 128, 128 |
| Actor learning rate | 3e-4 |
| Critic learning rate | 4e-3 |
| Batch size | 64 |
| Discount factor | 0.9 |
| Replay buffer | 1,000,000 |
| Target-network update factor | 0.1 |
| Decision epoch | 10 ms |

These are paper-level values and must not automatically be assumed to be identical to the current implementation.

### 2.4 Observation

OSCAR is based on frame-loss/collision information and historical observations. The original paper uses statistical information derived from observation windows rather than simply treating the current single scalar as the complete state.

For this project, the **actual existing implementation must be treated as authoritative for its current behavior**. Any change to the observation representation during the extension must be explicitly documented.

### 2.5 Action

The OSCAR action controls the contention window.

The current OSCAR implementation uses a continuous action/exponent representation and converts it into a power-of-two CW in the approximate range:

```text
16, 32, 64, 128, 256, 512, 1024
```

with:

```text
CW = 2^(action + 4)
```

subject to the implementation's scaling/clamping.

The fundamental OSCAR control concept is:

> one learned CW controls the stations associated with the AP.

### 2.6 Reward

OSCAR optimizes throughput/goodput. The reward is based on correctly received data and is normalized/scaled for RL training.

The exact reward formula must be taken from the implementation being used rather than reconstructed from memory.

### 2.7 Performance objective

The primary performance objective is **network throughput**.

Other useful metrics include:
- collision/loss rate,
- fairness,
- CW behavior/stability,
- cumulative reward,
- convergence speed,
- and training overhead.

The original OSCAR paper reports substantial throughput improvement over standard 802.11 under its evaluated scenarios. Exact comparisons for this project must use matched simulation configurations rather than comparing unrelated numbers.

---

## 3. Project Extension

### 3.1 Main goal

Extend OSCAR from:

```text
1 AP
1 Actor-Critic
1 CW
```

to:

```text
N APs
N local AP-level agents
N CW values
```

inside **one shared ns-3 simulation**.

The intended initial architecture is:

```text
                  ONE NS-3 SIMULATION

       AP1              AP2              ... APN
        |                |                 |
 Actor1 + Critic1   Actor2 + Critic2  ActorN + CriticN
        |                |                 |
       CW1              CW2               CWN
        |                |                 |
   AP1's STAs       AP2's STAs         APN's STAs
```

Each AP has its own local agent and its own learned CW.

### 3.2 Why multi-AP?

A single global CW is not necessarily appropriate for a multi-AP WLAN because APs can have different:
- numbers of associated stations,
- local contention levels,
- traffic conditions,
- loss/collision behavior,
- and throughput requirements.

Instead of forcing every AP to use the same CW, each AP should be able to adapt its own CW.

### 3.3 Shared simulation requirement

The chosen architecture is:

> **One ns-3 process containing multiple APs and their associated stations.**

This is important.

Running N independent one-AP ns-3 processes would be easier, but those processes would not naturally represent a shared wireless environment and would not model inter-AP interactions within the same simulation.

The project therefore uses one multi-AP ns-3 simulation.

Initially, AP interference/mobility can remain simplified or ignored according to the project scope. This must be an explicit experimental assumption, not an accidental consequence of implementation.

---

## 4. Agent Granularity

### 4.1 Initial design

The initial design is **one OSCAR-style Actor-Critic agent per AP**:

```text
AP1 -> Actor1/Critic1 -> CW1
AP2 -> Actor2/Critic2 -> CW2
...
APN -> ActorN/CriticN -> CWN
```

The CW selected by AP i is applied to the stations associated with AP i.

### 4.2 Per-station agents are not assumed

Some related papers use one RL agent per transmission station/device. In particular, the supplied SETL-DQN(MA) and Adaptive Throughput Optimization papers use station/node-level distributed agents.

Those papers are relevant literature but **do not establish that this project requires one Actor per station**.

Using one Actor per station would change OSCAR's fundamental control granularity from:

```text
one CW per AP/BSS
```

to:

```text
one CW per station
```

and would substantially increase implementation and experimental complexity.

Therefore, do not implement per-station Actors unless the project specification explicitly requires them later.

---

## 5. Decentralization

Each AP's Actor should use only information available to that AP's local environment.

Conceptually:

```text
Actor1 <- AP1 local observation
Actor2 <- AP2 local observation
Actor3 <- AP3 local observation
...
```

AP1 should not directly receive AP2's local state during decentralized action selection.

This is a core project requirement.

---

## 6. Central Critic — Optional Later Stage

The mentor has described a possible architecture involving:
- multiple AP-level actors,
- local critics,
- and a central critic with access to information from all APs.

However, the exact architecture is not confirmed by the supplied papers.

Therefore the central critic should be treated as a **later project extension**, not a prerequisite for the first working multi-AP implementation.

If implemented, the conceptual structure is:

```text
                    CENTRAL CRITIC
                  /       |       \
                 /        |        \
              AP1        AP2       APN
           Actor/Critic Actor/Critic
```

A centralized critic may receive global state and joint actions during training, while each Actor continues to use only its own local observation.

A possible critic formulation is:

```text
Q(s1, s2, ..., sN, a1, a2, ..., aN)
```

while the actors remain decentralized:

```text
ai = pi(si)
```

This is a CTDE-style design.

The exact central-critic input, loss, reward structure, and update procedure must be specified before implementation.

---

## 7. Reward Design

### Initial recommended design

Use an AP-local reward:

```text
reward_i = normalized throughput/goodput of AP i
```

This allows each local agent to learn from the performance of its own AP.

A later experiment may compare:
- local reward,
- global network reward,
- or a hybrid local/global reward.

For example, a hybrid could conceptually be:

```text
ri = alpha * local_reward_i
     + (1-alpha) * global_reward
```

but this is a later experiment, not an initial requirement.

The exact reward formula must be defined consistently and documented before final experiments.

---

## 8. Observation Design

The current OSCAR implementation transmits a 300-value loss-ratio history from ns-3 but the Python training code uses only the latest value as the actual DDPG state.

For the multi-AP implementation, the initial state should remain simple and AP-local:

```text
observation_i = local AP loss/collision information
```

The exact representation may later be expanded to a window/history if required by experiments or the finalized design.

The project must explicitly distinguish:
- data generated by ns-3,
- data sent through ns3-gym,
- data actually used by the neural network,
- and data used only for logging.

---

## 9. Multi-AP Topology

The implementation should begin with **2 APs**.

Each AP should have a different number of associated stations.

Example only:

```text
AP1 -> 20 STAs
AP2 -> 40 STAs
```

The exact station counts should be selected for a meaningful and computationally manageable experiment.

Then scale to at least:

```text
2 AP
4 AP
6 AP
8 AP
10 AP
```

with unequal station distributions.

The topology should initially use:
- fixed stations,
- no mobility,
- simplified propagation,
- and the same general Wi-Fi configuration as the baseline unless a deliberate experiment changes it.

---

## 10. ns-3 / ns3-gym Architecture

The project uses:

```text
ns-3.29
    |
OpenGym/ns3-gym
    |
ZMQ
    |
Python RL
```

The existing communication is synchronous.

The multi-AP environment should ideally expose a **joint action** for a single simulation decision epoch:

```text
(a1, a2, ..., aN)
```

and return:

```text
(observation1, observation2, ..., observationN)
(reward1, reward2, ..., rewardN)
```

for that same simulation step.

This avoids treating APs in the same physical simulation as completely independent simulations.

The exact OpenGym representation may use vectorized observation/action spaces or another carefully designed interface. This should be decided during implementation planning based on the existing ns3-gym APIs.

---

## 11. CW Control in the Multi-AP System

The current single-AP implementation uses a wildcard ns-3 configuration path that applies one CW to all Wi-Fi devices.

For multi-AP operation, this must become AP-specific.

Conceptually:

```text
CW1 -> stations associated with AP1
CW2 -> stations associated with AP2
...
CWN -> stations associated with APN
```

The implementation must avoid accidentally applying one AP's CW to every AP.

The exact ns-3 device/node paths must be verified before modification.

Whether the AP's own MAC CW is also changed must be explicitly defined and kept consistent with the intended OSCAR semantics.

---

## 12. Per-AP Statistics

The current implementation uses global counters for received/sent packets.

Multi-AP operation requires AP-specific statistics such as:

```text
AP1:
sent1
received1
loss1
throughput1

AP2:
sent2
received2
loss2
throughput2
```

and network-wide aggregates:

```text
total throughput
total loss
overall fairness
```

The project must ensure that:
- packets are attributed to the correct AP/BSS,
- per-AP rewards are correct,
- per-AP observations are correct,
- and aggregate metrics equal the appropriate combination of AP metrics.

Statistics validation must happen before RL training.

---

## 13. Evaluation

### Primary metric

**Aggregate network throughput.**

### Secondary metrics

- per-AP throughput,
- collision/loss rate,
- per-AP loss rate,
- Jain fairness,
- cumulative reward,
- CW values,
- CW stability,
- convergence speed,
- training time,
- scaling behavior.

### Baselines

At minimum compare:

1. Standard IEEE 802.11 behavior.
2. Original/single-global-CW OSCAR-style baseline.
3. Proposed multi-AP OSCAR with independent AP-level agents.

If implemented, additionally compare:

4. Multi-AP OSCAR + central critic.

All important comparisons should use the same topology and simulation parameters wherever scientifically appropriate.

---

## 14. W&B

Weights & Biases is used for experiment tracking.

The project should log at least:

```text
episode
step
AP count
station count per AP
per-AP reward
global reward, if used
per-AP throughput
aggregate throughput
per-AP loss/collision rate
aggregate loss/collision rate
CW per AP
fairness
actor loss
critic loss
```

Use clear names such as:

```text
AP1/CW
AP2/CW
AP1/Throughput
AP2/Throughput
Global/Throughput
AP1/Reward
...
```

rather than averaging AP metrics into one ambiguous scalar.

W&B is the experiment tracking mechanism; it is not itself the scientific objective.

---

## 15. Related Literature — Only Relevant Material

### Original OSCAR

Relevant because it is the project baseline:
- AP-level Actor-Critic/DDPG.
- CW optimization.
- throughput-oriented reward.
- 10-ms decision epochs.
- one learned CW for the AP's stations.

### SETL-DQN(MA)

Relevant only for:
- cooperative multi-agent CW optimization,
- station-level agents,
- local observations,
- common/system throughput reward,
- Dec-POMDP framing.

It should **not** be treated as the project's architecture.

### Adaptive Throughput Optimization

Relevant for:
- distributed CW optimization,
- multiple independent node-level agents,
- local observations,
- network-performance feedback.

Again, it is supporting literature, not the project's exact architecture.

### LILD-DQN

Relevant for:
- collision/loss information as an RL observation,
- throughput-oriented reward,
- DRL-based CW optimization.

### PDCF-DRL

Relevant for:
- AP-level DRL agent,
- CW adjustment,
- collision/history-based observations,
- throughput-oriented reward.

The supplied papers collectively support the feasibility of DRL/MARL-based CW optimization, but none of them proves the exact mentor-described central-critic architecture.

---

## 16. Current Technical Environment

The working environment is known to use approximately:

```text
Ubuntu 22.04 / WSL2
ns-3 3.29
ns3-gym 1.0.0 / Python package 0.1.0
Python 3.7.16
PyTorch 1.13.1 + CUDA 11.7
Gym 0.26.2
NumPy 1.21.6
protobuf 3.20.3 (Python)
pyzmq 26.2.1
W&B 0.18.7
```

GPU training is available on an NVIDIA GTX 1650 Ti 4 GB system.

Do not upgrade/downgrade dependencies casually. The existing environment is working and should be preserved unless a change is explicitly justified.

---

## 17. Important Engineering Principles

1. Preserve a reproducible baseline before major modifications.
2. Do not assume paper behavior equals current code behavior.
3. Do not assume a related paper describes this project's architecture.
4. Clearly label facts, decisions, inferences, and unknowns.
5. Validate ns-3 statistics before training RL.
6. Validate AP-specific CW control before long training.
7. Start with 2 APs.
8. Scale only after the 2-AP version works.
9. Do not implement a central critic before the local multi-AP system works.
10. Do not implement per-station actors unless explicitly required.
11. Avoid unnecessary changes to PHY/MAC parameters.
12. Keep experiments reproducible.
13. Use W&B for systematic experiment tracking.
14. Prefer the smallest implementation that satisfies the project requirements.
15. Optimize for fast completion, but never skip correctness validation or essential baseline/evaluation experiments.

---

## 18. Definition of Success

The project is successful when:

- a single ns-3 simulation contains multiple APs;
- APs have different numbers of associated stations;
- each AP has an independent OSCAR-style RL agent;
- each AP can select its own CW;
- each AP's stations use the correct AP-specific CW;
- AP agents use local information for decentralized decisions;
- per-AP and aggregate metrics are correct;
- the system trains without crashes/deadlocks;
- W&B records reproducible experiments;
- performance is compared against meaningful baselines;
- the system is demonstrated for at least 2 APs and scaled to at least 10 APs;
- the results are analyzed using throughput and supporting metrics;
- and all implementation/design decisions are documented clearly.

A central critic is an advanced extension and should be included if it is required by the final project specification or can be implemented and evaluated without jeopardizing completion of the core system.

---

## 19. Important Terminology

Use these terms consistently:

- **Actor** = policy network that selects the action.
- **Critic** = value/Q network that evaluates actions.
- **Actor-Critic agent** = one RL agent containing Actor and Critic components.
- **AP-level agent** = one agent associated with an AP and controlling that AP's CW.
- **CW** = contention window.
- **DDPG** = Deep Deterministic Policy Gradient.
- **ns-3** = network simulator.
- **ns3-gym/OpenGym** = interface between ns-3 and Python RL.
- **Decentralized actors** = each Actor makes decisions using local information.
- **Centralized critic** = optional critic with access to joint/global information during training.
- **CTDE** = Centralized Training with Decentralized Execution.

Never describe the Actor and Critic as two separate agents.

---

## 20. Development Status Context

The project already has a working single-AP OSCAR environment and successful training runs have been obtained.

The purpose of future work is **not** to recreate the environment from scratch. It is to:
1. preserve the working baseline,
2. extend the ns-3 environment to multiple APs,
3. implement AP-specific control,
4. add multiple local agents,
5. validate and benchmark,
6. scale,
7. optionally add centralized coordination,
8. and complete the academic evaluation/documentation.

The exact current uncommitted working-tree state is intentionally not part of this project description. This document describes the project itself rather than a transient Git state.

