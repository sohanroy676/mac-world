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

## 4c. Batch 3 (20,40) — PARTIAL (2026-10-14; 5 of 9 runs)
Data: `docs/figures/v1.1.0-b3/` (tables, 4 figures inspected, manifest). Run times 16-21 min each for global/independent/beb s1; beb s0 took 2500 s (slower, other load that day). Done: beb s0 s1, global s0 s1, independent s0. NOT run: independent s1, beb/global/independent s2. Stopped by user time budget, not by failure; all 5 runs `--check` PASS.

| Mode (policy window, Mbps) | n | Aggregate | AP1 | AP2 | Jain | CW last-100 AP1/AP2 |
|---|---|---|---|---|---|---|
| BEB | 2 | 27.16 ± 1.05 | 9.01 | 18.15 | 0.898 | 16 / 16 |
| Global-CW OSCAR | 2 | 36.66 ± 34.66 | 11.68 | 24.98 | 0.885 | ~260 / ~260 |
| Independent per-AP | 1 | 32.41 (n=1) | 13.23 | 19.18 | 0.967 | 108 / 136 |

Paired vs BEB (same ns-3 seed): global +9.50 ± 35.72 Mbps (+35.0 ± 132.8 %, n=2 pairs, CI far too wide to conclude); independent +5.16 Mbps (+18.9 %, n=1 pair, no CI).

- Fact: with n<=2 no 20,40 difference is statistically established. Point estimates favour both trained modes over BEB, but the global-CW seed spread is large (CI 2-71 Mbps in the figure).
- Fact (figures): global-CW CW wanders around 2^8 at both topologies; independent agents both fall to ~2^6-2^7 by step ~1500 with AP2 above AP1 at 20,40. Independent is still descending at the end of the run (not converged).
- Fact: t=1.144 s STA deassociation counts at 20,40: beb s0 = 1, beb s1 = 0, global s0 = 7, global s1 = 14, independent s0 = 6. Every event is at t=1.144 s and every deassociated STA re-associates (re-assoc count == deassoc count). At 20,20 (earlier): BEB 0, trained 4-14. So it occurs in BEB too but much more often in trained modes. Cause still unproven.
- Inference, untested: 1.144 s is a fixed simulation time (warm-up/first action boundary, when trained modes first change CW and STAs pick up a new EDCA set from beacons, §v0.5 rounding), so it is a transient at the start of policy control; BEB's single event argues for a second, policy-independent trigger. To test: log CW + beacon events around t=1.1-1.2 s in one trained and one BEB run.

## 5. Remaining for v1.1.0 and conclusion so far
Not run: 20,40 independent s1, beb/global/independent s2 (4 runs, ~16-21 min each, ~70-85 min). From `ns-3.29/scratch/linear-mesh`:
`../../venv/bin/python benchmark_v1_1_0.py --topos 20,40 --seeds 1 2 --benchDir results/bench-v1.1.0` (resumes PASS rows; ask first; one job at a time). Then re-aggregate to a NEW dir (e.g. `docs/figures/v1.1.0-b4`; never overwrite earlier ones), re-read §4c and replace its n=1/2 numbers.

Provisional conclusion across topologies (will change if 20,40 seeds change it):
- 2,3 and 5,15: all paired CIs include 0 (section 3).
- 20,20 (n=3): global-CW +26.0 ± 13.1 % over BEB, CI excludes 0; independent per-AP +0.2 ± 71.1 %, no evidence of gain, huge seed variance.
- 20,40 (n<=2): both trained modes above BEB in point estimate, no CI that supports a claim.
- So far the supported claim is only: a single global CW beats BEB at 20,20. Independent per-AP agents have not shown a reliable gain over BEB or over global-CW, and converge slowly (convergence step ~1000+).
Close and tag only with user approval.
