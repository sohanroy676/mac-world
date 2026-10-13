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

## 4c. Batch 3 (20,40) — PARTIAL (2026-10-13; 1 of 9 runs)
Data: `docs/figures/v1.1.0-b3-partial/` (no aggregate/figures yet). Runs take ~42 min each here (60 STAs; about 2x the 20,20 time), so the full batch is ~6 h. A terminal restart killed the job during `global` seed 0; only `beb` seed 0 reached the manifest.

| Run | Policy-window Mbps | AP1 | AP2 | Jain | CW |
|---|---|---|---|---|---|
| 20,40 BEB seed 0 (n=1) | 27.25 | 8.85 | 18.39 | 0.891 | 16 |

- Fact: `--check` PASS, 1500 steps, 2500 s.
- Fact: the t=1.144 s deassociation also occurs in BEB at 20,40 (1 event, STA nodeId=42 off AP2). Together with 20,20 (0 events in BEB, 4-14 in global/independent seeds 0-1), it is therefore not exclusive to trained modes. Cause still unproven; it happens at an identical time in every run, so a fixed simulation event (not a policy effect) is the more likely explanation. Inference, untested.
- Remaining: beb s1 s2; global s0 s1 s2; independent s0 s1 s2, then aggregate, figures, conclusion.

## 5. Remaining for v1.1.0
Batch 3 (20,40; 8 of 9 runs left (beb s0 done); ask before starting; ~42 min each here, ~5.5 h) from `ns-3.29/scratch/linear-mesh`:
`../../venv/bin/python benchmark_v1_1_0.py --topos 20,40 --seeds 0 1 2 --benchDir results/bench-v1.1.0` (same bench dir: resumes PASS rows). Then aggregate with `aggregate_bench.py results/bench-v1.1.0 --out ../../../docs/figures/v1.1.0-b3` (new dir; never overwrite `v1.1.0` or `v1.1.0-b2`), look at the figures, check the 20,40 BEB logs for the t=1.144 s STA deassociation (cause unproven; BEB not yet checked), add a §4c, and write a conclusion. Close and tag only with user approval.
