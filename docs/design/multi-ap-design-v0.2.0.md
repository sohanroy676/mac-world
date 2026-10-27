# OSCAR v0.2.0 - Multi-AP Design Specification

**Status:** CLOSED 2026-09-16 - design contract accepted.
**Scope:** documentation and architecture only; no simulation or training behavior changes.

This document defines the implementation contract for extending the current single-AP OSCAR codebase into the first two-AP multi-agent system. It is grounded in the current implementation (`cw.cc`, `scenario.h`, `OSCAR_train.py`, `wrappers.py`) and the v0.1.0 baseline freeze.

## 1. Architecture Decision Summary

v0.2.0 accepts the audit's recommended defaults:

| Decision | v0.2.0 choice |
|---|---|
| Process shape | One ns-3 process containing all APs and STAs |
| Agent granularity | One OSCAR-style DDPG Actor-Critic agent per AP |
| Critic design | Local critics only for the v1 core; no central critic yet |
| Reward | AP-local normalized goodput reward |
| Observation | AP-local latest loss ratio scalar initially |
| Stepping | Synchronous sequential joint simulation step |

The target shape is:

```text
One ns-3 simulation
  AP1 -> Actor1/Critic1 -> CW1 -> AP1 STAs
  AP2 -> Actor2/Critic2 -> CW2 -> AP2 STAs
```

The central critic, per-station actors, mobility, dynamic station joins, and detailed interference experiments remain out of scope for the core v1 path.

## 2. Initial Two-AP Topology

The first implementation target is exactly two APs in one shared ns-3 simulation.

| Item | v0.2.0 contract |
|---|---|
| AP count | 2 |
| Station allocation | `AP1=20`, `AP2=40` by default |
| BSS layout | One BSS per AP; every STA associates with exactly one AP |
| Node identity | APs and STAs must have stable AP-local and global node IDs |
| Mobility | Fixed positions only; `ConstantPositionMobilityModel` |
| Channel | Shared 5 GHz channel, preserving baseline 802.11ax settings |
| PHY/MAC defaults | Keep baseline MCS, channel width, guard interval, offered load, RTS setting unless explicitly changed in a later milestone |
| Traffic | UDP uplink STA -> associated AP, same payload and offered load pattern as baseline |

Positioning must make AP/BSS membership explicit. A simple default is APs separated on the x-axis, with each AP's STAs placed near their associated AP. The exact coordinates are an implementation detail for v0.3.0, but the design requires fixed and reproducible positions.

## 3. Per-AP Observation, Reward, and Statistics

Each AP has isolated counters and derived metrics. Global counters may still exist, but they must be aggregates over AP-local values rather than the source of AP-local learning signals.

Per AP, maintain:

- `tx_packets_i`: transmissions attributed to AP i's BSS.
- `rx_packets_i`: packets received by AP i's sink.
- `loss_ratio_i = (tx_delta_i - rx_delta_i) / tx_delta_i`, with a defined zero-sent fallback of `0.0`.
- `throughput_i` or goodput in Mbps.
- `reward_i`.
- `cw_i`.
- active station count for AP i.

Global metrics:

- `total_tx_packets = sum(tx_packets_i)`.
- `total_rx_packets = sum(rx_packets_i)`.
- `aggregate_throughput = sum(throughput_i)`.
- Jain fairness computed from valid per-flow or per-AP throughput values, with initialized accumulators.

Initial DDPG state remains intentionally close to v0.1.0:

```text
state_i = [latest_loss_ratio_i]
```

ns-3 may still keep a history deque per AP for compatibility and logging, but Python training initially consumes only the latest AP-local scalar.

Reward is AP-local normalized goodput:

```text
reward_i = goodput_mbit_i / (offered_load_mbps * active_sta_count_i * env_step_time)
```

The implementation must not carry forward the single-AP hard-coded `5 * 150` normalization. Reward clamping/holding behavior should be documented when implemented; the preferred default is a transparent clamp to `[0, 1]` rather than holding the previous reward.

## 4. Action and CW Contract

Each AP receives one continuous action in the OSCAR exponent domain:

```text
action_i in [0, 6]
cw_i = clamp(2^(action_i + 4), 16, 1024)
```

Python actors continue to emit `[-1, 1]` values and scale them to `[0, 6]`, as in v0.1.0.

CW application must be AP-specific:

```text
CW1 -> AP1-associated stations
CW2 -> AP2-associated stations
```

v0.3.0/v0.5.0 must replace the current wildcard `Config::Set` path with targeted per-node/per-device paths. The implementation must explicitly decide whether the AP device's own MAC uses `cw_i`; the default should preserve OSCAR's current behavior for the controlled BSS unless testing proves the AP should remain at default BEB.

## 5. ns3-gym Interface Contract

The multi-AP interface is a joint environment step, not independent simulations:

```text
ns-3 -> Python:
  observations = [obs_ap1, obs_ap2]
  rewards      = [reward_ap1, reward_ap2]
  done         = false
  info         = structured per-AP and aggregate metrics

Python -> ns-3:
  actions      = [action_ap1, action_ap2]
```

For the first implementation, prefer one OpenGym interface with vectorized spaces:

```text
observation_space shape = [ap_count, state_dim]
action_space shape      = [ap_count]
reward shape            = [ap_count]
```

If ns3-gym constraints make vectorized rewards awkward, keep rewards in `info` while preserving an AP-indexed scalar reward array on the Python side. The mapping between AP index, node ID, BSS, action, observation, reward, and CW must be deterministic and logged.

Sequential stepping means Python computes all AP actions for the current joint observation, sends the joint action once, and receives the next joint state. It does not run N independent ns-3 processes and does not require threaded port orchestration for the v1 core.

## 6. Python Training Contract

The initial multi-agent training loop will instantiate one DDPG object and one replay buffer per AP:

```text
agents = [DDPG_AP1, DDPG_AP2]
replay = [Replay_AP1, Replay_AP2]
```

At each decision epoch:

```text
obs_i -> actor_i -> action_i
joint_action = [action_1, action_2]
env.step(joint_action)
reward_i, next_obs_i -> replay_i
train agent_i from replay_i
```

Actors must only receive their AP-local observation. Local critics train only on local `(state_i, action_i, reward_i, next_state_i)` tuples. No global state or joint-action critic is part of v1 core training.

## 7. Logging and Validation Contract

W&B metrics must use explicit AP names:

```text
AP1/CW
AP2/CW
AP1/Reward
AP2/Reward
AP1/Throughput
AP2/Throughput
AP1/LossRatio
AP2/LossRatio
Global/Throughput
Global/Fairness
```

Validation order for later milestones:

1. v0.3.0: prove two APs and unequal STAs run in one ns-3 simulation without RL dependence.
2. v0.4.0: prove AP-local statistics are correct and aggregate throughput equals the sum of AP throughput.
3. v0.5.0: prove changing `CW1` does not change `CW2`, and vice versa.
4. v0.6.0: prove joint ns3-gym observations/actions/rewards map to the correct APs with deterministic test actions.
5. v0.7.0: train two independent AP-level DDPG agents for a short run.

## 8. Baseline Comparison

Later comparisons must use matched topology and parameters where scientifically appropriate:

- standard IEEE 802.11 BEB behavior;
- single/global-CW OSCAR-style control adapted to the same two-AP topology;
- independent per-AP OSCAR agents.

The v0.1.0 single-AP baseline remains the historical reference, but multi-AP claims should be evaluated against multi-AP baselines.

## 9. Completion Criteria

v0.2.0 is complete when this design and its ADR are committed, and the roadmap/memory bank identify v0.3.0 as the next implementation milestone.
