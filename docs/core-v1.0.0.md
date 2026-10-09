# v1.0.0 — Core milestone (2026-10-08)

Status: core system working and evidenced on 2,3, 5,15, 20,20 and 20,40. Open items are in §5.

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
| Rerun 2026-10-08 (closeout, this machine, rebuilt binary), policy phase Mbps | 9.40 | 31.00 | 40.40 | 0.798 |
| Rerun, all steps Mbps | 9.54 | 28.83 | 38.37 | |

The rerun (`results/multi-ap-20261008-211952`, `--check` PASS) is close to the first run but not bit-identical in the summary
(40.40 vs 40.34 Mbps, within 0.2%); the §2 identical-trace evidence was from two runs in one session. Cause of the small difference not investigated.

### 5,15
| | AP1 (5 STA) | AP2 (15 STA) | Global | Jain |
|---|---:|---:|---:|---:|
| BEB Mbps | 9.97 | 26.83 | 36.79 | 0.826 |
| Trained, policy phase Mbps (v0.9 run) | 30.76 | 7.67 | 38.42 | 0.846 |
| BEB Mbps, rerun on this machine (`--seed 1`) | 9.97 | 26.83 | 36.79 | 0.826 |
| Trained, policy phase Mbps, seed-pinned rerun 2026-10-08 | 32.67 | 6.89 | 39.56 | 0.818 |
| Trained, all steps Mbps, seed-pinned rerun | 28.74 | 10.33 | 39.06 | |

The v0.9 5,15 row predates seed pinning (ns-3 default seed); the seed-pinned rerun (`results/multi-ap-20261008-214229`, `--check` PASS) is the
matched comparison against BEB (BEB reproduced exactly on this machine). Rerun: aggregate is ~7.5% above BEB (39.6 vs 36.8), AP1 takes ~83%;
AP1 CW settles near 17, AP2 stays high (last-100 mean 237). The v0.9 run gave 38.4 Mbps (~4% above BEB).
Gains of this size are within the window caveat (one seed). Per-AP split is inverted: BEB gives each AP throughput roughly
proportional to its STA count; the trained agents let AP1 (5 STA) take ~80%. Jain here is over per-AP throughput, so it does not
measure per-STA fairness.

### 20,20 and 20,40 (60 STA; added 2026-10-08, same settings: 15 s, stepTime 0.01, seed 0 -> ns-3 seed 1)
Run times: BEB ~13.5 min (20,20); trained ~18 min (20,20). Both trained runs: `--check` PASS, 1500 steps, 1500 W&B rows x 19 keys.
Results dirs (gitignored): `results/multi-ap-20261008-185530` (20,20), `results/multi-ap-20261008-194402` (20,40).
Same comparability caveat as above; one episode, one seed.

20,20
| | AP1 | AP2 | Global | Phy loss | Jain |
|---|---:|---:|---:|---:|---:|
| BEB Mbps | 15.58 | 16.63 | 32.21 | 0.713 | 0.999 |
| Trained, policy phase Mbps | 15.67 | 14.38 | 30.05 | 0.700 | 0.998 |
| Trained, all steps Mbps | 16.00 | 14.75 | 30.75 | | |

20,40
| | AP1 | AP2 | Global | Phy loss | Jain |
|---|---:|---:|---:|---:|---:|
| BEB Mbps | 9.36 | 19.84 | 29.20 | 0.747 | 0.886 |
| Trained, policy phase Mbps | 13.20 | 19.14 | 32.34 | 0.684 | 0.972 |
| Trained, all steps Mbps | 13.33 | 18.79 | 32.12 | | |

CW (trained, mean of last 100 steps): 20,20 AP1 44.7 / AP2 82.7; 20,40 AP1 116.9 / AP2 133.5 (warm-up means ~224 / ~267).
Policy-phase mean reward is ~0.003-0.005 per AP (reward is normalized by offered load; scale not investigated).

