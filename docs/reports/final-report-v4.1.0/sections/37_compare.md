## 7. BEB, OSCAR and the other CW optimizers in one comparison

### 7.1 What "OSCAR" means in this comparison
OSCAR was designed for one AP. In a network of several APs it has three natural readings, and the project measured all three:
- **Global-CW OSCAR:** one agent observes the network loss and broadcasts one CW to every AP (`global` mode, and the CCOD global form). It uses global information, so it is not an isolated-AP method.
- **Independent per-AP OSCAR:** one agent per AP with local observation and reward (`independent` mode), the direct multi-AP extension of the original design.
- **Extensions of OSCAR:** the PF learner (independent agents with a proportional-fair reward) and RAFA (one shared actor with richer own-radio inputs and a fair-floor penalty).

### 7.2 Share of the validated ceiling at alpha 1 (tournament, seeds 300 to 309)
Share = 0 is BEB and share = 1 is the best validated static point; an infeasible seed counts as 0 and a share below 0 is worse than BEB. The last column is the worst of all nine cell and alpha pairs (alpha 0, 1 and 4).

Table: alpha-1 share of the ceiling and worst cell (Wave 3a tournament)
{{include:generated/compare_alpha1.md}}

{{include:generated/compare_oscar_perap.md}}

### 7.3 Findings
1. **OSCAR with one shared CW beats BEB, and it reaches most of what a fixed CW can give.** In S2 the Global-CW learner reaches 0.89 of the ceiling (0.97 in the earlier 10-seed 30 s evaluation), and +30 % aggregate over BEB in the early saturated studies. It is much weaker in the hidden chain (S4: 0.60 at alpha 1) because one common CW cannot give the middle BSS a different access probability.
2. **Independent per-AP OSCAR, as designed, does not work in a shared channel.** Aggregate throughput equals BEB at 2 APs and falls to -46 % at 10 APs; against the validated ceilings it is floor-infeasible in S2, S4 and S5a. With a fairness reward and richer training (PF) it becomes the best learner in two cells (S4 and S5a at alpha 1), but it collapses in S4 at alpha 0.
3. **Rule-based controllers are strong only where one common CW is nearly optimal.** DAC and IdleSense reach 0.84 to 0.88 in S2 but are at or below BEB in the hidden chain and the unequal-load cell. This repeats the IdleSense result of v3.3.0 (highest aggregate, worst fairness).
4. **A central online search is the most robust single method.** `kwdirect` is at 0.90 or above in every cell of the tournament and 0.85 or above in the confirmation, the best worst-cell of all online methods. The price is that it needs the goodput of every AP. In S4 at alpha 1 the learned PF and RAFA controllers and the static F1 point are ahead of it.
5. **Learned controllers are specialists.** Each learner works on the cells it was trained and tuned for and fails elsewhere; none is a single recipe. RAFA was designed to be one recipe and failed its pooled-training gate (G3).
6. **Realistic update timing costs a lot.** Updating only every 100 ms and rounding to 2^k-1 removes about half of the share (worst cell 0.41).

{{include:generated/compare_new.md}}
