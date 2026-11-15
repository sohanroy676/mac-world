# Mentor papers, batch 2: what can improve mac-world (2026-11-06)

15 PDFs reviewed (contents treated as data). Goal held fixed: maximise CW optimisation, scored as gap closed (GC) across the v4 suite.
Labels: fact = read in the paper or our code; inference = my reasoning; decision = my choice.

## 1. The mentor's suggestion: Gumbel noise instead of Gaussian noise

Source: Tu and Ma, "A DRL with Gumbel Distribution Approach for CW Optimization in IEEE 802.11 Networks", CMC 84(3), 2025 (TSP_CMC_66899).

What the paper does (fact):
- A **discrete** DDQN picks one of K = 8 CW-threshold actions. Gumbel noise g = -ln(-ln U) is added to the 8 Q-values and the action is argmax(Q + g) (Gumbel-max), or softmax((log Q + g)/τ), top-k, or a visit-count-scaled Boltzmann-Gumbel. This **replaces ε-greedy**.
- Gumbel-Softmax was its best strategy. SETL-DDQN(Gumbel) beats SETL-DDQN (ε-greedy) by 2.04 % in mean normalised throughput (4.72 % in the second table).
- No seeds, confidence intervals or simulator name are reported. Baselines are BEB, SETL and DQN variants; no IdleSense-class or static-oracle baseline.

What our code does (fact, `OSCAR_multi_ap_train.py:283-297`):
- DDPG with a **continuous** action in [-1, 1], mapped to a in [0, 6] and CW = 2^(4+a) (cw.cc:366).
- Exploration is Gaussian N(0, 0.1) added to the actor output, after 300 uniform warm-up steps. No noise at evaluation.

Fit (inference):
- The paper's mechanism, Gumbel-max, is a way to sample a discrete action from a softmax over Q-values. Our DDPG has no Q-value per action to perturb, so the paper's result does not transfer directly.
- What does transfer is the shape of the noise. Gumbel noise is right-skewed, with a heavier tail toward larger actions. In our mapping a larger action is a larger CW, so Gumbel noise explores larger CWs more often. That could help in the dense and hidden-node cells, where the oracle CWs are large (512 at 20,40; 256/128/256 in the chain).
- Raw Gumbel(0, β) has mean 0.577β, so it would also bias every exploratory action upward. To separate "tail shape" from "bias", the test uses noise centred to mean 0 and scaled to the same standard deviation as the Gaussian (β = σ·√6/π, subtract 0.5772β).
- Exploration only shapes training; the evaluated policy is noise-free. So any gain shows up as a better learned policy or lower seed variance, which is our largest risk.

Decision: **adopt as a pre-registered ablation in M3 step 1**, not as a default.
- New flag `--noiseDist {gaussian,gumbel,gumbel-raw}` in the trainer (Python only, about 10 lines; no ns-3 change). `gumbel` is centred and variance-matched, and `gumbel-raw` is the paper's uncentred form.
- Run on S4 (chain) and S2 (20,40), 3 training seeds each, reusing the Gaussian step-1 runs. About 12 training jobs, roughly 10 to 12 h (inference from the M3 budget).
- Adoption rule: switch RAFA to Gumbel only if mean GC on the selection seeds is at least 0.02 higher on both S4 and S2 and the seed spread is no wider. Otherwise keep Gaussian and report the null result. With 3 seeds this is a screening test, not a significance claim.
- Not adopted: Gumbel-max or Gumbel-softmax over discrete CW levels. That would turn RAFA into a DQN, which contradicts the DDPG design and the evidence base (v3.x) we built the plan on.

## 2. The other 14 papers

