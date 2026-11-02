# M1 (v3.6.0): oracle grids, convergence check, gates, first GC table (partial)

Status 2026-11-02 07:00 IST: A1 (BEB selection runs, 12 jobs), A2 (grids, 210 jobs) all PASS. A3 (GC table, 96 jobs) stopped at 48 PASS by the 06:45 STOP file; S4 complete, S2 partial (Global 2 of 3 seeds, no OSCAR/PF learner), S5a not run. Selection seeds = python 0-2, eval seeds 100-102. Load 10 Mbps/STA + `--rewardNorm 150` except S5a (`150,150,1`). Floor slack 5 % (plan rev 6). Job lists, manifests, logs: `docs/figures/v3.6.0-grids/` (run dirs local, not committed). Code: `m1_jobs_v3_6_0.py`, `m1_analysis_v3_6_0.py`; `--extraTraces` now adds an `idle` trace column and prints per-AP `DELAY` lines in gym runs (the trainer's stop request exited ns-3 before the end-of-main summary, so M0's DELAY lines only worked in dry runs).

## Oracles (static, selection seeds; full tables `m1_selection_analysis.md`)
| Cell | alpha 0 | alpha 1 | alpha 2 |
|---|---|---|---|
| S4 | 64,64,64 (GC gap 4.1 Mbps) | 128,64,128 | 256,128,256 |
| S5a | 128,128,128 | 128,128,128 | 128,64,128 |
| S8 phase 3 | degenerate (BEB beats all statics) | 64,64,64 | 64,32,64 |
| S2 | 512,512 | 512,512 | 512,512 |
Caveat (fact): S8p3 oracles sit at the edge-CW lower bound of the grid (64); smaller edge CWs were not run. STAs read CW as 2^k-1, so only powers of two were gridded.

## Gates
- G0a PASS (my definition: both APs' idle slots within 10 %, seed SD < 10 %): BEB 2.86/2.86, 512,512 4.45/4.45. Trivially true in one domain.
- G0b PASS on idle slots, FAIL on retry rate for BEB and IdleSense (my definition: |edge - middle| > 3 pooled seed SD). S4 BEB idle edge 2.62 vs middle 0.78; at 256,128,256 7.81 vs 3.10. Idle separates the roles; retry does not at BEB.

## IdleSense convergence (published rule, 15 s)
Not settled by the 3 s window: CW stays outside a factor 2 of its last-third median until step 1346-1498 (13-15 s) in every S2 and S4 run. By the plan rule, cells with IdleSense run 30 s. The criterion is mine (strict). S4 middle AP ends at CW 1024.

## First GC table, S4 (eval seeds 100-102, n=3, 5 % slack; `gc_table_s4.md`)
| Method | GC a0 | GC a1 | GC a2 | Floor |
|---|---|---|---|---|
| BEB | 0 | 0 | 0 | ok |
| Global (1 train seed) | 0.70 ± 0.81 | 0.30 ± 0.21 | 0.36 ± 0.27 | ok |
| IdleSense | 0.27 | -0.09 | -0.22 | infeasible |
| OSCAR per AP | 1.01 | -0.71 | -2.69 | infeasible |
| PF learner t0 / t1 / t2 | -2.05 / -3.86 / -1.92 | 1.02 / 0.80 / 1.00 | 0.99 / 0.97 / 0.99 | ok / infeasible / ok |
Fact: Global and IdleSense each fail on S4 alpha >= 1 (Global GC 0.3, IdleSense infeasible); the PF learner reaches the oracle at alpha 1 and 2 in 2 of 3 training seeds and is far below BEB at alpha 0. S2 (partial, `gc_table_s2.md`): IdleSense GC 0.93-0.95, Global 0.98 (n=2), static 512,512 = 1 by definition. Limits: n=3, one Global/OSCAR training seed, learner CIs include only eval-seed variance.

## Problem found: S7 load design
80 % of BEB aggregate per STA (S4 1.93, S2 0.37 Mbps) is infeasible for the middle AP in S4: it demands 19.3 Mbps, no static delivers more than 0.99 of it on all APs (best 64,64,64 at 0.97), and its p99 is about 500 ms for every setting. The plan's oracle rule (lowest p99 at >= 99 % delivered) has no S4 answer. S2 works: oracle 256,256 (p99 19.5 ms) vs BEB 27.3. Proposed fix (not run): per-AP loads with the middle AP at about 1 Mbps/STA via `--apLoads`. Decision needed.

## Not done / next
GC table: S2 remaining jobs, S5a, OSCAR/PF learner on S2; more PF training seeds are in `a3_jobs.json` (re-run the driver with the same manifest dir to resume). S8p3 lower edge CW grid. S7-S4 redesign. G0a/G0b definitions need your sign-off.
