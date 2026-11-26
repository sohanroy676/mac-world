## 5. Hidden nodes, fairness and sensing heuristics (v3.1.0 to v3.7.0)

### 5.1 The hidden chain
Topology S4 has three BSSs of 10 stations in a chain: AP1 and AP2 hear each other, AP2 and AP3 hear each other, and AP1 and AP3 do not (this is the mentor's "AP1 and AP2 overlap, AP2 and AP3 overlap, AP1 and AP3 negligible" case). The two outer BSSs transmit at the same time and corrupt the middle BSS, so under BEB the middle AP receives very little (about 1.3 Mbps, against about 24.4 Mbps for each outer AP, in the BEB runs that define the fair floors of the max-CW study) while the outer APs take most of the channel. Aggregate throughput hides this, which is why the project reports per-AP goodput, the minimum over APs and a fair utility.

### 5.2 What the static analysis showed (v3.4.0, 3 seeds)
- The best common static CW is not the best static point for the chain: an asymmetric CW of 256, 128, 256 beats the best common CW on proportional-fair utility by +0.15 ± 0.02, and 256, 64, 256 beats it on the minimum-AP goodput by +7.62 ± 0.27 Mbps. A different CW per AP is therefore necessary in this topology.
- With a fairness (proportional-fair) reward, independent per-AP agents beat BEB and Global-CW OSCAR on proportional-fair utility and on the weakest AP (p = 0.008, all 8 seeds), at lower aggregate throughput. Against the static optimum for the same seeds, independent PF agents stay below it (-0.03 ± 0.01 in proportional-fair utility and -3.3 Mbps in minimum-AP goodput).

### 5.3 Sensing heuristics (v3.3.0)
IdleSense, with its published rule, gave the highest aggregate throughput in the chain (78.12 Mbps, n = 8) but the worst fairness (proportional-fair utility 6.68, -0.80 against BEB; the middle AP got 0.53 Mbps). In the two-AP S2-like topology (20 and 40 stations) it matched Global-CW OSCAR (38.77 ± 0.21 against 38.65 ± 0.40 Mbps, paired difference +0.11 ± 0.25) and beat BEB by 40 %, without learning. Residual RL on top of IdleSense was unstable over three training seeds.

### 5.4 BEB with RTS/CTS
RTS/CTS is the standard answer to hidden nodes. In the v3.7.0 baselines (S2, S4 and S5a; 10 seeds; 30 s) BEB with RTS/CTS was worse than plain BEB in every cell and at every alpha (for example in S2 a gap-closed value of -0.76 at alpha 0 and -1.04 at alpha 1, where 0 is BEB). The extra RTS/CTS overhead outweighs the collision savings in this PHY with constant-rate UDP. Part I repeats this comparison on the report's hidden-node topologies.

### 5.5 Baselines added in v3.7.0 and v4.0.0
Table: gap-closed (GC) at alpha 1, 10 evaluation seeds, 30 s (v3.7.0); GC is the share of the distance from BEB to the best static optimum; negative means worse than BEB
| Cell | Global-CW | IdleSense | KW | UCB per AP | BEB + RTS/CTS | CCOD (global form) |
|---|---|---|---|---|---|---|
| S2 | 0.966 | 0.914 | 0.902 | -0.372 | -1.040 | 0.689 |
| S4 | 0.325 | -0.092 | 0.919 (infeasible) | 0.663 | -1.007 | 0.537 |
| S5a (loads 150,150,1) | 0.939 | -0.100 | 0.721 | -0.174 | -3.980 | 0.989 |
In v4.0.0 the DAC controller (Patras et al.) was the strongest new rival, the re-built drlCW was weak in the project's PHY (feasible in only some cells and below the other rivals), and BLADE was added later (section 6).
