# v1.1.0 — Baseline benchmarking (IN PROGRESS, 2026-10-09)

Status: tooling done; batch 1 (2,3 and 5,15) done; batch 2 (20,20) DONE (3 modes x 3 seeds, 9/9 PASS); batch 3 (20,40) PARTIAL (1/9 run: beb seed 0). v1.1.0 is not closed and not tagged.

## 1. Method
Three systems on the same topology, traffic, PHY, duration (15 s, step 0.01 s) and seeds (python seed 0,1,2 -> ns-3 seed 1,2,3):
- **BEB**: standard 802.11 (`OSCAR_multi_ap_train.py --mode beb` = ns-3 `--dryRun` driven through the same stepping loop, CW 16..1024).
- **Global-CW OSCAR**: `--mode global`, ONE DDPG agent, one CW broadcast to every AP. State = network loss (sum tx - sum rx)/sum tx; reward = network goodput / (150 Mbps x all STAs x step), clamped to [0,1].
- **Independent per-AP**: `--mode independent` (the v1.0.0 system, trace byte-identical to before this change).

All modes are measured identically from `trace.csv` (per-step rx), over the same policy window (steps >= 300). This removes the v1.0.0 window mismatch (core-v1.0.0 §3). Statistics: mean ± 95% CI (Student t) over seeds; paired difference vs BEB per seed. Reward is not compared across modes.
Tools: `benchmark_v1_1_0.py` (runner, resumable), `aggregate_bench.py` (tables + figures). Run manifest: `docs/figures/v1.1.0/manifest.csv`.

## 2. Seed bug found and fixed (fact)
`--seed` and `--rng` had NO effect on the simulation: dry runs of 2,3 gave identical packet counts for seeds 1, 2, 3 and rng 1, 2, 3, and BEB gym traces for seeds 0 and 1 were byte-identical. In `cw.cc` `RngSeedManager::SetSeed/SetRun` ran after nodes, devices and MACs were created. Inference (not separately tested): their random streams had already read the default seed.
Fix (`cw.cc`, project code, commit 0e71414): seed before `set_phy`. After the fix seeds 2, 3 and rng 2 give different runs; seed 1 / rng 1 is unchanged (2,3: 10830/4729 and 14195/5998). Regressions on the rebuilt binary: `--nWifi=5` dry seed 1 -> 10533 pkts, `5,15` dry -> 9000 pkts, gym smoke 10.59458.
Consequence: the v1.0.0 "ns-3 seed" pinning never varied the simulation; seed-0 results there equal today's ns-3 seed 1 runs (same default seed), other seeds are new.

## 3. Batch 1 results (n = 3 seeds; policy window; Mbps)
| Topology | BEB | Global-CW | Independent |
|---|---|---|---|
| 2,3 | 40.47 ± 0.09 | 40.41 ± 0.69 | 39.98 ± 0.90 |
| 5,15 | 34.48 ± 0.48 | 37.95 ± 5.51 | 33.57 ± 12.92 |

Paired difference vs BEB: 2,3 global -0.1 ± 1.6 %, independent -1.2 ± 2.1 %; 5,15 global +10.1 ± 17.4 %, independent -2.6 ± 38.3 %. All intervals include zero. Full tables (per-AP, loss, Jain, CW, convergence): `docs/figures/v1.1.0/tables.md`; plots in the same directory.

- Fact: BEB measured in the same per-step window is 40.47 (2,3) and 34.48 (5,15) Mbps; the v1.0.0 whole-run numbers were 43.47 and 36.79. The v1.0.0 "trained below BEB on 2,3" was mostly the window mismatch.
- Fact: with n=3 no system is distinguishable from BEB in aggregate throughput on either topology.
- Fact: independent per-AP results vary strongly between seeds on 5,15 (AP1 18.9 ± 29.6, AP2 14.6 ± 16.7 Mbps).
- Inference (untested): CW tuning helps more under uneven load; the 5,15 evidence is too weak to claim it.

## 4. Caveats
- n=3 gives wide CIs. Batch 1 and batch 2 figures were inspected; batch 3 pending.
- Convergence step = first step after which rolling-100 aggregate throughput stays within ±5 % of the last-300 mean; for independent runs the CI is larger than the mean (unstable).
- Run times were erratic on WSL (3-26 min per job, high sys time); one smoke job took 24 min with no cause found.
- Smoke-test runs used the pre-fix binary and were discarded.

