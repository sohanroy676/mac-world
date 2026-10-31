# Multi-AP OSCAR: Contention-Window Optimization with Per-AP DDPG Agents in a Shared ns-3 Simulation

Technical report, v2.3.0, updated 2026-10-27 with the v3.0.0 results (§20.4) and 2026-10-31 with the v3.4.0 results (§20.5). Status: draft for review. Five citations are filled (§26); the remaining placeholders are written `[REF:key]` and wait for the author's reference list.

Labels used throughout: **[Inherited]** = comes from the original OSCAR design or code; **[New]** = added by this project; **[Upstream]** = ns-3 / ns3-gym code used unchanged. Statements are fact unless marked *inference* (reasoned, untested).

---

## 1. Abstract

OSCAR optimizes the IEEE 802.11 contention window (CW) of one access point (AP) with a DDPG actor-critic agent. This project extends it to N APs in one shared ns-3 simulation, each AP with its own independent DDPG agent and its own CW. We compare three controllers against standard 802.11 binary exponential backoff (BEB): independent per-AP agents, one shared "global-CW" agent whose CW is broadcast to every AP, and (as an appendix, negative result) a central-critic variant.

On the final, fixed-binary set (n = 3 seeds, 95 % confidence intervals), the global-CW agent gains +29.5 % to +33.2 % aggregate throughput over BEB in every saturated topology, from 2 to 10 APs at a fixed 60 stations. The independent per-AP agents do not scale: they are on par with BEB at N = 2 (+3.8 ± 27.2 %), then fall below it from N = 4 (−27.0 ± 21.8 %) to N = 10 (−46.2 ± 12.2 %). At a light load of 0.5 Mbps per station the global gain shrinks to +6.3 ± 8.0 %. The central critic did not help and is reported as a negative result. A later attempt (v3.0.0, §20.4) to beat the global-CW agent with per-AP controllers that share weights reached global level (paired intervals span 0) and lowered seed variance in two topologies; it did not prove a gain. In a hidden-chain scenario with a fairness reward (v3.4.0, §20.5) independent per-AP agents beat BEB and the global agent on proportional-fair utility and weakest-AP throughput, at lower aggregate throughput. Results have wide intervals at n = 3, and several effects are explained only by inference.

## 2. Introduction

In 802.11 DCF, stations pick a random backoff in a window [0, CW]. A small CW wastes airtime in collisions when many stations contend; a large CW wastes airtime idling. BEB doubles CW after a loss and resets it after a success, which is not throughput-optimal in dense networks. OSCAR [OSCAR] learns a CW with deep reinforcement learning to raise throughput.

The original design controls one AP's BSS. Real deployments have many neighbouring APs sharing a channel. This project asks whether per-AP learners, each seeing only local information, can coordinate implicitly, and how that behaviour changes as APs are added.

## 3. Problem Statement

Given N APs on one shared channel, each serving its own stations, choose each AP's CW to maximize network throughput, where every AP's learner observes only its own BSS. The difficulty is that each AP's CW changes the environment of the others, so independent learners face a non-stationary problem.

## 4. Objectives

1. Build one ns-3 simulation containing N APs, with per-AP statistics, per-AP CW control and a multi-AP ns3-gym interface. [New]
2. Train one DDPG agent per AP with strict isolation of observations, rewards, actions and statistics. [New]
3. Provide baselines: BEB and a global-CW OSCAR agent. [New]
4. Evaluate from 2 to 10 APs and under load and imbalance changes, with multiple seeds and confidence intervals. [New]
5. Specify, prototype and evaluate an optional central critic without letting it block the core. [New]

Out of scope (design contract, ADR-0002): mobility, dynamic stations, detailed interference modelling, per-station actors, PHY/MAC changes.

## 5. Background

An 802.11ax (HE) network in a single 5 GHz channel is simulated in ns-3.29 [ns-3]. Stations send UDP uplink traffic to their associated AP. A frame lost to collision is retransmitted with a larger CW. The learning loop is a Gym interface to ns-3 (ns3-gym [ns3-gym]): every `stepTime` of simulated time the simulator pauses, sends an observation and reward to Python, and applies the returned action.

## 6. IEEE 802.11 Contention Window

