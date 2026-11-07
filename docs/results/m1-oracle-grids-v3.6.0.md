# M1 (v3.6.0): oracle grids, convergence check, gates, first GC table

Status 2026-11-02 23:15 IST: A1 (12 jobs), A2 (210 jobs) and A3 (96 jobs, resumed after the 06:45 STOP) all PASS `--check`. Selection seeds = python 0-2, eval seeds 100-102. Load 10 Mbps/STA + `--rewardNorm 150` except S5a (`150,150,1`). Floor slack 5 % (plan rev 6). Job lists, manifests, logs: `docs/figures/v3.6.0-grids/` (run dirs local, not committed). Code: `m1_jobs_v3_6_0.py`, `m1_analysis_v3_6_0.py`; `--extraTraces` now adds an `idle` trace column and prints per-AP `DELAY` lines in gym runs (the trainer's stop request exited ns-3 before the end-of-main summary, so M0's DELAY lines only worked in dry runs).

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

## First GC table, S2 and S5a (eval seeds 100-102, n=3, 5 % slack; `gc_table_s2.md`, `gc_table_s5a.md`)
| Cell | Method | GC a0 | GC a1 | GC a2 | Floor |
|---|---|---|---|---|---|
| S2 | Global | 0.97 ± 0.06 | 0.97 ± 0.06 | 0.98 ± 0.06 | ok |
| S2 | IdleSense | 0.93 ± 0.05 | 0.94 ± 0.06 | 0.95 ± 0.06 | ok |
| S2 | OSCAR per AP | -0.42 | -0.75 | -1.29 | infeasible |
| S2 | PF learner t0 / t1 / t2 | 0.96 / 0.96 / 0.84 | 0.54 / 0.81 / 0.60 | 0.24 / 0.71 / 0.43 | infeasible / ok / ok |
| S5a | Global | 0.93 ± 0.08 | 0.94 ± 0.09 | 0.86 ± 0.12 | ok |
| S5a | IdleSense | 0.47 | -0.09 | -0.45 | infeasible |
| S5a | OSCAR per AP | -3.08 | -3.07 | -3.16 | infeasible |
| S5a | PF learner t0 / t1 / t2 | 0.94 / 0.89 / 0.75 | 1.05 / 1.08 / 0.90 | 1.00 / 1.06 / 0.90 | ok |
Fact: in the one-domain S2 cell IdleSense and Global are both near the ceiling (0.93-0.98) and the PF learner is below them at alpha >= 1; in S5a Global is also near the oracle (0.86-0.94), IdleSense is infeasible (AP3 9.45 vs floor 10), and the PF learner matches the oracle. So on these three cells only IdleSense (S4, S5a) and OSCAR per AP (everywhere) fail the floor; Global fails to separate from the oracle only in S4 at alpha >= 1. Limits: n=3, one Global/OSCAR training seed, PF learner 3 training seeds shown separately, no multiplicity correction, learner CIs are eval-seed variance only.

## Problem found: S7 load design
80 % of BEB aggregate per STA (S4 1.93, S2 0.37 Mbps) is infeasible for the middle AP in S4: it demands 19.3 Mbps, no static delivers more than 0.99 of it on all APs (best 64,64,64 at 0.97), and its p99 is about 500 ms for every setting. The plan's oracle rule (lowest p99 at >= 99 % delivered) has no S4 answer. S2 works: oracle 256,256 (p99 19.5 ms) vs BEB 27.3. Proposed fix (not run): per-AP loads with the middle AP at about 1 Mbps/STA via `--apLoads`. Decision needed.

## Not done / next
GC table at eval seeds 100-107 (only 100-102 run); S8p3 lower edge CW grid. S7-S4 redesign. G0a/G0b definitions need your sign-off.

