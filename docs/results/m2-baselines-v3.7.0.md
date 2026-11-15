# M2 (v3.7.0): new baselines

Status 2026-11-05: BEB + RTS/CTS, a Gawłowicz-style KW search, a per-AP UCB bandit and CCOD (Global form) are built, tuned where the plan asks for it, and scored on S2, S4 and S5a at eval seeds 100-109 (n=10, 30 s, 5 % floor slack). **Not built:** drlCW, Patras PI, BLADE-style, Bianchi/Kalman (their texts were not read; no code from memory, per the plan). Job lists, tables and logs: `docs/figures/v3.7.0-baselines/`; code: `ap_controllers.py`, trainer modes `kw`, `ucb`, `ccod`, `m2_tune_analysis.py`, job sets `a6`-`a8` in `m1_jobs_v3_6_0.py`.

## What each baseline is (and where it deviates)
- **BEB + RTS/CTS:** `--mode beb --useRts` (RtsCtsThreshold 0). No parameters.
- **KW:** distributed asynchronous Kiefer-Wolfowitz search on y = log(lam/(1-lam)), lam = 2/(CW+1) (arXiv 2102.05149, Alg. 2; PDF text read 2026-11-03; constants in memory). Deviations: (1) AP level, the AP sets its BSS CW; (2) each AP's utility sums n_j ln(x_j/n_j) over BSSs it can hear, read from the trainer's rx counters via the `--apHidden` hearing graph, so it uses neighbour information and breaks ADR-0002 isolation by design; (3) the paper writes y - eta*g for a maximised utility, we ascend (inference: not explained in the text); (4) CW 16..1024; (5) stations read CW as 2^k-1 (cw.cc ECW = floor(log2(CW+1))), so the paper's delta 0.2 probes are mostly invisible to them.
- **UCB per AP:** UCB1 over the exponents 4..10, 200 ms pulls, reward = own goodput per STA normalised like the trainer reward. Our construction, not from a paper.
- **CCOD (Global form):** the repo's `agents/ddpg` agent (RLinWiFi, from `CCOD_train.py`: 300-step history, [8,128,16] layers, gamma 0.7, lr 4e-4/4e-3, 12 episodes of 15 s) with one CW for all APs, network-loss history as input and network goodput as reward. The CCOD paper (arXiv 2003.01492) was not read. Deviation: `teacher.train` stores the raw observation as the state, which cannot feed the LSTM, so the processed previous and next observation are stored. One training seed (2000 -> ns-3 2001+), no tuning sweep, 12 training episodes against 2 for Global/OSCAR.