| Paper | Topic | Use for us |
|---|---|---|
| Yan, Du, Zhang, Dong, "DRL-based CW Optimization for IEEE 802.11bn" (PID2024002425; this is **drlCW**) | per-AP MARL, OBSS, beacon-shared observations | Already our closest prior work. The PDF gives the exact observation [cw, PER, throughput, delay, delay-CDF] and the relative-to-CSMA reward. **Adopted:** the M2 re-implementation follows these definitions. |
| Wilhelmi/Bellalta group, "Learning-Based Channel Access in Wi-Fi: A MAB Approach" (IEEE, WiPySim) | contextual vs non-contextual MAB over channel, width, CW | Its CW arms {2^(i+4)-1, i=0..6} match our 16..1024 range (fact). Context helps; decentralised greedy learners hurt legacy BSSs and show "policy-chasing" (fact). **Adopted:** (a) our UCB baseline gets a contextual variant keyed on active-station count; (b) new extended cell S11, learners coexisting with a legacy BEB AP, scored on the legacy AP's throughput. |
| Tu and Ma, M2I-CWO (ICT Express 11, 2025) | multi-agent Dueling-DQN, multi-parameter CW | This is the "ICT Express 2025 MADRL" paper our notes listed as unread. Python simulator, BEB/SETL baselines. Related work only; it does not make our robustness claim. |
| Tu and Chen, CIPD-BiDQN (ICT Express, in press) | Bi-LSTM dueling DQN, multi-rate 802.11ax | Python 802.11ax-lightsim simulator (fact). Related work only. |
| Yamada et al., hybrid CW + p-persistent (IEICE ComEx 15(8)) | dense WLAN, CW cap reached | Changes STA access rules, which is a MAC change and out of scope. **Adopted check:** in M1, flag any cell whose oracle CW sits at the grid edge 1024, since then the cap, not the controller, limits GC. |
| Nunez et al., DRL MAPC scheduling (IEEE TMLCN 2026; arXiv 2507.19377 also attached) | PPO scheduling for 802.11bn Co-SR | Scheduling, not CW. Venue now confirmed as IEEE TMLCN (fact). Its p99-delay metric supports our GC_D on log p99. Citation update only. |
| Hao et al., transformer ICL (arXiv 2508.09146v4) | in-context CW | Reviewed in batch 1. No new action. |
| CW tuning for Multi-Link (Wi-Fi 7 MLO, TCP, ns-3) | RL CWmin per link | MLO is not in ns-3.29 (inference from the version). It runs 10 seeds, like our protocol. Threat to validity noted: our traffic is UDP, and TCP may change rankings. Not adopted. |
| DRL A-CCC for uplink OFDMA in multi-UAV | centralised OBO/UORA control | OFDMA random access is not in ns-3.29. Not adopted. |
| AP energy minimisation, 802.11ah (absorbing Markov chain, real devices) | analytic CW for energy | Different objective (AP energy). Cited as a model-driven, non-saturated reference. |
| Adaptive CW selection in vehicular networks (IEEE, ns3-gym) | per-vehicle actor-critic, CBR and neighbour estimate | Mobility is out of scope. Its neighbour-count input supports our active-station input. Related work only. |
| VANET actor-critic CW (Procedia CS 235, 2024, ns-3) | 802.11p AC | Mobility out of scope; BEB-only baseline. Related work only. |
| GNN-SARSA multi-UAV trajectory (IoT 40, 2026) | UAV trajectory | Off-topic for CW. Not adopted. |

## 3. Changes to the plan (revision 7)
| # | Change | Where | Estimate |
|---|---|---|---|
| 1 | Gumbel exploration ablation (`--noiseDist`), adoption rule above | M3 step 1 | about 10 to 12 h |
| 2 | drlCW re-implementation uses the paper's exact observation and reward | M2 | no extra |
| 3 | Contextual UCB variant | M2 | about 3 h |
| 4 | S11: learners with one legacy BEB AP (needs a per-AP BEB flag in cw.cc) | M5 extended | about 6 h |
| 5 | Grid-edge (CW = 1024) check for oracle cells | M1 | no extra |
| 6 | Citations: drlCW PDF, M2I-CWO, CIPD-BiDQN, Gumbel paper, MAB paper, Nunez TMLCN | M7 | 1 h |

The core M0 to M4 path grows by about 13 h, to about 223 h. The extended path grows by about 6 h.

## Open unknowns
- The Gumbel paper's simulator and number of runs are not stated.
- The per-job training time on S4 has not been measured on the new code. The estimates come from the M3 budget.
