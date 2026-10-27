# Research: beating OSCAR and BEB

Status: research note, 2026-10-27. No new runs. Based on `main` 76cedcc (`cw.cc`, `OSCAR_multi_ap_train.py`, `agents/our_ddpg/`, results docs v1.1.0 to v3.0.0) and the papers in §8. Web version: https://claude.ai/artifact/E9krr69c1gQkaN9cxr8yVM (private).

Labels: **fact** = read from code or committed results; **inference** = reasoning, untested; **lit** = reported by a paper; **unknown** = needs a run.

## 0. Bottom line
1. **The simulated network is one collision domain.** `set_phy` in `cw.cc` builds a `MatrixPropagationLossModel` with `SetDefaultLoss(50)` and never calls `SetLoss` for a pair. Every link, including links between BSSs, is 50 dB, so every STA hears every other STA and the 50 m AP spacing has no effect (fact). In one collision domain a single common CW is close to the best any per-AP scheme can do on aggregate throughput. Per-AP CWs mainly move airtime between APs (inference). This explains why V5 and A1 are at Global level and why their CWs do not separate.
2. **Independent OSCAR is below BEB mainly because of a selfish CW game with no brake.** The per-AP goodput reward makes lowering its own CW pay off for each AP. OSCAR's CWmin = CWmax removes BEB's per-collision back-off. The repo's traces show CWs drifting from about 2^8 to 2^6 and phy loss rising toward 0.95 at N=10 (fact).
3. **Cheapest first step:** a static CW sweep with no learning (`--apCws`, `--disableGym`) to get the throughput ceiling.
4. **Where a real win is likely:** (a) a topology where the best CWs differ per AP (partial overlap, uneven load); (b) channel-sensing local observations (idle slots, retries); (c) a cooperative reward with a fairness term, plus a heuristic prior (IdleSense or Bianchi) for residual RL; (d) MAC knobs that OSCAR lacks (TXOP, A-MPDU).
5. **Fix the protocol before claiming anything:** multi-episode training, frozen noise-free evaluation, n ≥ 8 paired seeds, and IdleSense as a non-RL baseline. Today every RL number is measured during learning with exploration noise on, with n = 3 (fact).

## 1. What "beat OSCAR" means (agreed framing)
Each AP keeps its own CW. The baseline is independent OSCAR in each AP. "Ours" must add something that OSCAR-per-AP lacks. Global-CW OSCAR is a reference point, not the bar.

| Comparator | In this repo | 20,40 result (n=3) | Role |
|---|---|---|---|
| BEB | `--mode beb` (ns-3 `dryRun`, CW 16..1024, doubling) | 27.30 ± 0.63 Mbps | Must beat |
| OSCAR per AP | `--mode independent` | 25.78 ± 20.80 | Must beat (main baseline) |
| Global-CW OSCAR | `--mode global` | 36.29 ± 7.16 | Reference; match or beat |
| V5 / A1 (shared) | `--mode shared` (ADR-0004) | 37.08 ± 0.85 / 38.48 ± 2.64 | Current best "ours" |
| IdleSense (proposed) | not in repo | — | Non-RL baseline to add |

Report more than aggregate throughput: min-AP throughput and Jain (Global starved one AP at Jain 0.64 on one seed in v1.1.0), true collision/retry rate, delay at non-saturated load, convergence time, and seed variance. V5's lower variance (±0.85 against ±6.95) and lower phy loss (0.533 against 0.626) are already reportable (fact).

## 2. Why independent OSCAR is below BEB

