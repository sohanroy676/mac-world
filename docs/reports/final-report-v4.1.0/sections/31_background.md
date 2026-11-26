## 1. Background and related work

### 1.1 Contention in 802.11
In the 802.11 distributed coordination function (DCF) a station that wants to send waits a random number of idle slots drawn from [0, CW]. A small CW makes collisions likely when many stations compete; a large CW wastes airtime on idle slots. Binary exponential backoff (BEB) doubles the CW after a failed transmission and resets it after a success. In dense networks BEB is not throughput-optimal, because a station can only infer the load from its own failures.

With several APs on the same channel the problem has a second layer. Each BSS (an AP and its stations) contends with the others. If every BSS only maximizes its own goodput, the result can be worse for everybody, and if some BSSs cannot hear each other (hidden nodes), the middle BSS can be starved. This is the setting studied here.

### 1.2 OSCAR
OSCAR (Grasso, Raftopoulos and Schembra, ICC 2023) controls the CW of one AP with a DDPG actor-critic agent. The AP observes a loss ratio, outputs a CW for its stations every 10 ms, and is rewarded for goodput. The original paper reports relative gains only (about +11 % with 15 stations up to +40 % with 50 stations over 802.11, after convergence), so this project re-measures OSCAR against BEB in its own simulator. The v0.1.0 code audit found where the repository differs from the paper (for example the agent uses one scalar of the loss history as its state); the code is authoritative over the paper throughout.

### 1.3 Related work used in this project
| Work | Idea | Role here |
|---|---|---|
| Heusse et al., IdleSense (2005) | Keep the mean number of idle slots between transmissions at a target value | Rule-based rival, published rule, target derived for this PHY |
| Patras et al., DAC (IEEE TMC 2011) | PI controller on CWmin from the failure and collision rates, updated once per beacon | Rival (AP-level, Ziegler-Nichols gains); also the model-based static CW |
| Gawłowicz, Walrand and Wolisz, KW (2021) | Distributed proportional-fair gradient search on the CW, reported about +20 % over BEB in ns-3 | Rival (AP-level; uses neighbour goodput, so it breaks per-AP isolation) |
| BLADE (NSDI 2026) | Rule-based CW adaptation aimed at tail latency | Rival (re-implemented following the paper) |
| Yan et al., drlCW (IEEE VTC 2024) | Per-AP DDQN with LSTM, neighbour observations through beacons, reward gated against CSMA | Closest prior learning work; re-built from the paper |
| CCOD / RLinWiFi | DDPG agent on loss history with one CW for the network | Global-form learner |
| Contextual UCB | Bandit over CW exponents keyed on the number of active stations | Bandit rival |
| Recent work 2023-2026 (for example Hao et al. on in-context learning, Nunez et al. on multi-AP scheduling) | Learning-based MAC control | Checked; none makes the same multi-AP claim with the same baselines |

Recent deep-RL papers on CW optimization mostly compare only against BEB. A guiding rule of this project is therefore that every learned result is also compared with strong heuristics and with the best static CW of the same scenario.

### 1.4 What is new in MAC-WORLD
- A single ns-3 process with N APs, per-AP statistics, per-AP CW control and a multi-agent gym interface.
- Per-AP agents with strict isolation of observation, reward and action, and baselines that relax this on purpose (a shared CW, a shared actor, a central critic, central controllers).
- A scenario suite with hidden nodes, unequal loads and dynamic load, and metrics beyond aggregate throughput: station-weighted alpha-fair utility, a fair floor against BEB, and a share-of-ceiling measure that uses a validated static optimum.
- A reproducible pipeline: every run is a job with a recorded trace hash, executed on GitHub Actions in a pinned container image, with 0 trace-hash mismatches across machines in the non-learned runs.
