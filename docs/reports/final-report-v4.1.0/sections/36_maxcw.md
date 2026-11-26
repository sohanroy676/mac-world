## 6. The max-CW study (v4.1.0)

### 6.1 Question and plan
How close can an **online** CW controller get to the best **static** CW of each scenario, and does it beat BEB, the rule-based rivals and the learned (OSCAR-family) controllers? The study covers S2, S4 and S5a at alpha 0, 1 and 4 (9 cell and alpha pairs). The evaluation protocol was fixed in advance: tuning seeds 0 to 3, ceiling validation seeds 200 to 209, tournament seeds 300 to 309 and confirmation seeds 103 to 122; the target for the primary criterion (the worst-cell share of the best online method) was 0.95, a hypothesis set before the runs.

### 6.2 Measurement modes and the pipeline
- The simulator gained a wide CW range (4 to 32767), exact-CW writes, a CW hold mode for static runs, two-phase CW schedules, and measured PHY durations (Ts 226 us, Tc 242 us). Old BEB and static traces stayed byte-identical (design note `docs/design/measurement-modes-v4.1.0.md`, ADR-0008).
- All runs are jobs in a pinned container image on GitHub Actions; each result carries the SHA-256 of its trace. Across machines the non-learned runs gave 0 hash mismatches; learned runs hashed differently on Intel and AMD CPUs, so learners are compared by their statistics, not by trace identity.

### 6.3 Ceilings
The ceiling of a cell is the best floor-feasible validated point of three families: F1 (exact static CW per AP), F2 (static CWmin) and F3 (a two-phase schedule that mutes an AP part of the time, S4 only). The search ran 4,723 runs (Halton points and Gaussian-process proposals), and the best three points per cell and family were re-run on fresh seeds 200 to 209 (480 runs).

Table: validated ceilings (utility U, higher is better; the CW point is per AP)
{{include:generated/maxcw_ceilings_table.md}}

At alpha 1 and 4 the validated gap above BEB is large in every cell (for example in S2 at alpha 1 from -46.5 to -24.8). At alpha 0 (total throughput) it is small in S4 (+5 %) and almost zero in the last phase of S8 (77.4 to 77.6). A schedule beats the best static family at alpha 1 in S4 (+1.34 utility, 18 seed standard deviations): a CW-only schedule helps the middle AP of the hidden chain.

### 6.4 Online controllers and tuning
A cascade of DAC with a KW search, a floor-guarded coordinator and `kwdirect` were tuned in a series of waves on seeds 0 to 3 (results in `docs/results/wave2*-v4.1.0.md`). The floor guard (a penalty when an AP falls under its BEB floor) removed the infeasible results of the first grid; a longer probe window (0.6 s) fixed the throughput cells (alpha 0); a change detector was tried for the dynamic cell S8 and brought no measurable gain at the shift size used. The tournament and confirmation use `kwdirect`, with `coord` only for S4 at alpha 1.

### 6.5 Tournament on seeds 300 to 309
430 runs of 60 s (BEB, static F1 and F2, DAC, BLADE, IdleSense, KW, contextual UCB, kwdirect, coord) plus frozen learners evaluated on the same seeds (Global, PF and RAFA, best training seed per cell). Share of the ceiling, 10 seeds:

![Share of the validated ceiling of every method in every cell (tournament seeds 300-309). Blue is near the ceiling, orange is below BEB.](figures/maxcw_tournament_heatmap.png){w=500}

Table: worst-cell view of the tournament (share of the ceiling)
{{include:generated/maxcw_tournament_table.md}}

- `kwdirect` has the best worst-cell share of every method that covers all nine cells: 0.90 (S4 at alpha 1); every other cell is 0.94 to 1.04.
- No other family is close in its weakest cell: BLADE -0.53, DAC -0.14, IdleSense -0.34, KW -0.72, contextual UCB -3.76, Global 0.60, PF -2.11, RAFA -1.91 to -2.07. The learners are strong in some cells (PF 1.09 in S5a at alpha 1) and collapse in others (PF and RAFA at S4 alpha 0), so none of them is a single recipe across scenarios.
- DAC is the strongest published rival in S2 (0.87 to 0.89) and BLADE is functional but weaker (0.72 to 0.80 in S2).

### 6.6 Confirmation on seeds 103 to 122 (760 runs, 300 s)
![Confirmation: mean share of the ceiling with 95 % confidence intervals for kwdirect, the static F1 reference, DAC and the two best learners.](figures/maxcw_confirmation_share.png){w=500}

Table: share of the validated ceiling, mean (sd) with feasible seeds out of 20 (confirmation, seeds 103-122)
{{include:generated/maxcw_confirmation_table.md}}

- **Target not met.** `kwdirect` has a worst-cell share of 0.85 (S4 at alpha 1); the other eight cells are 0.93 to 1.02, and all 20 seeds are feasible in every cell. It is better than BEB in all nine pairs.
- **Against the static optimum (F1).** Not shown non-inferior (intersection-union p = 0.83): kwdirect is worse in seven cells by at most 0.065 and better in two. F1 is a tuned static reference, not an online method.
- **Against DAC.** Better (p < 0.001). DAC is infeasible in every S4 and S5a cell.
- **Against learners** (each only on the cells it was tuned for). PF and RAFA fail at S4 alpha 0 (about -1.9). Global-CW ties kwdirect in S2 (0.97 to 0.98). PF is slightly ahead in S5a at alpha 1 and 4 (no test run). In S4 at alpha 1, PF (0.92) and RAFA (0.94) beat kwdirect (0.85), the cell where the F3 schedule beats the best static point.

### 6.7 Gate C: update every 100 ms, rounded to 2^k-1
A real AP announces CW values in beacons (about every 100 ms) and stations read them as 2^k-1. Gate C applies the controller's CW every 100 ms, rounded to 2^k-1, without modelling the beacon delay.

![Cost of the beacon-style update: change in share of kwdirect-gatec relative to exact kwdirect, with 95 % confidence intervals.](figures/maxcw_gatec_cost.png){w=430}

- The worst-cell share falls to 0.41. S2 loses 0.50 to 0.56, and 9 to 13 of 20 seeds are feasible; S4 loses 0.09 to 0.28; S5a loses 0.01 to 0.19.
- It is not known whether this is caused by the 100 ms period itself or by a controller that is not tuned for slow updates; the study did not separate the two.