| # | Cause | Evidence | Cheapest test |
|---|---|---|---|
| D1 | Selfish CW game: own-goodput reward makes a lower own CW individually rational. Each agent bears about 1/N of the harm it causes, so it gets worse with N. | v1.3.0: CW 16 gives 13.8 Mbps and CW 1024 gives 0.59 Mbps on the shared channel (fact). Independent CWs drift from 2^8 to 2^6 (v1.1.0, fact). Trend −27 % at N=4 to −46 % at N=10 (fact). Čagalj et al. 2005: selfish CSMA/CA equilibria are inefficient (lit). | 2×2 payoff matrix: `--apCws` ∈ {64,512}² at 20,40, `--disableGym`. Then independent with `--alpha 0`, 3 seeds at N=4 and N=10. |
| D2 | No BEB safety net: `setApCw(ap, cw, cw)` gives CWmin = CWmax, so a too-low CW never backs off. | `MyExecuteActions` (fact). Global settles near 2^8, independent goes lower (fact). | Idea #8 (CWmin only, CWmax 1023). |
| D3 | The observation cannot see the cause: `(PhyTx − Rx)/PhyTx` counts the AP's own ACKs and beacons in PhyTx (about 0.5 with zero collisions) and cannot attribute losses to a BSS. A 10 ms window holds only about 15 to 20 received frames. | `recordHistory` (fact). Noise level is inference. | Log `MacTxDataFailed` and the PHY idle fraction, and correlate them with throughput. |
| D4 | Non-stationary independent learners on stale replay. | Late drift, no convergence by step 1500 (fact). Shared mode has N transitions per step in one buffer and lower variance (inference). | Idea #2 (multi-episode, frozen eval). |
| D5 | Measured while learning, with N noise streams. | `--episodes 1` default; reported window = steps ≥ 300 of the same run (fact). | Idea #2. |
| D6 | Unequal reward scales: normalised by each AP's own STA count, about 0.003 to 0.007. | `recordHistory` (fact). ×100 did not help independent mode (V2, n=1, fact). | Low priority: running reward normalisation. |

