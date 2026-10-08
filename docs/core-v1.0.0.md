# v1.0.0 — Core milestone (2026-10-08)

Status: core system working and evidenced on 2,3 and 5,15. Open items are listed in §4.

## 1. Requirement → evidence

| Roadmap requirement | Evidence |
|---|---|
| One ns-3 simulation, 2 APs, unequal STAs | `cw.cc --apStaCounts`; association / per-AP stats checks PASS on 2,3, 5,15, 20,20, 20,40 (v0.3, v0.9 Test C) |
| One AP-level Actor-Critic per AP | `OSCAR_multi_ap_train.py`: one DDPG + replay per AP, disjoint params (v0.7, `--check`) |
| AP-local observation / reward | `--check` recomputes obs and reward per AP from that AP's counters every step (v0.9 Tests A, D) |
| AP-specific CW | `setApCw`, readback per AP every step (v0.5, v0.9 Test B) |
| Decentralized actors, local critics | Actor_i sees only state_i; critic_i trains on its own tuples (design §6) |
| W&B logging | `AP{i}/*`, `Global/*` keys, 1500 rows x 19 keys verified from the offline `.wandb` (v0.8). Online sync untested |
| Reproducible training | §2 |
| Baseline comparison | §3 |

## 2. Reproducibility

Command (from `ns-3.29/scratch/linear-mesh`):

```
../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --check
```

`--seed S` seeds torch/numpy and, new in v1.0.0, the ns-3 simulation (`ns-3 seed = S + 1`, because ns-3 rejects seed 0).
Before v1.0.0 the trainer did not pass a seed to ns-3 (it used the ns-3 default).

Evidence: two full runs (15 s, 1500 steps, defaults, seed 0, 2,3), `results/multi-ap-20261008-153807` and
`results/multi-ap-20261008-154141`: **all 17 trace.csv columns identical (0 differing lines of 3001)**, including actor/critic
losses. Both `--check` runs PASS (1500 steps, 19 W&B keys per row). Scope: same machine, same GPU/CPU, one seed.

## 3. Baseline comparison (2,3 and 5,15; 15 s; ns-3 seed 1; stepTime 0.01)

BEB = standard 802.11 backoff (`baseline_beb.py`, ns-3 `--dryRun`, CW min 16 / max 1024). Trained = independent per-AP DDPG
(`OSCAR_multi_ap_train.py`, 1 episode, seed 0, policy phase = steps 300–1500).

**Comparability caveat.** BEB throughput = received·1464·8 / 15 s over the whole run (dry-run counters include the 1 s
warm-up and the tail, no per-step window). Trained throughput = mean of per-step rx over the 15 s of stepping. The windows
are close but not identical, so differences of a few percent are not meaningful.

### 2,3
| | AP1 (2 STA) | AP2 (3 STA) | Global | Jain |
|---|---:|---:|---:|---:|
| BEB Mbps | 18.87 | 24.60 | 43.47 | 0.983 |
| Trained, policy phase Mbps | 9.46 | 30.88 | 40.34 | 0.800 |
| Trained, all steps Mbps | 9.58 | 28.74 | 38.32 | |

### 5,15
| | AP1 (5 STA) | AP2 (15 STA) | Global | Jain |
|---|---:|---:|---:|---:|
| BEB Mbps | 9.97 | 26.83 | 36.79 | 0.826 |
| Trained, policy phase Mbps (v0.9 run) | 30.76 | 7.67 | 38.42 | 0.846 |

The v0.9 5,15 run predates seed pinning (ns-3 default seed), so it is a different realization than the BEB row; not rerun for time.
Aggregate is ~4% above BEB (within the window caveat, one seed). Per-AP split is inverted: BEB gives each AP throughput roughly
proportional to its STA count; the trained agents let AP1 (5 STA) take ~80%. Jain here is over per-AP throughput, so it does not
measure per-STA fairness.

### Historical single-AP reference (v0.1, 40 STA)
CW 117 → 315, ~35.5 Mbps (33.9 Mibit/s), loss 0.631. Different topology and reward; reference only.

### Reading (fact vs inference)
- Fact: on 2,3 the trained agents did **not** beat plain BEB on aggregate throughput (40.3 vs 43.5) and are less fair (Jain 0.80 vs 0.98);
  on 5,15 aggregate is about equal (38.4 vs 36.8) with a very different split. On 2,3 both agents drive CW toward 16 (the BEB minimum); on 5,15 AP1 does, AP2 stays high for most of the policy phase.
- Inference (untested): with few STAs per AP the CW has little room to help; the 40-STA single-AP baseline is where OSCAR's gain
  was shown, so 20,20 / 20,40 are the informative cases. Not claimed.
- One episode, one seed. No confidence intervals.

## 4. Regressions
Smoke cumulative reward 10.59458; `--nWifi=5` dry seed 1 simTime 2 -> 10533 pkts (cw.cc untouched, no rebuild).

## 5. Open / deferred
- 20,20 and 20,40 long runs (60 STAs, hours) — deferred to v1.1 (user decision, session time).
- Global-CW OSCAR baseline (Baseline B) and multi-seed statistics — v1.1.
- AP2 deassociation at 20,40 (STA nodeId=42, t=1.144 s → 1.277 s) — cause unproven.
- W&B online sync untested; multi-AP gym supports `basic` scenario only; warm-up actions stored in [-1,1].
- Baseline reward formula differs from the multi-AP one; throughput unit (Mibit/s vs Mbps) differs from the v0.1 report.