## Tuning (selection seeds 0-2, 30 s, S2 and S4; `tune_analysis.md`)
Rule fixed before the runs: highest mean alpha-1 GC over S2 and S4 among settings floor-feasible on both. KW (delta, eta): paper (0.2, 0.1) 0.36 / 0.90 (infeasible on S4); (0.7, 0.1) 0.78 / 0.89 (infeasible); **(0.7, 0.03) 0.88 / 0.93 (selected)**; (0.7, 0.01) 0.84 / 0.92. UCB c = 0.1 / 0.3 / 1: S2 GC -0.35 / -0.41 / -0.42, all infeasible on S2, so the rule has no winner; c = 0.1 (best mean) was evaluated and is labelled infeasible. CCOD got no sweep (departure from the plan's equal-tuning rule).

## GC at eval seeds 100-109 (n=10, 30 s; mean ± 95 % CI; degenerate cell -> raw U)
| Cell | Method | GC a0 | GC a1 | GC a2 | Floor a0/a1/a2 |
|---|---|---|---|---|---|
| S2 | Global-CW | 0.982±0.033 | 0.966±0.040 | 0.957±0.035 | ok/ok/ok |
| S2 | IdleSense | 0.919±0.055 | 0.914±0.059 | 0.914±0.052 | ok/ok/ok |
| S2 | KW (Gawłowicz-style) | 0.887±0.046 | 0.902±0.031 | 0.917±0.022 | ok/ok/ok |
| S2 | UCB per AP | -0.264±0.033 | -0.372±0.069 | -0.522±0.120 | infeas/infeas/infeas |
| S2 | BEB + RTS/CTS | -0.759±0.045 | -1.040±0.030 | -1.435±0.026 | infeas/infeas/infeas |
| S2 | CCOD (Global form) | 0.664±0.100 | 0.689±0.101 | 0.715±0.095 | ok/ok/ok |
| S4 | Global-CW | 0.641±0.137 | 0.325±0.067 | U -61.3 | ok/ok/ok |
| S4 | IdleSense | 0.157±0.119 | -0.092±0.034 | U -116.8 | infeas/infeas/infeas |
| S4 | KW (Gawłowicz-style) | -3.889±0.136 | 0.919±0.220 | U -16.7 | infeas/infeas/infeas |
| S4 | UCB per AP | -3.107±0.178 | 0.663±0.119 | U -25.4 | ok/ok/ok |
| S4 | BEB + RTS/CTS | -5.775±0.153 | -1.007±0.210 | U -205.4 | infeas/infeas/infeas |
| S4 | CCOD (Global form) | 1.137±0.115 | 0.537±0.054 | U -47.5 | ok/ok/ok |
| S5A | Global-CW | 0.943±0.007 | 0.939±0.014 | 0.878±0.023 | ok/ok/ok |
| S5A | IdleSense | 0.465±0.013 | -0.100±0.024 | -0.470±0.037 | infeas/infeas/infeas |
| S5A | KW (Gawłowicz-style) | 0.429±0.037 | 0.721±0.028 | 0.831±0.032 | ok/ok/ok |
| S5A | UCB per AP | -0.485±0.043 | -0.174±0.049 | 0.034±0.056 | ok/ok/ok |
| S5A | BEB + RTS/CTS | -2.234±0.015 | -3.980±0.049 | -8.173±0.203 | infeas/infeas/infeas |
| S5A | CCOD (Global form) | 0.997±0.011 | 0.989±0.018 | 0.918±0.026 | ok/ok/ok |

## Facts and what they mean
1. **BEB + RTS/CTS is worse than BEB everywhere** and infeasible in every cell: S4 aggregate 72.5 -> 51.3 Mbps and the middle AP 1.34 -> 0.51 Mbps. It does not rescue the hidden-node chain here.
2. **KW is the strongest rival in S2 and S4 at alpha 1** (0.90 and 0.92) but misses the S4 floor by a hair (edge APs 22.81 / 22.73 Mbps against 22.96 = 0.95 x floor) and sits at 0.72 in S5a against Global 0.94. The paper's own (0.2, 0.1) is weak in S2.
3. **CCOD (Global form) is feasible in every cell**, near the ceiling in S5a (0.92-1.00), 0.69 in S2 and 0.54 in S4 at alpha 1 (Global 0.33). It is not comparable with Global at equal budget: 12 training episodes against 2.
4. **In S4 at alpha 1 no method that passes the floor exceeds 0.66** (UCB 0.66, CCOD 0.54, Global 0.33; the PF learner reaches 0.95 for 2 of 3 seeds, per-scenario). That is the gap left for M3.
5. UCB is floor-feasible in S4 and S5a and infeasible in S2; its S2 aggregate is 24.9 Mbps against BEB 28.0.
Limits: n=10, one training seed for CCOD/Global/OSCAR, KW tuned on selection seeds only at 30 s, no multiplicity correction, CIs are evaluation-seed variance. S7 and S8 were not run for these baselines; selection-seed RTS runs for S8p3 and S7 (`a6`) are in the run dirs but not analysed here.

## Next
M3 (RAFA) per `docs/planning/mac-world-v4-plan.html`; optional M2 remainder (drlCW, Patras PI, BLADE-style) only after their texts are read.