Under BEB the CW starts at 16 (`CWmin`) and doubles per failed attempt up to 1024 (`CWmax`). Every run here uses the range 16..1024 [REF:ieee80211]. In the agent modes the agent sets this value directly (§13), and the same clamp applies. In `beb` mode the ns-3 default DCF is used with no agent (`--dryRun`).

## 7. Original OSCAR [Inherited]

OSCAR is an AP-level DDPG agent that sets one CW for the AP's stations, from a loss-based observation, with a throughput-oriented reward and 10 ms decision epochs [OSCAR]. The v0.1.0 baseline freeze (`docs/results/baseline-v0.1.0.md`) records what the code does, which differs from the paper in places. Differences measured in the code (code is authoritative over the paper):

| Item | This codebase | Note |
|---|---|---|
| Hidden layers (actor, critic) | 128, 128 | matches paper |
| Critic learning rate (Adam) | 4e-3 | matches paper |
| Actor learning rate (Adam) | 4e-4 | paper: 3e-4 |
| Discount / soft-update τ | 0.7 / 1e-3 | |
| State actually used | 1 scalar of the 300-value loss history | largest modelling gap versus the paper |
| Single-AP reward normalization | hard-coded `5 · 150` | not N-generic |
| Known quirks | uninitialized `jain_index()` in `cw.cc`; CW 0/0 until the first action | `docs/results/baseline-v0.1.0.md` §7 |

Both the single-AP path and the original agent classes (`agents/our_ddpg/Our_DDPG.py`) are reused unchanged by the multi-AP trainer. [Inherited]

## 8. Related Work