- Fact: at 20,20 trained is ~7% below BEB in the policy phase (30.0 vs 32.2) with slightly lower loss; fairness equal. No improvement shown.
- Fact: at 20,40 trained is ~11% above BEB (32.3 vs 29.2), lower loss (0.684 vs 0.747), more even split (Jain 0.972 vs 0.886); the gain is on AP1 (13.2 vs 9.4), AP2 about equal.
- Differences of a few percent are within the window caveat; one seed gives no confidence interval.
- Inference (untested): CW tuning helps more when load is uneven (20,40) than when it is balanced (20,20).
- Deassociation at 20,40 (trained run log): six STAs (nodeId 25, 33, 35, 37, 38, 39) left AP2's BSSID at t=1.144 s and re-associated to it at 1.274-1.311 s. The earlier note (single STA nodeId=42) was from a different run. BEB stdout was not saved, so BEB was not checked. Cause unproven.

### Historical single-AP reference (v0.1, 40 STA)
CW 117 → 315, ~35.5 Mbps (33.9 Mibit/s), loss 0.631. Different topology and reward; reference only.

### Reading (fact vs inference)
- Fact: on 2,3 the trained agents did **not** beat plain BEB on aggregate throughput (40.3 vs 43.5) and are less fair (Jain 0.80 vs 0.98);
  on 5,15 aggregate is modestly above BEB (38.4 and 39.6 vs 36.8, two runs) with a very different split. On 2,3 both agents drive CW toward 16 (the BEB minimum); on 5,15 AP1 does, AP2 stays high for most of the policy phase.
- Across all four topologies trained is below BEB on 2,3 (-7%) and 20,20 (-7%), above on 5,15 (+4 to +8%) and 20,40 (+11%). The wins are in the unequal-load cases (5,15; 20,40) and the losses in the balanced-ish ones (2,3; 20,20).
- Inference (untested): CW tuning helps more when load is uneven; with balanced load BEB is already near-optimal. Not claimed.
- One episode, one seed. No confidence intervals.

## 4. Regressions
Smoke cumulative reward 10.59458; `--nWifi=5` dry seed 1 simTime 2 -> 10533 pkts. Re-verified 2026-10-08 on a rebuilt binary
(the previous binary predated the v0.9 `cw.cc` change): smoke 10.59458, 10533 pkts, `5,15 --apCws=32,256` CW + stats checks PASS (9000 pkts),
`test_multi_ap_gym.py` PASS on 2,3 and 5,15.

## 5. Open / deferred
- Reward scale: policy-phase reward is ~0.003-0.07 per step (0.003-0.005 at 60 STAs). It follows design §3 (goodput / (150 Mbps x STAs x step)); because the offered load saturates the channel, the [0,1] range is barely used. Inference (untested): a weak learning signal may contribute to the modest or uneven gains. Not changed in v1.0.0.
- 20,20 and 20,40 long runs: DONE 2026-10-08 (§3; ~15-20 min each, not hours). Tag `v1.0.0` awaits user approval.
- Global-CW OSCAR baseline (Baseline B) and multi-seed statistics — v1.1.
- AP2 deassociation at 20,40 (t=1.144 s; STA nodeId=42 in one run, six STAs in the 2026-10-08 trained run, §3) — cause unproven.
- W&B online sync untested; multi-AP gym supports `basic` scenario only; warm-up actions stored in [-1,1].
- Baseline reward formula differs from the multi-AP one; throughput unit (Mibit/s vs Mbps) differs from the v0.1 report.
- Correction (2026-10-09, v1.1.0): `--seed`/`--rng` did not change the ns-3 simulation until `cw.cc` was fixed (commit 0e71414); the "ns-3 seed" pinning in §2/§3 only affected agent-side randomness. Seed 1 results are unchanged by the fix. BEB whole-run numbers here are also biased high vs the per-step window (e.g. 2,3: 43.47 vs 40.47 Mbps). See `docs/benchmark-v1.1.0.md`.