## Update v3.6.1 (2026-11-03): leftovers
Decisions (user, 2026-11-02): G0a, G0b and the IdleSense "settled" criterion approved as defined above. S7-S4 redone with `--apLoads 1.93,1.0,1.93` (tag `s7-s4b`; the old uniform-load runs stay as `s7-s4`). Jobs and analysis: `docs/figures/v3.6.1-leftovers/` (`a4gate_jobs.json`, `a4_jobs.json`, `a4_analysis.md`); 51 + 4 jobs PASS.
- **S7-S4b (fact):** every setting delivers its offered load except 16,16,16. Oracle by the plan rule (lowest worst-AP p99 at >= 99 % delivered): 128,64,128 at 9.3 ms, tied with 64,64,64 (9.3 ms); BEB 10.7 ms (ln gap 0.141). The worst-AP metric is set by the middle AP (about 9-10 ms in all settings); edge-AP p99 differs more (64,64,64: 5.0/4.8 ms vs BEB 7.8). Inference: the cell separates methods weakly; the oracle choice between 128,64,128 and 64,64,64 is within noise.
- **S8 phase 3 lower edges (fact):** alpha 0 oracle is now 32,64,32 (U gap 1.09, BEB SD 0.28, no longer degenerate; 16,128,16 is worse, so 32 is interior). Alpha 1 stays 64,64,64 and alpha 2 stays 64,32,64; edge 32 and 16 did not beat them. Not run: middle CW 16 with edge 64.
- **Rule violation found (fact):** the first GC tables (seeds 100-102) ran every cell at simTime 15, including IdleSense, which settles at 13-15 s. Plan rule: cells with IdleSense run 30 s for all methods. Re-evaluation of S2/S4/S5a at 30 s and seeds 100-109 is batch `a5` (270 jobs, learners reload the saved actors, trained at 15 s); it supersedes the 15 s tables.

## GC tables at 30 s, eval seeds 100-109 (v3.6.1, batch `a5`, 270 jobs PASS, 2026-11-04)
Plan rule applied: all methods in the three cells run 30 s (the 15 s tables above are superseded). Learners reload the actors trained at 15 s (2 episodes, 1 seed Global/OSCAR, 3 PF seeds shown separately); statics are the selection-seed oracles. n=10, 95 % CI, 5 % floor slack. Full tables: `docs/figures/v3.6.1-leftovers/gc30_table_{s4,s2,s5a}.md`.
| Cell | Method | GC a0 | GC a1 | GC a2 | Floor |
|---|---|---|---|---|---|
| S2 | Global | 0.98 ± 0.03 | 0.97 ± 0.04 | 0.96 ± 0.04 | ok |
| S2 | IdleSense | 0.92 ± 0.06 | 0.91 ± 0.06 | 0.91 ± 0.05 | ok |
| S2 | OSCAR per AP | -0.40 | -0.78 | -1.38 | infeasible |
| S2 | PF learner t0 / t1 / t2 | 0.95 / 0.97 / 0.86 | 0.43 / 0.74 / 0.53 | 0.04 / 0.60 / 0.30 | infeasible / ok / infeasible |
| S4 | Global | 0.64 ± 0.14 | 0.33 ± 0.07 | raw U -61.3 | ok |
| S4 | IdleSense | 0.16 ± 0.12 | -0.09 ± 0.03 | raw U -116.8 | infeasible |
| S4 | OSCAR per AP | 1.14 | -0.55 | raw U -260.4 | infeasible |
| S4 | PF learner t0 / t1 / t2 | -2.30 / -4.43 / -2.22 | 0.95 / 0.76 / 0.95 | raw U -20.3 / -20.0 / -19.1 | ok / infeasible / ok |
| S5a | Global | 0.94 ± 0.01 | 0.94 ± 0.01 | 0.88 ± 0.02 | ok |
| S5a | IdleSense | 0.47 | -0.10 | -0.47 | infeasible |
| S5a | OSCAR per AP | -3.09 | -3.02 | -3.13 | infeasible |
| S5a | PF learner t0 / t1 / t2 | 0.94 / 0.89 / 0.75 | 1.04 / 1.07 / 0.90 | 1.01 / 1.08 / 0.91 | ok |
Facts: (1) the 15 s conclusions hold at 30 s: IdleSense is infeasible in S4 and S5a, OSCAR per AP is infeasible in every cell, Global is near the ceiling in S2 and S5a and 0.33 in S4 at alpha 1, the PF learner reaches 0.95 in S4 at alpha 1 for 2 of 3 seeds. (2) S4 alpha 2 is now a degenerate cell by the plan rule (U gap 84.5 vs BEB SD 81.8; the middle AP's goodput sits near the 0.01 Mbps floor in some seeds), so it is reported as raw U: static 256,128,256 -16.2, PF learners -19 to -20, Global -61, BEB -101. (3) PF learner GC is below 0 at S4 alpha 0 (-2.2 to -4.4): it was trained for fairness and gives up aggregate. Caveats: PF-learner CIs are eval-seed variance only; Global/OSCAR have one training seed; GC > 1 for learners in S5a is within the oracle's noise (static CI about ±0.03); no multiplicity correction.