Supporting literature on DRL/MARL-based CW optimization (not this project's architecture; `docs/planning/project_description.md` §15):

- OSCAR [OSCAR]: the project baseline (AP-level DDPG, loss observation, throughput reward).
- SETL-DQN(MA) [REF:setl]: cooperative multi-agent CW optimization with station-level agents and local observations, common throughput reward, Dec-POMDP framing.
- Adaptive Throughput Optimization [REF:ato]: distributed CW optimization with independent node-level agents.
- LILD-DQN [REF:lild]: collision/loss information as an RL observation.
- PDCF-DRL [REF:pdcf]: AP-level DRL agent adjusting CW from collision history.

These papers show that DRL/MARL CW control is feasible. None of them establishes the architecture used here (per-AP actors in one shared simulation, with a global-CW baseline and an optional shared critic). Station-level agents in some of them are not adopted here.

## 9. Proposed Multi-AP Architecture [New]

One ns-3 process contains N APs and all their stations. A Python trainer owns one DDPG agent per AP (actor and critic together are one agent). Each step the trainer reads N local observations, produces N actions, and ns-3 applies one CW per AP.

```text
 one ns-3 process (shared channel)           Python trainer
 +-----------------------------------+      +-----------------------------+
 | AP1 + STAs1  --loss_1, reward_1-->|----->| agent 1 (actor+critic) -> a1|
 | AP2 + STAs2  --loss_2, reward_2-->|----->| agent 2 (actor+critic) -> a2|
 | ...                               |      | ...                         |
 | APN + STAsN  --loss_N, reward_N-->|----->| agent N (actor+critic) -> aN|
 |        ^                          |      +--------------+--------------+
 |        +---- CW_1 .. CW_N ----------<-------------------+  (ns3-gym, ZMQ)
 +-----------------------------------+
```

Design contract: ADR-0002 and `docs/design/multi-ap-design-v0.2.0.md`. Invariants: per-AP isolation (no agent sees another AP's observation), local critics only in the core, sequential joint stepping, central critic optional and never blocking.

## 10. System Design

| Item | Value |
|---|---|
| Topology | N BSSs, one SSID per AP, fixed positions (`ConstantPositionMobilityModel`), shared channel |
| Traffic | UDP uplink STA → associated AP, constant rate, 1464-byte payload |
| Default stations | 20 + 40 (AP1 + AP2); scaling uses an equal split of 60 |
| Stepping | 1 step = 0.01 s simulated; 1500 steps = 15 s per run |
| Interface | multi-AP ns3-gym: observation Box [N, H], action Box [N] |
| Modes | `beb`, `independent`, `global`, `central` (appendix) |

## 11. RL Formulation

Per AP *i* (mode `independent`): a single-agent MDP with state = AP *i*'s latest loss ratio, action = a scalar in [−1, 1] mapped to AP *i*'s CW, reward = AP *i*'s normalized goodput. The joint problem is a multi-agent game in which each agent treats the others as part of the environment. Algorithm: DDPG [DDPG] with actor/critic of 128-128 hidden units [Inherited]. Hyper-parameters (code defaults of `OSCAR_multi_ap_train.py`): batch 32, discount 0.7, τ = 1e-3, exploration noise σ = 0.1, 300 random-action warm-up steps, actor/critic lr 4e-4 / 4e-3.

## 12. Observation

[New, AP-local; the scalar is Inherited in kind] Each AP's observation is its latest loss ratio

`loss_i = (tx_i − rx_i) / tx_i`

over the last step, from AP *i*'s PHY transmit count and AP *i*'s sink receive count (0 if nothing was sent). The environment delivers a 300-step history per AP, but the agents use only the newest value (`state_dim = 1`), as in the original code. A richer state (windowed mean/std) exists in `preprocessor.py` but is not used here. In `global` mode the single agent sees one network-level loss scalar.

## 13. Action / CW Mapping

The actor outputs `a ∈ [−1, 1]` (Gaussian exploration noise added, then clipped). The trainer maps it to an exponent `e = 6 (a + 1) / 2 ∈ [0, 6]`, and `cw.cc` sets `CW = clamp(2^(4+e), 16, 1024)` per AP. [Inherited mapping, applied per AP by the project.] The first 300 steps use uniform random actions. From the v2.0.0 fix, agent runs start with CW 16/1024 instead of 0/0 until the first action (see §15).

## 14. Reward

[New in this form] Per AP: `reward_i = clamp(goodput_i / (offered_load · stas_i · step), 0, 1)`, i.e. received payload bits of AP *i*'s sink normalized by what its stations offer. In `global` mode the reward is the network goodput normalized by the offered load of all stations. Because the offered load saturates the channel, the policy-phase reward is small (about 0.003–0.004 at 60 STAs); this is a known scale (`docs/results/core-v1.0.0.md` §5), and the effect on learning is *inference* (untested). Reward plots (`reward.png`) are comparable within a figure only.

## 15. ns-3 Implementation

Project code, all under `ns-3.29/scratch/linear-mesh/` ([Upstream] ns-3.29 and `contrib/opengym` are used as-is; `git log` shows `ns-3.29/src` and `contrib/opengym` touched only by one commit, bc6f12c, and by no later commit):

- `scenario.h`, `cw.cc`: N-AP topology, per-AP counters, per-AP CW setting with readback, per-AP reward and loss, the multi-AP gym interface.
- PHY/MAC: 802.11ax 5 GHz, HE MCS 11, 20 MHz channel width, 800 ns guard interval, constant-rate station manager. [Inherited baseline settings, unchanged]
- Seeds: ns-3 seed = Python seed + 1; a bug where `--seed` did not affect ns-3 was fixed in v1.1.0 (commit 0e71414).
- **Bug found and fixed (v2.0.0, commit 1306e37):** agent modes began with CW 0/0, which starved most stations during warm-up. Multi-AP agent runs now begin at 16/1024. All v1.1.0–v1.9.0 agent results were produced before this fix and are treated as pre-fix (appendix only). Only the 81 v2.0.0 `*-cwfix` runs are used for conclusions.
- Association: with traffic starting at t = 0, large-N runs show late association and deassociation bursts; `--trafficStart=2` removed them in a diagnostic run (`docs/results/robustness-v2.0.0.md` §G). The final set keeps the inherited t = 0 start; dry BEB checks of its topologies (20,40, 6 x 10, 5,5,5,45) show every STA associated by 1.12 s, before the policy window (`docs/results/robustness-v2.0.0.md` §G.5).

## 16. Multi-Agent Architecture

| Mode | Agents | Observation | Action | Reward | Status |
|---|---|---|---|---|---|
| `beb` | none | none | standard BEB | none | baseline |
| `global` | 1 (shared) | network loss | one CW broadcast to all APs | network goodput | baseline B [New] |
| `independent` | N (one per AP) | own AP loss | own CW | own AP goodput | core [New] |
| `central` | N actors + 1 shared critic (CTDE) | own AP loss (actors); joint (critic) | own CW | global goodput | optional, appendix A |

`global` mode is the OSCAR-style single controller applied to a multi-AP network; it uses global information and is therefore not an isolated-AP method. It is the reference for how much a shared signal helps.

## 17. W&B Experiment Tracking

Each run logs per-AP and global metrics (names from design §7) to Weights & Biases, offline by default. Since v2.1.0 runs are named `<topology> <mode> s<seed>` with mode and git-revision tags. Fact: the 81 final runs were produced before this naming and are stored as local offline `.wandb` files. Update 2026-10-20: all 81 were synced online to project `contention_window` (private) and renamed `<topology> <mode> s<seed>` with tags `multi-ap`, `final-v2.2.0`, `bench-<set>`, `mode-<mode>` (`docs/results/final-results-v2.2.0.md` §5). The committed record is the aggregated tables, CSVs and plots under `docs/figures/v2.2.0/`.

## 18. Experimental Setup

| Parameter | Value |
|---|---|
| Run length | 15 s simulated, step 0.01 s, 1500 steps |
| Policy window | steps ≥ 300 (after warm-up) |
| Seeds | 0, 1, 2 (n = 3 per cell); ns-3 seed = Python seed + 1 |
| Statistics | mean ± 95 % CI (Student t); paired difference vs BEB uses the same ns-3 seed |
| Offered load | 150 Mbps per station (saturated) unless stated |
| Binary | fixed (v2.0.0 `*-cwfix`), 81 runs, all PASS, no `cw.cc` change in v2.1–v2.2 |

Experiments:

| # | Experiment | Runs |
|---|---|---|
| 1 | Main comparison, 20,40 stations at 150 Mbps | 9 |
| 2 | Scaling at a fixed 60 stations, N = 2, 4, 6, 10 (equal split) | 36 |
| 3 | AP imbalance: 5,55 and 5,5,5,45 | 18 |
| 4 | Offered load 0.5 / 1 / 150 Mbps at 20,40 | 18 (+ #1) |

## 19. Baselines

- **BEB (802.11):** ns-3 default DCF, CW 16..1024, no agent.
- **Global-CW OSCAR:** one DDPG agent, one CW for all APs (§16).
- **Independent per-AP DDPG:** the proposed core method.

## 20. Results

Aggregate throughput in Mbps, mean ± 95 % CI over 3 seeds. Source: `docs/figures/v2.2.0/*/tables.md`.

### 20.1 Main comparison, 20,40 at 150 Mbps

| Mode | Aggregate | AP1 / AP2 | Jain | Phy loss | Paired vs BEB |
|---|---|---|---|---|---|
| BEB | 27.30 ± 0.63 | 9.48 / 17.82 | 0.913 | 0.747 | n/a |
| Global-CW | 36.29 ± 7.16 | 12.49 / 23.81 | 0.911 | 0.624 | +33.0 ± 29.0 % |
| Independent | 25.78 ± 20.80 | 9.26 / 16.52 | 0.837 | 0.765 | −5.6 ± 76.0 % |

![Aggregate throughput, 20,40](../figures/v2.2.0/main-20-40/aggregate_throughput.png)
![Per-AP throughput, 20,40](../figures/v2.2.0/main-20-40/per_ap_throughput.png)
![CW traces, 20,40](../figures/v2.2.0/main-20-40/cw_traces.png)

### 20.2 Imbalance

| Topology | BEB | Global | Global vs BEB | Independent | Independent vs BEB |
|---|---|---|---|---|---|
| 5,55 | 28.64 ± 3.03 | 37.07 ± 5.45 | +29.7 ± 29.5 % | 27.14 ± 11.62 | −5.4 ± 36.2 % |
| 5,5,5,45 | 27.25 ± 1.47 | 36.28 ± 8.05 | +33.2 ± 29.3 % | 22.81 ± 3.55 | −16.2 ± 17.3 % |

![Aggregate throughput, imbalance](../figures/v2.2.0/imbalance/aggregate_throughput.png)

### 20.3 Offered load, 20,40

| Load / STA (Mbps) | BEB | Global | Independent | Global vs BEB | Independent vs BEB |
|---|---|---|---|---|---|
| 0.5 | 27.90 ± 0.85 | 29.64 ± 1.36 | 28.86 ± 2.84 | +6.3 ± 8.0 % | +3.5 ± 13.3 % |
| 1 | 27.86 ± 1.60 | 38.96 ± 0.40 | 11.43 ± 13.75 | +39.9 ± 8.3 % | −58.8 ± 50.3 % |
| 150 | 27.30 ± 0.63 | 36.29 ± 7.16 | 25.78 ± 20.80 | +33.0 ± 29.0 % | −5.6 ± 76.0 % |

![Load sweep](../figures/v2.2.0/load-sweep/load_sweep.png)

### 20.4 Attempt to beat Global-CW OSCAR (v3.0.0)

Question: can a per-AP-CW method match or beat the global-CW agent, not just BEB? v3.0.0 added trainer options only (`--mode shared`, `--obs hist`, `--alpha`, `--rewardScale`; `cw.cc` unchanged). `shared` uses one set of actor and critic weights for all APs, each AP still sets its own CW from its own observation, so per-AP isolation is relaxed (ADR-0004). V5 = shared + windowed-loss observation + reward x100 + alpha 0. Full tables: `docs/results/improvement-v3.0.0.md`.

20,40 at 150 Mbps, aggregate Mbps, n = 3 seeds:

| Controller | Aggregate | vs Global (paired) |
|---|---|---|
| BEB | 27.30 ± 0.63 | |
| Global-CW | 36.17 ± 6.95 | |
| V5 | 37.08 ± 0.85 | +2.8 ± 16.9 % |
| A1 (shared, loss-only observation, x100) | 38.48 ± 2.64 | +6.9 ± 26.7 % |

V5 vs BEB is +35.8 ± 6.2 %. Imbalance, V5 minus Global, n = 3: 5,55 +5.0 ± 13.6 %; 5,5,5,45 +3.8 ± 10.8 %. 6x10, seed 0 only: −0.9 %.

Facts: every paired interval against Global includes 0, so no gain over Global is shown. V5's seed spread is lower at 20,40 (±0.85 vs ±6.95) and at 5,55. In the independent-agent screen (n = 1 each) the added observation and reward changes lowered throughput; only parameter sharing reached Global level. Per-AP CWs end nearly equal even under imbalance. Inference (untested): V5 behaves like a global CW with shared weights, and the variance reduction may come from the N transitions per step feeding one agent.

### 20.5 Per-AP scenario: hidden chain and a fairness reward (v3.4.0)

Question: in a topology where the best CWs differ per AP, does a per-AP learner with a cooperative reward beat BEB and Global-CW? ADR-0005 approved a coarse loss matrix (the "detailed interference modelling" item in the out-of-scope list is touched only to this extent). Scenario `10,10,10 --apHidden 1-3`: BSS1 and BSS3 cannot hear each other (200 dB), every other pair keeps 50 dB; 150 Mbps per station, 15 s. Reward option `--reward pf` (sum of log per-AP goodput). Full tables: `docs/results/per-ap-scenario-v3.4.0.md` (section numbers below refer to it).

Static gate (§3, no learning, n = 3): the middle AP is starved under BEB (35.0 / 1.4 / 35.2 Mbps). An asymmetric static setting 256,128,256 beats the best common CW on PF utility by +0.15 ± 0.02, and 256,64,256 beats it on the weakest AP by +7.62 ± 0.27 Mbps. The gain is a fairness gain; aggregate falls from 62.9 (common 256) to 53.9-59.5 Mbps.

Frozen evaluation (§4, 2 training episodes, eval seeds 100-107, paired by seed, mean ± 95 % CI, exact Wilcoxon p = 0.008 means all 8 seeds agree):

| Arm | aggregate | AP1 / AP2 / AP3 | PF utility | min-AP |
|---|---|---|---|---|
| BEB | 71.63 ± 0.62 | 34.95 / 1.44 / 35.24 | 7.48 ± 0.04 | 1.44 ± 0.07 |
| Global-CW | 76.46 ± 0.34 | 36.93 / 2.58 / 36.94 | 8.16 ± 0.07 | 2.58 ± 0.21 |
| independent, aggregate reward | 68.77 ± 0.15 | 38.50 / 1.26 / 29.01 | 7.25 ± 0.05 | 1.26 ± 0.07 |
| independent, `--reward pf` (trainSeed 0) | 62.82 ± 1.18 | 24.76 / 9.99 / 28.07 | 8.84 ± 0.01 | 9.99 ± 0.54 |
| static 256,128,256 (§4b) | 59.58 ± 0.11 | 23.18 / 13.25 / 23.15 | 8.87 ± 0.00 | 13.25 ± 0.09 |

Facts:
- A PF-reward independent per-AP learner beats BEB and Global-CW on PF utility and weakest-AP throughput in all 8 eval seeds, for every policy seed (3 seeds DDPG, 2 seeds each TD3 and CWmin-only, §4c-§4h). Against BEB: +0.92 to +1.44 PF and +2.9 to +12.3 Mbps min-AP across all policies. The price is aggregate throughput (-3 to -14 Mbps vs BEB; Global-CW has the highest aggregate).
- With the aggregate-goodput reward the independent learner is worse than BEB on all four metrics.
- The learned CWs separate per AP, but the policies differ from seed to seed (final CWs 208/41/77, 218/123/251, 286/311/347). The comparison with the static oracle is not stable: independent pf is -0.03 ± 0.01 PF (seed 0), +0.02 ± 0.02 (seed 1) and -0.27 ± 0.05 (seed 2) against 256,128,256, and 3-5 Mbps under it on min-AP.
- Not stable across policy seeds, so not claimed: independent-vs-shared ordering on PF, DDPG vs TD3 vs CWmin-only ranking, "matches the oracle". The policy-to-policy spread is larger than the eval-seed CIs.
- Unsaturated AP3 (`--apLoads 150,150,1`, §4g): BEB gives AP2 11.25 Mbps instead of 1.4; independent pf ties the static 256,128,256 on PF (+0.00 ± 0.01) and beats BEB by +0.31 ± 0.01, and its CWs adapt to the load (AP3 stays at 16). `150,150,20` still saturates AP3 and was not an uneven-load test (§4f).

Inference (untested): the PF reward gives each learner an objective that the static asymmetric optimum also maximises, so reaching about the oracle's PF is expected; the claim that survives is "a cooperative fairness reward lets independent learners fix the hidden-node starvation that BEB and a single common CW leave".

## 21. Scaling Analysis

Total stations fixed at 60, equal split, N = 2, 4, 6, 10 (removes the confound of growing station count in the earlier v1.x sweep).

| N | BEB | Global | Global vs BEB | Independent | Independent vs BEB |
|---|---|---|---|---|---|
| 2 | 27.38 | 36.23 | +32.3 ± 26.3 % (3/3) | 28.44 | +3.8 ± 27.2 % |
| 4 | 27.55 | 35.64 | +29.5 ± 27.5 % (3/3) | 20.14 | −27.0 ± 21.8 % |
| 6 | 28.06 | 36.92 | +31.5 ± 18.9 % (3/3) | 18.07 | −35.8 ± 109.7 % |
| 10 | 27.89 | 36.87 | +32.2 ± 23.9 % (3/3) | 14.99 | −46.2 ± 12.2 % |

![Aggregate vs N](../figures/v2.2.0/fixed60-scaling/aggregate_vs_n.png)
![Paired delta vs N](../figures/v2.2.0/fixed60-scaling/paired_delta_vs_n.png)
![Min per-AP throughput vs N](../figures/v2.2.0/fixed60-scaling/min_ap_vs_n.png)
![Jain index vs N](../figures/v2.2.0/fixed60-scaling/jain_vs_n.png)

Full table (per-station, per-AP, minimum per-AP, Jain, convergence step, run time, deassociation counts): `docs/figures/v2.2.0/fixed60-scaling/scaling_table.md`. Run time is about linear in the number of stations, not APs.

## 22. Discussion

Facts:
- BEB is flat in N at a fixed total load (27.4–28.1 Mbps).
- The global-CW agent is above BEB in all 3 seeds at every N, with +29.5 % to +33.2 % in every saturated topology and at 1 Mbps; the paired confidence-interval lower bounds are close to 0.
- Independent agents are negative from N = 4 (the interval excludes 0 at N = 4 and N = 10). Under imbalance the intervals include 0. At 1 Mbps they are far below BEB.
- Independent per-AP throughput and reward drift down late in the 20,40 run (`reward.png`, `convergence.png`). Minimum per-AP throughput at N = 10 is 0.22 ± 0.05 Mbps against 2.24 ± 0.02 Mbps for BEB.

Inference (not tested):
- Independent learners face a non-stationary environment because every other AP's CW changes the contention each agent sees; this may explain the decay with N.
- A weak learning signal (small, saturated reward) may contribute to modest and uneven gains.
- The global agent benefits from a signal that reflects the whole network; it does not respect the per-AP isolation rule, so the comparison shows an upper reference, not a deployable method.

Per-AP scenario (v3.4.0, §20.5):
- Facts: in a hidden chain the single global CW leaves the middle AP at 2.6 Mbps, while PF-reward independent per-AP learners lift the weakest AP (the middle one) to 4.4-13.8 Mbps depending on the policy (BEB: 1.4). This is the setting where per-AP control does better than the global agent, on fairness, not on aggregate throughput.
- Inference: the earlier failure of independent agents (§21) is partly an objective problem. With the aggregate reward the independent learner cannot see the starved AP and is worse than BEB here; with a PF reward it is not.

## 23. Limitations

- n = 3 per cell; most agent-versus-BEB intervals are wide and several include 0.
- Active sinks were measured only at 20,40 / 150 Mbps, seed 0: 19/20 and 39/40 in BEB, global and independent alike, so inactive stations do not explain the agent gain there (`docs/results/robustness-v2.0.0.md` §F.5, n = 1). Other topologies were not measured.
- Traffic starts at t = 0 (inherited), which causes late association at 220 STAs (not seen in the final-set topologies, §G.5 of the robustness doc, dry BEB, n=1); the final set was not rerun with `--trafficStart`.
- Observation is one loss scalar; the 300-value history is unused.
- Reward scale is small in saturation.
- Pre-fix (CW 0/0) results for v1.x and the central critic are not comparable to the final set.
- The v3.0.0 ablations V1–V4 and A2 are single-seed, 6x10 is single-seed, and all of v3.0.0 uses one load (150 Mbps per station) and 15 s runs.
- Raw traces and `.wandb` files are local only, so regeneration needs the local run directories.
- A single channel, fixed positions, uplink UDP only; no mobility and no dynamic stations.
- v3.4.0 (§20.5): one coarse topology (a 3-AP hidden chain, 200 dB / 50 dB loss), one main load, 2 training episodes, 15 s runs; 3 policy seeds for DDPG and 2 for TD3 and CWmin-only. Policy-seed variance exceeds the eval-seed CIs and no policy-seed test was run, so rankings between algorithms and the "matches the static oracle" claim are not shown. The static oracle comes from a coarse grid and is not a proven optimum. The PF reward matches the PF/min-AP metrics by construction. Idle-sensing and IdleSense/Bianchi heuristics (v3.3.0) were not part of these runs.

## 24. Future Work

1. Find why the central critic collapsed at N = 10 (cause untested); rerun it on the fixed binary.
2. Rerun the final set with traffic started after association.
3. Measure active-sink counts for other topologies and seeds (only 20,40 seed 0 is done).
4. Reward shaping that uses more of [0, 1], and more seeds. (Windowed-statistics observation was tried in v3.0.0, §20.4, with no throughput gain.)
5. Find a setting where per-AP CWs should differ (asymmetric load, mixed traffic) and test why shared weights lower seed variance. Check single-AP OSCAR against BEB at 15 and 50 stations to compare with the published gain (`docs/reference/oscar-baseline-metrics.md`).
6. Neighbourhood information sharing between APs as a middle point between independent and global.

## 25. Conclusion

The project delivers a working multi-AP OSCAR in one ns-3 process with strictly isolated per-AP DDPG agents, per-AP statistics and CW control, baselines, and a reproducible benchmark pipeline. Under saturation a single shared CW agent beats BEB by about 30 % at every tested size, while isolated per-AP agents match BEB at two APs and degrade as APs are added. Learning to coordinate through local loss alone is therefore not sufficient in this setup. The central critic prototype did not change that conclusion, and the open causes are listed in §23–24. Relaxing isolation with shared weights (v3.0.0) brings per-AP controllers to the global agent's level, not past it (§20.4). In a hidden-chain topology with a proportional-fairness reward (v3.4.0, §20.5), strictly isolated per-AP agents do beat both BEB and the global agent on PF utility and on the weakest AP in all 8 evaluation seeds, at lower aggregate throughput; which learner or algorithm is best is not settled by the policy seeds run.

## 26. References

Fill in (user to supply full entries):

- [OSCAR] Grasso, Raftopoulos and Schembra, "OSCAR: A Contention Window Optimization Approach Using Deep Reinforcement Learning," IEEE ICC 2023, doi:10.1109/ICC45041.2023.10279663.
- [REF:setl] SETL-DQN(MA) paper.
- [REF:ato] Adaptive Throughput Optimization paper.
- [REF:lild] LILD-DQN paper.
- [REF:pdcf] PDCF-DRL paper.
- [DDPG] T. P. Lillicrap et al., "Continuous control with deep reinforcement learning," ICLR 2016, arXiv:1509.02971.
- [ns-3] ns-3 network simulator, version 3.29, https://www.nsnam.org.
- [ns3-gym] P. Gawłowicz and A. Zubow, "ns-3 meets OpenAI Gym: The Playground for Machine Learning in Networking Research," ACM MSWiM 2019; code https://github.com/tkn-tub/ns3-gym.
- [REF:ieee80211] IEEE 802.11 standard.
- [W&B] L. Biewald, "Experiment Tracking with Weights and Biases," 2020, https://www.wandb.com.

---

## Appendix A. Central critic (negative, pre-fix)

Spec: `docs/design/central-critic-v1.7.0.md`, ADR-0003. Prototype: `--mode central` (N local actors, one shared critic on the global reward, joint replay). Evaluation (`docs/results/central-eval-v1.9.0.md`, n = 3, on the pre-fix binary): at N = 4 central 38.96 ± 5.11 vs independent 23.27 ± 13.19 (paired +72.5 ± 82.4 %, interval includes 0); at N = 10 central 3.20 ± 4.91 vs independent 9.00 ± 6.16 (paired −59.4 ± 71.5 %, interval includes 0), and −83 % against BEB. At N = 10 it collapsed after step ~300 (cause untested). The pre-agreed rule (beneficial only if the paired interval excludes 0 at N = 10) was not met; it stays optional and was excluded from the final set. Because the numbers predate the CW-start fix, they are not directly comparable to §20–21.

## Appendix B. Reproducing the results

From `ns-3.29/scratch/linear-mesh`, with `../../venv/bin/python` and the local run directories; commands are in `docs/results/final-results-v2.2.0.md` §4 (`aggregate_bench.py`, `scaling_analysis.py --preset fixed60`, `load_sweep.py`). Reproducibility checks (identical traces across repeated runs, seed sensitivity) are in `docs/reference/reproducibility-v2.1.0.md`. Build and run: `cd ns-3.29 && ./waf build --target=linear-mesh`; training entry point `OSCAR_multi_ap_train.py --apStaCounts 20,40 --mode {beb,global,independent}`.

## Appendix C. Version history

v0.1 baseline freeze → v0.2 design → v0.3 two-AP topology → v0.4 per-AP statistics → v0.5 per-AP CW → v0.6 multi-AP ns3-gym → v0.7 independent agents → v0.8 W&B → v0.9 validation → v1.0 core → v1.1–v1.6 benchmarks and 2→10 AP scaling (pre-fix) → v1.7–v1.9 central critic (spec, prototype, evaluation) → v2.0 robustness and CW-start fix → v2.1 reproducibility → v2.2 final results → v2.3 this report → v2.4 presentation → v2.5 final audit → v2.7 W&B sync of the final runs → v3.0 attempt to beat Global-CW (§20.4) → v3.1 ceiling → v3.2 fair protocol → v3.4 per-AP hidden-chain scenario (§20.5).