## 4b. Batch 2 (20,20) results (2026-10-13, second laptop; n = 3 seeds)
Batch 1 raw traces (`results/bench-v1.1.0/` from the first laptop) are gitignored and were NOT available here (decision: skip). Batch 2 was run into a fresh `results/bench-v1.1.0/` on the second laptop (2 cores, 5 GB RAM) with the rebuilt binary (regressions re-verified 2026-10-13: `--nWifi=5` dry seed 1 -> 10533; `5,15` dry seed 1 -> 9000 = 2520 + 6480; per-AP stats/CW/association checks PASS). Outputs are kept separate from batch 1: `docs/figures/v1.1.0-b2/` (manifest, tables, 4 figures, all inspected). Runs took 16-20 min each.

| Mode (policy window, Mbps) | n | Aggregate | AP1 | AP2 | Jain | Δ vs BEB (paired) |
|---|---|---|---|---|---|---|
| BEB | 3 | 30.10 ± 0.20 | 14.87 ± 1.07 | 15.23 ± 0.92 | 0.999 ± 0.001 | n/a |
| Global-CW | 3 | 37.93 ± 4.17 | 23.11 ± 24.57 | 14.82 ± 21.29 | 0.877 ± 0.510 | +26.0 ± 13.1 % |
| Independent | 3 | 30.19 ± 21.60 | 16.68 ± 28.88 | 13.51 ± 7.44 | 0.870 ± 0.271 | +0.2 ± 71.1 % |

Per-seed aggregate (policy window, Mbps), seeds 0/1/2: BEB 30.08/30.03/30.18; global 38.20/36.13/39.45 (seed 2 Jain 0.64); independent 30.41/21.38/38.77.

- Fact: global-CW beats BEB on all three seeds (+6.1 to +9.3 Mbps); the paired CI excludes zero (n=3). This is the first topology where a trained system is distinguishable from BEB.
- Fact: independent per-AP is not distinguishable from BEB; its seed-to-seed spread is huge (21.4 to 38.8 Mbps). Seed 1 ends well below BEB, seed 2 well above.
- Fact (figures): global CW rises past the step-300 warm-up marker and holds ~38 Mbps from step ~500 with CW ~2^8 on both APs (one shared value). Independent starts ~35 Mbps, then the 3-seed mean decays to ~27.5 Mbps by step ~1100 while both CWs drift from ~2^8 down to ~2^6 (AP1 drops last, ~step 900).
- Fact: global-CW fairness is uneven on some seeds (seed 2 Jain 0.64: one AP is starved while the aggregate is highest); the large per-AP CIs reflect this.
- Inference (untested): the independent agents fail to coordinate (each lowers its own CW, raising contention); n=3 cannot confirm this.
- Note: 20,20 BEB here (30.1 Mbps, policy window) is not comparable to the v1.0.0 whole-run 32.2 Mbps (window mismatch, see §3 of core-v1.0.0).
- Trainer self-check bug (fixed, not a simulation bug): seed 2 global first FAILED `--check` because `cw.cc` computes `pow(2, 4 + a)` with a float `a` (4 + a is rounded to float32 before `pow`), giving CW 139 where the Python check (double) expected 140, in 2 of 3000 rows (both APs equal; readback == set value). Offline replay of all 6 trained 20,20 traces: float32 arithmetic explains exactly those 2 rows, 0 mismatches elsewhere. Only the check was changed (`OSCAR_multi_ap_train.py`); `cw.cc` and the binary are unchanged, and the re-run PASSED. The FAIL row stays in the manifest.

## 4c. Batch 3 (20,40) results (2026-10-14/15; 15/15 PASS, n = 5 seeds)
Data: `docs/figures/v1.1.0-b5/` (n=5; tables, 4 figures inspected). Seeds 3,4 added 2026-10-15 (6 runs, 864-953 s each, all PASS, one job at a time, binary unchanged). `v1.1.0-b4` (n=3) and earlier partial aggregates are superseded.

