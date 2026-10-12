# v1.1.0 — Baseline benchmarking (IN PROGRESS, 2026-10-09)

Status: tooling done; batch 1 (2,3 and 5,15) done; batch 2 (20,20) PARTIAL (seed 0 complete, seed 1 BEB done; seed 1 global/independent and seed 2 not complete); batch 3 (20,40) NOT run. v1.1.0 is not closed and not tagged.

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
- n=3 gives wide CIs. Figures were generated but not yet inspected by eye.
- Convergence step = first step after which rolling-100 aggregate throughput stays within ±5 % of the last-300 mean; for independent runs the CI is larger than the mean (unstable).
- Run times were erratic on WSL (3-26 min per job, high sys time); one smoke job took 24 min with no cause found.
- Smoke-test runs used the pre-fix binary and were discarded.

## 4b. Batch 2 (20,20) partial results (2026-10-12, second laptop)
Batch 1 raw traces (`results/bench-v1.1.0/` from the first laptop) are gitignored and were NOT available here (decision: skip them). Batch 2 was run into a fresh `results/bench-v1.1.0/` on the second laptop (2 cores, 5 GB RAM) with the rebuilt binary (regressions: `--nWifi=5` dry seed 1 -> 10533, `5,15` dry seed 1 -> 9000, seed 2 -> 9023). Outputs are kept separate from batch 1: `docs/figures/v1.1.0-b2/` (manifest, tables, 4 figures; figures not yet inspected by eye).
Completed PASS runs (manifest): seed 0 beb/global/independent (1176/1158/1130 s) and seed 1 beb (1133 s). Seed 1 global was in flight when this was written; seed 1 independent and all of seed 2 were not run.

| Mode (policy window, Mbps) | n | Aggregate | AP1 | AP2 |
|---|---|---|---|---|
| BEB | 2 | 30.06 ± 0.36 | 14.63 | 15.43 |
| Global-CW | 1 | 38.20 | 17.91 | 20.29 |
| Independent | 1 | 30.41 | 16.18 | 14.23 |

- Fact: on seed 0, global-CW is +27.0 % over BEB (8.11 Mbps); independent is +1.1 %. n=1 per trained mode, so no CI and no claim.
- Note: 20,20 BEB here (30.1 Mbps, policy window) is not comparable to the v1.0.0 whole-run 32.2 Mbps (window mismatch, see §3 of core-v1.0.0).
- Run times ~19 min each on this laptop (batch 1 laptop: 8-32 min at 2 APs).

## 5. Remaining for v1.1.0
Finish batch 2 (20,20: seed 1 global + independent, seed 2 x3 = 5 runs) and batch 3 (20,40: 9 runs) (ask before each); aggregate all four topologies; look at figures; finish this doc; check the 20,40 BEB logs for the deassociation (cause still unproven); then close and tag only with user approval.
Command: `../../venv/bin/python benchmark_v1_1_0.py --topos 20,20 --seeds 0 1 2 --benchDir results/bench-v1.1.0` (same bench dir: resumes). Then `aggregate_bench.py results/bench-v1.1.0 --out ../../../docs/figures/v1.1.0`.
