# Benchmark: Azure for Students, Standard D2as_v4 (2026-11-10)

Run by xyz on their VM; script `tools/bench/run_bench.sh azure-d2as --parallel 2` (branch bench/common). Cell: 20,40 APs, beb, seed 0, simTime 15, 1500 steps.

| Item | Value |
|---|---|
| Hardware | 2 vCPU (AMD EPYC 7763, 1 core x 2 threads), 7 GB RAM seen, 29 GB disk |
| OS / toolchain | Ubuntu 22.04.5, GCC 11.4.0, protoc 3.12.4, libzmq 4.3.4, Python 3.7.17, torch 1.13.1+cpu |
| Clean ns-3 build + dry run | 183 s |
| Single cell | 1399 s (23.3 min), --check PASS |
| 2 seeds at once | 2213 s and 2214 s each, phase 2217 s, both exit 0 |
| Throughput | single 2.6 cells/h; 2 at once 3.2 cells/h (about 1.6x slower per run when sharing 2 threads) |

Notes: the student subscription had a 6-core regional quota (8-vCPU D8s_v5 at 0.404 USD/h was refused; D4s_v5 not selectable). Price of D2as_v4 per hour not reported (unverified). Smoke output pasted earlier came from a different machine (Azure Cloud Shell) and is not an Azure VM result.
