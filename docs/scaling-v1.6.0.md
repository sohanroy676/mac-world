# v1.6.0 Scaling analysis (2 -> 10 APs)

Branch `feature/v1.6.0-scaling-analysis`. Analysis only: no ns-3 run, no build, no `cw.cc` change. Tooling `ns-3.29/scratch/linear-mesh/scaling_analysis.py`; outputs in `docs/figures/v1.6.0/` (`scaling_table.md`, `scaling_per_seed.csv`, 10 figures).

## 1. Data and method
Recomputed from the raw per-run `trace.csv` of v1.1.0..v1.5.0 (local `results/bench-v*`, gitignored), with the same `summarize()` and policy window (steps >= 300) as every per-version table. Mean ± 95 % CI (Student t) over seeds; paired deltas use the same ns-3 seed.

| N APs | Split (STAs/AP) | Total STAs | Seeds | Source |
|---|---|---|---|---|
| 2 | 20,40 | 60 | 0-4 (n=5) | `benchmark-v1.1.0.md` §4c, figures `v1.1.0-b5` |
| 4 | 5,10,15,20 | 50 | 0-2 | `scaling-v1.2.0.md`, `v1.2.0-b2` |
| 6 | 5..30 step 5 | 105 | 0-2 | `scaling-v1.3.0.md`, `v1.3.0-b2` |
| 8 | 5..40 step 5 | 180 | 0-2 | `scaling-v1.4.0.md`, `v1.4.0` |
| 10 | 4,8,..,40 | 220 | 0-2 | `scaling-v1.5.0.md`, `v1.5.0` |

Fact (verified): the script's recomputed aggregate mean and n match the committed per-version `tables.md` for all 15 N x mode cells (`CROSS-CHECK PASS`).

**Confound (fact):** total STAs is not constant and not monotone in N (60, 50, 105, 180, 220). Every "vs AP count" curve therefore mixes AP count with load. The topologies are also not the same family (N=2 and N=4 are not subsets of N=10). No result here separates the two effects. The n differs (5 vs 3), so the N=2 CI is narrower for that reason alone. Run times at N=2 come from more than one laptop (see §4).

## 2. Results
Full table with CIs: `docs/figures/v1.6.0/scaling_table.md`. Means (policy window):

| N | BEB Mbps | Global Mbps | Indep. Mbps | BEB per-STA kbps | BEB min-AP Mbps | BEB Jain | Indep. Jain | Indep. phy loss |
|---|---|---|---|---|---|---|---|---|
| 2 | 27.96 | 36.89 | 25.27 | 466 | 10.52 | 0.933 | 0.814 | 0.773 |
| 4 | 28.63 | 37.29 | 23.27 | 573 | 3.02 | 0.862 | 0.737 | 0.796 |
| 6 | 23.83 | 32.53 | 18.72 | 227 | 1.36 | 0.865 | 0.678 | 0.846 |
| 8 | 20.05 | 27.99 | 12.54 | 111 | 0.84 | 0.855 | 0.674 | 0.907 |
| 10 | 19.24 | 27.04 | 9.00 | 88 | 0.56 | 0.856 | 0.634 | 0.945 |

Paired Δ vs BEB (%, ± 95 % CI; "above" = seeds above BEB):

| N | Global | above | Independent | above |
|---|---|---|---|---|
| 2 | +31.9 ± 11.8 (excl. 0) | 5/5 | -9.3 ± 31.0 | 2/5 |
| 4 | +30.5 ± 27.2 (excl. 0) | 3/3 | -18.6 ± 47.6 | 0/3 |
| 6 | +36.4 ± 49.3 | 3/3 | -21.6 ± 81.0 | 1/3 |
| 8 | +40.1 ± 92.7 | 3/3 | -37.1 ± 96.8 | 1/3 |
| 10 | +41.0 ± 83.9 | 3/3 | -53.5 ± 27.6 (excl. 0) | 0/3 |

## 3. How performance scales
- Fact: BEB aggregate falls from 27.96-28.63 Mbps (N=2, 4) to 19.24 Mbps (N=10), with the largest step 4 -> 6 (more STAs). Per-STA throughput falls 466 -> 88 kbps (573 at N=4). Phy loss rises with N (BEB 0.739 -> 0.835).
- Fact: global-CW is above BEB at the mean at every N and at every seed (17/17 seed pairs). The paired CI excludes 0 only at N=2 and N=4; from N=6 the CI includes 0 and widens (±49, ±93, ±84 %). The mean gain (+30 to +41 %) does not shrink with N.
- Fact: independent per-AP is below BEB at the mean at every N, and its deficit grows monotonically (-9, -19, -22, -37, -54 %). Only N=10 has a CI excluding 0 (3/3 seeds below BEB). At N=6 and N=8 the CI is huge because runs are bimodal (a seed that holds, others that decay).
- Fact: fairness (Jain over per-AP throughput) is stable for BEB and global (0.85-0.87 for N>=6) and falls for independent (0.81 -> 0.63). The minimum per-AP throughput of BEB falls 10.5 -> 0.56 Mbps; the smallest APs are starved much more than the mean per-AP drop (14.0 -> 1.9 Mbps) suggests, but BEB per-AP throughput also follows STA count in these splits (BEB AP1 0.56 vs AP10 2.70 Mbps at N=10).
- Fact: independent has the highest phy loss at every N (0.77 -> 0.945) and does not converge inside 1500 steps by the aggregate-throughput criterion (convergence step 1230-1469; global 473-870; BEB ~0 because its CW is fixed). Convergence step for BEB at N=8, 10 is non-zero (214, 576) (inference: run-to-run throughput variation, since BEB has a fixed CW).
- Inference (not tested): the independent agents' deficit grows with N because each AP's loss observation is dominated by contention from more neighbors it cannot see, so its local reward is a poor signal. No experiment here isolates this (no ablation of observation, no central critic yet). Unknown: whether more seeds change the picture at N=6, 8 (bimodal).
- Inference: the global-CW gain over BEB is a robust direction (always above), but with n=3 beyond N=4 we cannot claim a size. A single shared CW is a much easier learning problem than N coupled ones.

