# v0.9.0 — Two-AP validation (2026-10-08)

Status: Tests A–F PASS on short runs. Long training done for **2,3** and **5,15** (see §3); 20,20 / 20,40 long runs are
deferred to a later session. Run dirs are under `ns-3.29/scratch/linear-mesh/results/` (not committed).

## 1. Tests (roadmap §v0.9.0)

| Test | What was run | Result |
|---|---|---|
| A independent obs | Trainer `--check` recomputes each AP's obs and loss as `(tx_i−rx_i)/tx_i` from its own counters, every step. Gym sweep `5,15 --phases "0,3;5,3"` (AP1 CW 16→512, AP2 fixed 128) | PASS. AP2 rx went 126→320 when AP1 backed off: shared-channel coupling (expected), not code leakage |
| B independent CW | `test_multi_ap_gym.py` 2,3 and 5,15, default phases (64/512, then swapped) | PASS, readback matches per AP every step |
| C association | Dry runs 2,3 / 5,15 / 20,20 / 20,40 (`--seed=1 --simTime=2`) | Association, per-AP statistics and per-AP CW checks all PASS; wrongAp=0, unassociated=0 |
| D reward | Trainer `--check` recomputes `rx_i·1464·8/1e6/(150·stas_i·stepTime)`, clamped [0,1], every step | PASS |
| E reset | `--episodes 2` (2,3, 3 s, 0.1 s step): each episode starts at Step 1, cumulative reward is per episode, W&B rows = steps, no leftover ns-3 process | PASS (60 steps) |
| F repeated runs | Seeds 0, 0, 1, 1, 2 (30 steps each) | All PASS. Seed 0 twice: trace columns 1–9 (state, action, CW, reward, …) identical |

## 2. Findings

- **Deassoc=1 at 20,40 (AP2), explained as far as observed:** with a new trace in `cw.cc`, STA nodeId=42 deassociated
  from AP2's BSSID at t=1.144 s and re-associated with the same BSSID at t=1.277 s (~0.13 s). Final state ok=40/40,
  wrongAp=0. Cause not proven; inference: a missed-beacon timeout under saturation (60 STAs at 150 Mbps each). It is
  not 2-AP specific logic and does not affect the PASS checks. Seen only at 20,40, not at 20,20 / 5,15 / 2,3.
- **Harness fix:** the `.wandb` file was copied before the writer had flushed (copy 32768 B vs original 45272 B), which
  made the `--check` readback fail intermittently (seed 1). The trainer now waits for the size to settle before copying.
- **Leftover-process check** uses `pgrep -x linear-mesh`; do not run another ns-3 job at the same time or it will
  report a false positive (happened once, with a concurrent dry run).

## 3. Long training (15 s, 1500 steps, 300 warm-up, baseline settings)

### 2,3 (3m46s wall, `--check`: all per-step checks PASS)

| Metric | AP1 (2 STA) | AP2 (3 STA) | Global |
|---|---:|---:|---:|
| CW mean warm-up / policy | 224.2 / 22.5 | 266.7 / 19.8 | |
| CW first-100 → last-100 | 223.8 → 17.3 | 282.7 → 17.2 | |
| Throughput Mbps (policy) | 9.46 | 30.88 | 40.34 |
| Loss ratio | 0.562 | 0.565 | 0.564 |
| Reward mean (policy) | 0.032 | 0.069 | |
| Jain fairness (mean thr) | | | 0.800 |

Observation: both agents drove CW to the minimum (16), unlike the 40-STA single-AP baseline (CW 117 → 315,
~35.5 Mbps, loss 0.631). With 5 STAs total low CW is plausible, but this is **not** evidence of correct learning:
the comparison needs a 40-STA run (20,20) and matched baselines (v1.1). Not a claim.

Comparison caveats: baseline throughput is Mibit/s (33.9 ≈ 35.5 Mbps); multi-AP is Mbps (1e6). Baseline reward uses a
different formula (5·150 constant), so rewards are not comparable. One episode, one seed.

### 5,15 (8m33s wall, `--check`: all per-step checks PASS)

| Metric | AP1 (5 STA) | AP2 (15 STA) | Global |
|---|---:|---:|---:|
| CW mean warm-up / policy | 224.2 / 23.0 | 266.7 / 361.6 | |
| CW first-100 → last-100 | 223.8 → 17.3 | 282.7 → 44.9 | |
| Throughput Mbps (policy) | 30.76 | 7.67 | 38.42 |
| Loss ratio | 0.589 | 0.612 | 0.596 |
| Reward mean (policy) | 0.041 | 0.003 | |
| Jain fairness (mean thr) | | | 0.846 |

Observation: independent local agents diverged: AP1 sits at CW≈16 and takes ~80% of the throughput; AP2 spent most of
the policy phase at high CW (mean 362) and ended near 45, with a much smaller share. Global throughput (38.4 Mbps) is
about the same as 2,3 (40.3) and the 40-STA baseline (~35.5). Per-AP isolation holds (checks PASS); the unequal outcome
is a learning/contention result, not evidence of a leak. Same Python seed 0 gives identical warm-up CW columns as 2,3
(expected: same random warm-up actions). One episode, one seed.

### 20,20 / 20,40
Not yet done (time-boxed session). 60 STAs is much slower per step than 5,15 (the 2 s dry run alone takes >10 min).
Command: `../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts X --simTime 15 --stepTime 0.01 --historyLength 300
--start_timesteps 300 --check`, then `summarize_run.py results/multi-ap-<ts>`. Run one ns-3 job at a time.

## 4. Regressions
`--nWifi=5 --dryRun=true --disableGym=true --simTime=2 --seed=1` → sinkReceivedPackets=10533 on the rebuilt binary
(rebuilt 14:17, `cw.cc` trace lines only). Gym smoke (`baseline_v0_1_0.py --smoke`): not re-run yet.
