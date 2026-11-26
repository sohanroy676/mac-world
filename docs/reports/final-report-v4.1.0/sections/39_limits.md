## 9. Limitations and threats to validity

- **Simulation only.** ns-3.29's early 802.11ax model, one 20 MHz channel, constant-rate UDP uplink, no mobility, no OBSS-PD. Rankings might change with TCP, aggregation or real traffic.
- **Exact CW writes.** The simulator lets the AP write an exact CW to its stations every 10 ms. A real AP can only signal CW through beacons. Gate C tests a 100 ms, 2^k-1 update and shows a large loss (worst-cell share 0.41). Whether it is the period or a missing tuning that causes the loss was not separated.
- **Central versus isolated controllers.** `kwdirect` and `coord` see all APs' goodput; per-AP OSCAR agents see only their own BSS. Comparisons between them are not like for like. KW and the central critic are central by design as well.
- **Targets.** The confirmed worst-cell share of 0.85 misses the 0.95 target set in advance (S4 at alpha 1).
- **Ceilings are lower bounds.** The static search was cut by a third and F2 is a grid, so true optima may be higher. A share above 1 means above the lower-bound ceiling.
- **Seeds and tuning.** Learner training seeds were chosen on seeds 0 to 2; tournament and confirmation seeds are out of sample. Rival knobs were tuned once on seeds 0 to 3 and `kwdirect` has per-alpha settings, which gives it a slight advantage.
- **Determinism.** Learner runs hash differently on Intel and AMD CPUs; learned results are compared by their statistics, not bit-identity. Non-learned runs were identical across machines.
- **Early studies.** v1.1 to v1.9 agent results used a start with CW 0 and are not used for conclusions; the v2 studies have only three seeds and wide intervals.
- **New mentor-scenario cells.** They have no validated static optimum (a ceiling search needs thousands of runs per cell), so they are reported with BEB as the reference and absolute goodput, fairness, collisions and delay, not as a share of a ceiling. Learner training in the new cells uses three training seeds and no selection; the results of all three seeds are averaged.
- **Infrastructure.** GitHub cancelled three Actions runs in the confirmation wave and, in the report evaluation, run rs2b after 1,272 of its 1,289 jobs (no reason was given). The lost jobs were rerun (rs2c) and every result is complete.
- **Novelty.** The comparison with the related work (Gawłowicz et al. and others) was not checked line by line.
