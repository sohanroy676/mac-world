# GitHub Actions full-cell timing, 2026-11-03

Workflow `.github/workflows/actions-timing.yml` on branch `feature/actions-compute`, commit `5233c1f`, run [41685034879](https://github.com/sohanroy676/mac-world/actions/runs/41685034879). Two jobs ran in parallel on separate hosted runners, each one full-size cell: `--apStaCounts 20,40 --seed 0 --check`, 1500 steps (15 s simulated), default hyperparameters. W&B offline. Nothing outside `.github/` and `docs/` was changed, and no other branch or local run was touched.

## Results (fact)
| Cell | Trainer wall time | Result | W&B rows | Job total | Clean build in job |
|---|---|---|---|---|---|
| 20,40 `beb` seed 0 | 1037 s (17 min 17 s) | `RESULT: PASS`, 1500 steps | 1500 x 19 keys | 25 min 7 s | 6 min 20 s |
| 20,40 `independent` seed 0 | 1531 s (25 min 31 s) | `RESULT: PASS`, 1500 steps | 1500 x 19 keys | 34 min 55 s | 7 min 32 s |

Whole workflow: 17:31:18 to 18:06:15 UTC (about 35 min), both cells in parallel. Output files (log, W&B offline run, CSVs) were uploaded as artifacts `timing-beb` (652 KB) and `timing-independent` (928 KB), kept 7 days.

Final-step snapshot (single seed, not a result to cite): BEB global throughput 30.45 Mbps, Jain 1.0; independent 31.62 Mbps, Jain 0.81, final CWs 61 and 316.

## Hardware and software
- Runner label `ubuntu-24.04`, job container `ubuntu:22.04`. Hosted runner, 4 vCPU, 15 GB RAM, about 85 GB free disk (from runs 2-5 of the smoke test).
- CPU: AMD EPYC 7763, 2 cores x 2 threads, read in smoke-test runs 2 and 3. The "Machine info" step of these timing jobs ran but its output was not read back, so the CPU of these two particular runners is **not confirmed**.
- GCC 11.4.0, protoc 3.12.4, libzmq 4.3.4-2, Python 3.7.17 (deadsnakes, OpenSSL 3.0.2), torch 1.13.1+cpu, numpy 1.21.6, gym 0.26.2, wandb 0.18.7, protobuf 3.20.3, pyzmq 26.2.1, matplotlib 3.5.3, ns-3.29 default (debug, -O0) profile.
- Setup times per job: checkout 15 s, Python and pip installs 53-70 s, one transient pip "Network is unreachable" retry on the independent job that recovered by itself.

## Comparison with lab logs (fact for the lab numbers, inference for the conclusion)
- Lab BEB 20,40: 16-21 min on one laptop and about 42 min on another (`docs/results/scaling-v1.6.0.md` notes). Actions: 17 min 17 s, inside the faster range.
- Lab trained runs at 20,40: about 15-20 min (`core-v1.0.0.md`); other lab batches 1300-2020 s (`improvement-v3.0.0.md`). Actions independent: 1531 s, inside that range.
- Inference: one hosted 4 vCPU runner is about as fast as the lab laptop per run, not faster. The gain is parallelism: both cells finished in the time of the slower one (35 min including a fresh build), where a laptop doing them back to back needs about 2 x 20 min or more.

## Caveats
- One seed per mode, one run each; run-to-run spread on hosted runners is not measured (the build alone took 3:38 to 7:32 across five runs).
- Each job rebuilt ns-3 from scratch (6-8 min). Caching the build would remove this from later jobs.
- Only 2 runs were in parallel; 20 concurrent jobs is the documented limit, not tested.
- Runs are GitHub-hosted use for this repo's own evaluation; see the terms note in `research/github-actions-feasibility-2026-11-03.md`.