## 3. The ceiling problem
For saturated DCF in one collision domain, aggregate throughput depends mainly on the total attempt rate. The optimum is reached with a common CW of about n·√(Tc/2σ) (Bianchi 2000; Bianchi and Tinnirello 2003, lit). Unequal per-AP CWs can reach the same total but not exceed it by much (inference). To beat Global-CW OSCAR with per-AP control, you therefore need either a scenario where the best CWs differ per AP (#7) or a metric where per-AP control helps (fairness, delay, convergence). Measure the ceiling with #1 first.

## 4. Ranked ideas (gain per effort, dependencies considered)
Effort assumes the current trainer and about 20 to 30 minutes per 15 s run on a 2-core laptop. Gain is a judgement unless a paper is cited.

| Rank | # | Idea | Where in code | Gain | Effort |
|---|---|---|---|---|---|
| 1 | 1 | Static CW sweep: ceiling plus payoff matrix | none (`--apCws`, script) | decides plan | XS |
| 2 | 2 | Fair protocol: multi-episode training, frozen eval, n ≥ 8 paired seeds | trainer | high (credibility) | S |
| 3 | 3 | Repair independent baseline (team reward, payoff test) | existing `--alpha 0` | high | XS |
| 4 | 8 | Agent sets CWmin only; BEB doubling kept | `cw.cc` `MyExecuteActions` + flag | med | XS |
| 5 | 9 | TD3 in place of DDPG | `agents/our_ddpg/` | med (variance) | S |
| 6 | 4 | Channel-sensing local observations | `cw.cc` traces + extraInfo; trainer obs | high | M |
| 7 | 5 | IdleSense / Bianchi heuristic baseline | trainer `--mode idlesense` | strong baseline | S–M |
| 8 | 6 | Residual RL on top of the heuristic | trainer action mapping | high (speed, stability) | M |
| 9 | 14 | Cooperative reward with fairness (proportional fair / min-AP) | trainer reward | med–high (fairness) | S |
| 10 | 7 | Scenario where per-AP CW matters | `cw.cc` `set_phy`, `scenario.h` | high (prerequisite) | M |
| 11 | 11 | Neighbour summary via beacons (mean-field) | trainer obs (+ `cw.cc`) | med | S–M |
| 12 | 12 | Federated averaging of per-AP agents | trainer | low–med | S–M |
| 13 | 10 | Cooperative MARL: MAPPO or QMIX | new agent module | med | L |
| 14 | 13 | Extra knobs: TXOP, A-MPDU, RTS/CTS, AIFSN per AP | `cw.cc` action space | high (raw Mbps) | M–L |

## 5. Ideas in detail

**#1 Static CW sweep.** `linear-mesh --disableGym=true --apCws=c1,c2 --simTime=15` with c ∈ {32, 64, 128, 256, 384, 512, 768, 1023} on the diagonal plus a coarse off-diagonal grid, 3 seeds, at 20,40. Repeat the diagonal at 6×10. Gives the best fixed common CW, the best fixed per-AP pair, and the D1 payoff matrix. No sweep exists yet; v1.3.0 only checked that per-AP CWs apply (fact). Decision rule: if best pair ≈ best common CW ≈ Global, stop chasing aggregate throughput in this topology and move to #7 and #14.

**#2 Fair evaluation protocol.** Train k episodes (for example 5 × 15 s, different ns-3 seeds), save the actor, then evaluate frozen with zero exploration noise on held-out seeds. Report the paired difference against BEB on the same seed with n ≥ 8, a t-interval and Wilcoxon. With n = 3 the t-multiplier is 4.30; with n = 8 it is 2.36. Code: `--evalEpisodes`, `--saveActor/--loadActor`, noise 0 during evaluation. Episodes already restart ns-3 (Test E).

**#3 Repair the independent baseline.** Keep strict OSCAR-per-AP (α = 1) as the faithful baseline and report D1 as a finding. Add α = 0 (and #8) as a repaired variant. V3 (α = 0.5) already recovered 20.8 → 26.2 Mbps at n = 1 (fact).

**#4 Channel-sensing local observations.** Use only what the AP's own radio measures: mean idle slots between transmissions (PHY `State` trace: IDLE / CCA_BUSY / TX / RX intervals over the 9 µs slot), busy-air fraction, failure rate from `MacTxDataFailed`/retries in the BSS, own STA count, and own CW exponent. The idle-slot count is what IdleSense regulates, because it encodes total contention (lit). This keeps ADR-0002 isolation, since it is the AP's own sensing, and removes D3. Comparable features: channel occupancy (Casasnovas et al.), idle-time ratio (E-FRL), idle time since the last ACK (FC-MAPPO). Both trace sources exist in ns-3.29 (`wifi-phy-state-helper.cc` "State", `wifi-remote-station-manager.cc` "MacTxDataFailed"; fact). Project code only, not upstream.

**#5 IdleSense and Bianchi baselines.** IdleSense (Heusse et al. 2005): AIMD on CW toward a target mean number of idle slots. The target is about 5.68 for 802.11b and must be recomputed for 802.11ax HeMcs11 timings. Bianchi/Tinnirello: estimate n from the collision probability p with n ≈ 1 + log(1−p)/log(1−τ) (Kalman-filtered), then set CW* analytically. Both are decentralised, need no training, and are near-optimal and fair in one collision domain (lit). A reviewer will ask whether these match Global.

**#6 Residual RL.** The actor outputs Δ in log2 CW (for example ±2) around the heuristic CW: `real = log2(CW_heur) − 4 + Δ`, clipped to [0, 6]. This removes the destructive random warm-up, shrinks the search space, and targets convergence time and seed variance (Silver et al. 2018; Johannink et al. 2019). Ablation: heuristic, then heuristic + residual, then pure RL.

**#7 Scenario where per-AP CW matters.** Use `MatrixPropagationLossModel::SetLoss(a, b, dB)` per pair for partial overlap. Example: a 3-AP chain where AP1↔AP2 and AP2↔AP3 hear each other but AP1 and AP3 do not, so AP2 is a hotspot. Add uneven offered loads per AP and a multi-AP `convergence` scenario with STAs joining over time. Here no single CW is optimal for all APs, so per-AP control can beat Global by design (inference). This is open "option 4". CLAUDE.md lists "detailed interference modelling" as out of scope for v1; a coarse loss matrix is a user decision. Re-validate association and per-AP stats as in v0.3 and v0.4.

**#8 CWmin only.** Add a flag that calls `setApCw(ap, cw, 1023)` so BEB doubling stays on. It keeps BEB's robustness (D2), and it is an honest, simple difference from OSCAR/CCOD, which pin CW. `checkApCw` already reads back MaxCw. Needs a rebuild and the CW readback check.

**#9 TD3.** Twin critics, delayed actor updates, target smoothing (Fujimoto et al. 2018). `Our_DDPG.py` is already the Fujimoto-style DDPG, so this is about 30 lines. Apply it to Global as well, for fairness.

**#14 Cooperative fairness reward.** Σ log(throughput_i) or total + λ·min-AP, given to all agents. A difference reward or COMA-style counterfactual is optional. One global CW cannot trade airtime between APs; a per-AP method can. Joint min-max and average rewards are standard in multi-AP bandit work (Wilhelmi et al. 2024; Iturria et al. 2024, via Casasnovas et al.).

**#11 Mean-field neighbours.** Add the mean CW and BSS size of overheard neighbour APs, which real APs can read from beacons' EDCA parameter set (Mean Field MARL, Yang et al. 2018). The state size stays fixed from N=2 to N=10. This relaxes ADR-0002 (neighbour actions, not observations), so write an ADR.

**#12 Federated averaging.** Periodic FedAvg of per-AP agents (E-FRL reports up to +14.2 % throughput over independent DRL, lit). Shared mode probably already captures most of this (inference).

**#10 MAPPO / QMIX.** MAPPO (Yu et al. 2022): shared actor plus centralised value. QMIX/VDN on the 7 discrete exponents. FC-MAPPO (Pan et al. 2025) reports about 6 points fewer collisions and +5 % system throughput over BEB (lit). Do this only after #4 and #7; on the current topology it can only reach Global level. It is on-policy, so it needs many more episodes.

**#13 Extra MAC knobs.** A-MPDU is disabled on STAs (`BE_MaxAmpduSize = 0`) and RTS/CTS is off (fact). With 1464-byte frames at HeMcs11, per-frame overhead dominates, so aggregation and TXOP gains likely exceed CW gains (inference). Run BEB and OSCAR with the same aggregation default, and frame the result as "OSCAR plus knobs". Do this last.

## 6. Recommended order (proposed milestones)
| Milestone | Content | Exit criterion |
|---|---|---|
| v3.1.0 Ceiling | #1 sweep + D1 payoff matrix at 20,40 and 6×10 | Ceiling table committed; decision recorded: is total throughput headroom over Global > CI width? |
| v3.2.0 Fair protocol | #2, #3, #8, #9; re-run BEB, Global, independent, V5 with n ≥ 8 frozen eval | Paired tables with n ≥ 8; independent baseline explained or repaired |
| v3.3.0 Sensing + heuristics | #4, #5, #6 | IdleSense baseline and residual RL compared with all baselines, n ≥ 8 |
| v3.4.0 Per-AP scenario | #7 with #14 | Partial-overlap/uneven-load topology validated; per-AP method compared with Global, n ≥ 8 |
| v3.5.0 Optional | #11, then #10, then #13 | Only if time is left; the central critic stays optional |

## 7. Lower value, given current results
- More tuning of `--obs hist`, `--rewardScale` or the obs window in this topology: A1/A2/V5 show these move the CW level, not throughput (fact).
- Another MADDPG-style central critic on the loss-only state: negative before; the state is the bottleneck (D3).
- Bigger networks or longer histories: the action is one-dimensional, and the limit is the signal and the topology (inference).
- Comparing with the OSCAR paper's numbers: it reports only relative gains (+11 % at 15 STAs, +40 % at 50 STAs). Re-run OSCAR against BEB in mac-world with one AP at 15 and 50 STAs instead (open option 3).

## 8. Sources
- Grasso, Raftopoulos, Schembra. OSCAR: A Contention Window Optimization Approach Using Deep Reinforcement Learning. IEEE ICC 2023. https://www.iris.unict.it/handle/20.500.11769/677573
- Wydmański, Szott. Contention Window Optimization in IEEE 802.11ax Networks with Deep Reinforcement Learning (CCOD). IEEE WCNC 2021. https://arxiv.org/abs/2003.01492
- Heusse, Rousseau, Guillier, Duda. Idle Sense: An Optimal Access Method for High Throughput and Fairness in Rate Diverse Wireless LANs. SIGCOMM 2005. https://www.cs.sjtu.edu.cn/~wang-xb/wireless_new/coursePages/courseMaterial/UIUC_CS_598/p121-heusse.pdf
- Čagalj, Ganeriwal, Aad, Hubaux. On Selfish Behavior in CSMA/CA Networks. IEEE INFOCOM 2005. https://infoscience.epfl.ch/record/30094
- Bianchi, Tinnirello. Kalman Filter Estimation of the Number of Competing Terminals in an IEEE 802.11 Network. IEEE INFOCOM 2003. https://doi.ieeecomputersociety.org/10.1109/INFCOM.2003.1208922
- Yu et al. The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games (MAPPO). NeurIPS 2022. https://arxiv.org/abs/2103.01955
- Pan, Wang, Ouyang, Cheng, Zhang. AI-Enhanced Distributed Channel Access for Collision Avoidance in Future Wi-Fi 8 (FC-MAPPO). arXiv 2509.23154. https://arxiv.org/html/2509.23154v1
- Yu, Liang, Ye, Jin. Hierarchical MARL-based Coordinated Spatial Reuse for Next Generation WLANs. arXiv 2506.14187. https://arxiv.org/abs/2506.14187
- Zhang, Yin, Roy, Cao. Multi-Access Point Coordination for Next-Gen Wi-Fi Networks Aided by Deep Reinforcement Learning. arXiv 2206.11378. https://arxiv.org/pdf/2206.11378
- Du, Fang, He, Yan, Lu, Luo. Federated DRL-Based Intelligent Channel Access in Dense Wi-Fi Deployments (E-FRL). arXiv 2409.01004. https://arxiv.org/abs/2409.01004
- Casasnovas, Wilhelmi, Combes, et al. Learning-Based Channel Access in Wi-Fi: A Multi-Armed Bandit Approach. IEEE TCCN (arXiv 2511.10143). https://arxiv.org/html/2511.10143v1
- Cruz, de Figueiredo, de Souza. Decentralized Deep Reinforcement Learning Approach for Channel Access Optimization. SBrT 2024. https://biblioteca.sbrt.org.br/articlefile/4631.pdf
- Ke, Astuti. Applying Deep Reinforcement Learning to Improve Throughput and Reduce Collision Rate in IEEE 802.11 Networks (SETL-DQN). KSII TIIS 2022. https://koreascience.kr/article/JAKO202209059049675.do
- Foerster et al. Counterfactual Multi-Agent Policy Gradients (COMA). AAAI 2018. https://arxiv.org/abs/1705.08926
- Cited from background knowledge, not fetched for this note: Bianchi 2000 (IEEE JSAC, DCF model); Fujimoto et al. 2018 (TD3); Yang et al. 2018 (Mean Field MARL); Rashid et al. 2018 (QMIX); Lowe et al. 2017 (MADDPG); Silver et al. 2018 and Johannink et al. 2019 (residual policy learning); Wolpert and Tumer (difference rewards); Szczech et al. 2025, Wilhelmi et al. 2024, Iturria et al. 2024 (via Casasnovas et al.).