## 4. How computational cost scales
Wall time per 1500-step run (`runtime_vs_n.png`, means over modes' seeds):

| N | STAs | BEB s | Global s | Indep. s | BEB s/STA |
|---|---|---|---|---|---|
| 2 | 60 | 1333 | 1023 | 992 | (mixed laptops) |
| 4 | 50 | 723 | 736 | 803 | 14.5 |
| 6 | 105 | 1569 | 1603 | 1982 | 14.9 |
| 8 | 180 | 2870 | 3226 | 3132 | 15.9 |
| 10 | 220 | 3495 | 3849 | 4212 | 15.9 |

- Fact: for N>=4, BEB run time is roughly 14.5-15.9 s per STA, i.e. about linear in total STAs; N=4 (50 STAs) is faster than N=2 (60 STAs). Run time tracks STAs, not AP count. N=2 timings are not comparable (the v1.1.0 batches ran on two laptops/sessions; progress notes record ~42 min vs 16-21 min for 20,40 BEB; BEB 1333 ± 867 s here).
- Fact: the trained modes add little over BEB: independent minus BEB is +80 s (N=4) to +717 s (N=10), about +11 to +20 %.
- Inference: cost is dominated by ns-3 simulating the STAs, not by DDPG updates (10 actor-critic pairs at N=10 add ~20 %).
- Fact (from per-version docs §4): trainer `--check` full size 6:19 (N=6), 11:56 (N=8), 13:41 (N=10); peak RSS 365, 367, 478 MB. The N=2/4 equivalents are in `validation-v0.9.0.md` / `scaling-v1.2.0.md`, not re-extracted here. No ZMQ stalls at any N. Memory is not a constraint; time is (about 1 h per run at 10 APs, 9 runs about 9 h).
- Fact: node budget caps the current subnet at 10 APs / 244 STAs (`cw.cc:822`, 230 of 254 addresses used at N=10).

## 5. Association / deassociation vs N (limitation)
Mean deassociation events per run (from logs; every one re-associated in all per-version checks): BEB 0.2, 0.0, 1.7, 2.7, 6.0; global 6.6, 10.3, 1.7, 7.3, 16.7; independent 7.2, 10.7, 1.7, 7.3, 21.3 (N=2..10; CIs are wider than the means, see `scaling_table.md`, `deassoc_vs_n.png`).
- Fact: events appear in BEB too (so not trained-mode-only), are larger on average in trained modes at N=2, 4, 10, and grow with N for all modes in the mean. Not monotone (N=6 is lowest).
- Fact: the full-size 10-AP dry run fails the end-of-run association check (`scaling-v1.5.0.md` §3); the long runs' end-of-run association state was never recorded.
- Unknown: the cause. Deferred by decision (user, 2026-10-16) to a later robustness item (v2.x). Throughput numbers for large N should be read with this caveat: some STAs may be unassociated for part of the run, in every mode.

## 6. Summary
1. Aggregate throughput of every policy falls as N (and total STAs) grows; per-STA throughput falls much faster (BEB 466 -> 88 kbps).
2. Centralized single-agent beats BEB in direction at every N (+30 to +41 %), with CI support only at N=2 and N=4.
3. Independent per-AP agents get progressively worse than BEB (-9 -> -54 %) and are the least fair; CI support only at N=10. This is the motivation for the optional central critic (v1.7+), but v1.6.0 provides no test that a central critic fixes it.
4. Cost grows about linearly with total STAs (~15 s per STA per 1500-step run); agents add roughly 10-20 %.

## 7. Open
- Late-association / deassociation cause (deferred); end-of-run association not recorded for long runs.
- Why independent < BEB (not tested; inference in §3 only).
- AP count vs STA load is confounded; a fixed-total-STA sweep would separate them (needs new runs, not done). Deferred to v2.0.0 (station-density variation), user decision 2026-10-16.
- n=3 for N>=4; N=6/8 independent bimodal.
- Per-STA/per-AP numbers use the policy-window throughput definition from `summarize_run.py`; reward is not compared across modes.