| Mode (policy window, Mbps) | n | Aggregate | AP1 | AP2 | Jain | CW last-100 AP1/AP2 |
|---|---|---|---|---|---|---|
| BEB | 5 | 27.96 ± 1.26 | 10.52 | 17.44 | 0.933 | 16 / 16 |
| Global-CW OSCAR | 5 | 36.89 ± 3.62 | 11.97 | 24.92 | 0.890 | 280 / 280 |
| Independent per-AP | 5 | 25.27 ± 8.21 | 6.96 | 18.31 | 0.814 | 160 / 108 |

Paired vs BEB (same ns-3 seed, n=5): global +8.93 ± 3.24 Mbps (+31.9 ± 11.8 %), CI excludes 0; independent -2.69 ± 8.70 Mbps (-9.3 ± 31.0 %), CI includes 0. (n=3 earlier: global +30.5 ± 32.3 %, independent +4.6 ± 33.8 %.)

- Fact: at 20,40 with n=5, global-CW beats BEB (paired +31.9 ± 11.8 %, CI excludes 0); independent is not distinguishable from BEB, and its point estimate is below BEB and below the n=3 value (seed variance, 25.27 ± 8.21).
- Fact (figures): global-CW CW wanders around 2^8 (mean-over-seeds trace drifts down to ~2^7.5 after step ~1100); independent agents fall to ~2^6.5-2^7 with AP1 above AP2 until step ~1000, then converge together. Independent aggregate throughput is NOT monotone: at 20,40 it dips to ~26.5 Mbps (below BEB) at steps 400-650, recovers to ~31, then ends ~28.5; at 20,20 it declines from ~35 to ~28 (below BEB's ~30) by step 1100-1500. The policy-window mean (30.2 / 28.6) hides that the end-of-run level is at or below BEB.
- Fact: per-AP split is BEB 9.5/17.8 (AP2 has 40 STAs and gets more). Global raises both APs; independent mainly moves AP2 up.
- Fact: t=1.144 s STA deassociation counts at 20,40 (all 9 runs; every event at t=1.144 s, every STA re-associates, re-assoc count == deassoc count):

| Mode | s0 | s1 | s2 | total |
|---|---|---|---|---|
| BEB | 1 | 0 | 0 | 1 |
| Global-CW | 7 | 14 | 4 | 25 |
| Independent | 6 | 12 | 0 | 18 |

  Seeds 3 / 4 (added 2026-10-15; same t=1.144 s, all re-associate): BEB 0 / 0, global 1 / 7, independent 9 / 9. n=5 totals at 20,40: BEB 1, global 33, independent 36.

  At 20,20 (earlier): BEB 0, trained 4-14. So it occurs in BEB too but much more often in trained modes (runs with at least one event at 20,40: BEB 1/5, global 5/5, independent 4/5; independent s2 shows 0 even though trained). Cause still unproven.
- Inference, untested: 1.144 s is a fixed simulation time (warm-up/first action boundary, when trained modes first change CW and STAs pick up a new EDCA set from beacons, §v0.5 rounding), so it is a transient at the start of policy control; BEB's single event and independent s2's zero argue the trigger is not simply "CW changed". To test: log CW + beacon events around t=1.1-1.2 s in one trained (global s1, 14 events) and one BEB (beb s0) run.

## 5. Conclusion and remaining for v1.1.0
All 18 + 9 + 15 benchmark runs (2,3; 5,15; 20,20 at n=3; 20,40 at n=5; 3 modes) are PASS. Remaining before close: user approval and tag only.

Conclusion across topologies (n = 3 seeds; 20,40 n = 5; policy window; paired vs BEB):
- 2,3 and 5,15: all paired CIs include 0 (section 3).
- 20,20: global-CW +26.0 ± 13.1 %, CI excludes 0; independent +0.2 ± 71.1 %.
- 20,40 (n=5): global-CW +31.9 ± 11.8 % (CI excludes 0); independent -9.3 ± 31.0 % (CI includes 0).
- Supported claim: a single global CW beats BEB at 20,20 (+26 %) and at 20,40 (+32 %, n=5); at 2,3 and 5,15 no difference. Independent per-AP agents show no reliable gain over BEB or over global-CW at any topology, have very large seed variance, converge slowly (step ~1000-1300), and their throughput trends down late in the run at 20,20.
- Not tested: longer training, reward/obs changes. The unproven t=1.144 s deassociation cause remains open.
Close and tag only with user approval.
