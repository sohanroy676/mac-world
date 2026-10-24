# v2.8.0: attempt to beat OSCAR-style global CW with cooperative per-AP agents (negative result)

Status: experiment closed 2026-10-25 on branch `feature/v2.8.0-coop-reward`. **No improvement over global-CW OSCAR was found.** Code is optional and off by default (existing modes give byte-identical traces). Not merged, pushed or tagged.

## 1. Question and rule (fixed before the runs)
Can a per-AP design beat `global` (one OSCAR-style agent, one CW for all APs) on aggregate throughput? Claim only if the paired (same ns-3 seed) shared − global delta has a 95 % CI above 0 on seeds not used for tuning.

## 2. Diagnosis that motivated it (fact, existing fixed-binary traces, 15,15,15,15 and larger)
`global` puts all APs on one CW (157–459) and reaches 34–39.5 Mbps. `independent` agents each settle on a different near-constant CW (some at 16, others 500–1000), 8–28 Mbps. Per-step rewards are about 0.004. All APs share one Yans channel, so the network is probably one collision domain (inference), which limits headroom over a good common CW.

## 3. What was added (Python only, no `cw.cc` change, no rebuild)
| Flag / mode | What | Commit |
|---|---|---|
| `--mode coop --rewardMix L` | independent agents, own-loss obs only, replay reward `(1-L)·r_i + L·r_global` | 1e7ea5d |
| `--explNoiseEnd x` | exploration noise decays linearly from `--expl_noise` to x after warm-up (default off) | ea6ce84 |
| `--mode shared --sharedApId {0,1}` | ONE actor-critic and ONE replay for all APs, input `[own loss, AP id/(N-1)]`, team reward, one update per env step; ADR-0004 | 45abf24 |

`aggregate_bench.py` gained the modes and a paired table against global. `independent`, `global` and `coop L=1` short traces are byte-identical before and after each change.

## 4. Dev runs (tuning seeds 0–2, 15,15,15,15, last-300-step aggregate Mbps)
| Mode | Mean ± 95 % CI | Per seed 0 / 1 / 2 |
|---|---|---|
| BEB | 27.55 ± 1.01 | – |
| Global | 35.64 ± 6.84 | 34.2 / 38.8 / 33.9 |
| Independent | 20.14 ± 6.78 | 23.2 / 18.1 / 19.0 |
| Coop L=1 | 27.90 ± 18.91 | 36.4 / 21.8 / 25.4 |
| Coop L=0.5 | 24.97 ± 21.62 | 34.8 / 18.1 / 22.0 |
| Coop L=1, noise 0.1→0.01 | 26.47 ± 22.08 | 36.3 / 19.0 / 24.1 |
| Shared (AP id, L=1) | 34.62 ± 15.12 | 37.9 / 27.6 / 38.4 |

Reading (dev seeds only): a team reward and less exploration noise did not fix the lack of agreement between agents (CW traces: each agent keeps its own CW, e.g. [951, 209, 39, 206]). Parameter sharing looked like global (-1.0 ± 22.0 Mbps vs global, above it in 2 of 3 seeds), so it went to confirmation.

## 5. Confirmation (fresh seeds 10–14, never used for tuning; fresh BEB and global, 15/15 PASS)
| Mode | Mean ± 95 % CI | Seed 10 / 11 / 12 / 13 / 14 |
|---|---|---|
| BEB | 27.85 ± 0.65 | 27.1 / 27.9 / 28.0 / 27.7 / 28.5 |
| Global | 32.94 ± 11.01 | 37.2 / 33.2 / 17.5 / 37.9 / 38.9 |
| Shared | 27.76 ± 19.04 | 3.3 / 22.2 / 39.5 / 35.6 / 38.3 |

- Shared − global: **-5.18 ± 25.04 Mbps**, above global in **1 of 5** seeds. CI includes 0.
- Shared − BEB: -0.09 ± 18.50 Mbps. Global − BEB: +5.09 ± 11.11 Mbps (+18.4 ± 39.8 %), CI includes 0 at n=5.
- **Decision rule not met: no improvement claim.**

## 6. Observations and limits
- Shared is as good as global on seeds 13 and 14 (35.6 vs 37.9, 38.3 vs 38.9), beats it clearly on seed 12 (39.5 vs 17.5) and fails badly on seed 10 (3.3 vs 37.2). It is unstable across seeds.
- Global itself is unstable here: seed 12 gave 17.5 Mbps, below BEB. The earlier "global ≈ +30 % over BEB" for this topology (n=3) shrinks to +18 % with a CI including 0 at n=5.
- The dev mean for shared (34.6) did not hold on fresh seeds (27.8): the dev result was optimistic (small n, chosen after looking).
- Shared gets N times more samples per update than independent agents; that advantage would have counted toward any gain.
- Untested: why shared collapses at seed 10 (CW traces not inspected), the `--sharedApId 0` ablation, other topologies (6×10, imbalance), longer training, reward scaling for the shared agent. Only 15,15,15,15 was tested.
- Raw run dirs are local only (`ns-3.29/scratch/linear-mesh/results/bench-coop-dev-*`, `bench-shared-dev`, `bench-shared-confirm`). Tables, per-seed CSVs and manifests are in `docs/figures/v2.8.0/`.

## 7. Conclusion
Within this experiment no per-AP variant beat global-CW OSCAR. The honest summary for the report: cooperative reward and exploration changes do not help; parameter sharing recovers global-level performance in some seeds but is unstable, and the confirmation does not support a gain (-5.2 ± 25.0 Mbps vs global, 1 of 5 seeds above).
