# OSCAR v0.1.0 — Single-AP Baseline Freeze & Reproducibility

**Status:** CLOSED 2026-09-16 — code frozen, pipeline smoke-validated, baseline
numbers recorded from episode 1 of the reproduction run (full 3-episode run
stopped by user decision during episode 2; redo anytime with one command, §8).
**Date:** 2026-09-16
**Baseline repo:** `ns-3.29/scratch/linear-mesh/` (branch `major-project`, tag `v0.1.0`)

This document is the reference point that all later multi-AP versions (v0.2.0+)
compare against. Everything below is code-grounded (`cw.cc`, `scenario.h`,
`OSCAR_train.py`, `agents/our_ddpg/`), not paper-derived. Paper values that do
NOT match this code are flagged.

---

## 1. What v0.1.0 is (and is not)

v0.1.0 freezes the existing single-AP OSCAR baseline **without any behavioral
change**: same RL algorithm, same observation, same topology, no multi-agent
functionality. It adds only:

- `baseline_v0_1_0.py` — a non-behavioral reproduction runner (pins the
  `OSCAR_train.py` config/loop via `parse_args([])`, archives artifacts);
- this documentation;
- a `.gitignore` entry for the `cw.csv` simulation artifact.

### Frozen commits (repo `ns-3.29/scratch/linear-mesh/`)

| Commit | Content |
|---|---|
| `2bfbd22` | **Baseline code** (last commit that produces baseline behavior) |
| `735233c` | `chore: ignore cw.csv simulation artifact` (non-behavioral) |
| `ce5f7de` + fix | `feat(baseline): add v0.1.0 baseline freeze runner` (non-behavioral) |

A `v0.1.0` tag will be added only after the full reproduction run completes
(§8), so the tag certifies code + evidence together.

## 2. Environment (verified, see `docs/next-actions-results-2026-09-15.md`)

| Component | Version |
|---|---|
| OS | Ubuntu 22.04 (WSL2) |
| Compiler | g++ 11.4.0 (also drives the ns-3 waf build) |
| ns-3 | 3.29 (ns-allinone), build verified 2026-09-16 |
| ns3-gym | C++ contrib `opengym` 1.0.0; Python pkg `ns3gym` 0.1.0 (installed copy) |
| Python | 3.7.16 (`ns-3.29/venv`) |
| PyTorch | 1.13.1 (+cu117) |
| Gym | 0.26.2 (do NOT swap to Gymnasium — ns3gym imports `gym`) |
| NumPy | 1.21.6 |
| protobuf | Python 3.20.3 / system C++ 3.12.4 (wire-compatible per ns3-gym design) |
| pyzmq | 26.2.1 (bundles libzmq 4.3.5; C++ side uses system libzmq 4.3.4) |
| W&B | 0.18.7 (baseline runs use `WANDB_MODE=offline`; `--online` to sync) |

## 3. Single-AP topology (`cw.cc` + `scenario.h`)

| Aspect | Value (code-grounded) |
|---|---|
| Nodes | 1 AP + `nWifi` STAs (baseline: **40**), one BSS, SSID `ns3-80211ax` |
| Positions | AP (0,0,0); ALL STAs at (1,0,0); `ConstantPositionMobilityModel` |
| PHY | 802.11ax 5 GHz, `HeMcs11` (data + control), 20 MHz channel, 800 ns guard interval |
| Propagation | `YansWifiChannel` + `MatrixPropagationLossModel` (default loss **50 dB**, no per-pair entries) + constant-speed delay |
| Traffic | Per STA: OnOff UDP uplink STA→AP, constant rate **150 Mbps**, payload 1464 B (1500−20−8−8), ToS 0x70 (AC_BE), UdpServer sink on AP; `Rx` trace → `g_rxPktNum` |
| Tx counter | `PhyTxBegin` trace on all devices → `g_txPktNum` (counts AP + STAs) |
| Routing/ARP | Global routing populated; ARP cache pre-populated (1-year alive timeout) |
| Timing | Decision epoch = `envStepTime` = **0.01 s**; first RL step at sim-time **1.0 s**; `MyGetGameOver` always false |
| Seed | ns-3 side: default seed, `RngRun = 1` (pinned via `rng=1` default); `--seed` is parsed but the Python wrapper never forwards it |
| Scenarios | `basic` (all STAs active the whole run — the baseline) or `convergence` (staggered starts; not used for the baseline) |

## 4. RL configuration (the frozen agent)

### Observation (what the agent actually sees)

ns-3 sends a `history_length`-float box (300) of the per-step frame-loss ratio
`(sent − received) / sent` from the **whole WLAN** (Tx trace on all devices vs
AP Rx trace). **The Python side keeps only element 0** — the most recent loss
ratio — as a 1-scalar state (`state_dim = 1`). The other 299 values are
discarded (the `Preprocessor` output is computed but only used for logging).

### Action → CW mapping

1. DDPG actor outputs `a ∈ [−1, 1]` (tanh, `max_action = 1`).
2. During warmup (`time_step < start_timesteps = 300`): `action ~ U(0, 6)` directly.
3. Otherwise Python scales: `real_action = 6 · (a + 1) / 2 ∈ [0, 6]` (+ Gaussian
   exploration noise σ = 0.1·max_action, clipped to [−1,1] before scaling).
4. C++: `CW = 2^(real_action + 4)`, clamped to **[16, 1024]**.
5. Applied as **MinCw = MaxCw = CW on ALL Wi-Fi devices** (AP + every STA) via
   one wildcard `Config::Set` on the BE queue — one global CW for the WLAN.

### Reward

```
reward = rxPktDelta · 1464 · 8 / 1024 / 1024 / (5 · 150 · envStepTime) · 10
```

- Global (all flows pooled). First two steps return 0.
- If `reward > 1.0` or `< 0`: held at the previous value (clamping via `last_reward`).
- The `5 · 150` normalization is **hard-coded** (5 = old default station count,
  150 = offered load) — with nWifi=40 the raw reward saturates >1 and rides the
  clamp. NOT fixed in v0.1.0 (behavior change); revisit in the v0.2.0 design.

### DDPG hyperparameters (`agents/our_ddpg/` + `OSCAR_train.py` defaults)

| Parameter | Value | Note |
|---|---:|---|
| Actor hidden layers | 128, 128 | paper: 128, 128 ✓ |
| Critic hidden layers | 128, 128 | paper: 128, 128 ✓ |
| Actor lr (Adam) | **4e-4** | paper: 3e-4 ✗ |
| Critic lr (Adam) | **4e-3** | paper: 4e-3 ✓ |
| Batch size | **32** | paper: 64 ✗ |
| Discount γ | **0.7** | paper: 0.9 ✗ |
| Target update τ | **1e-3** | paper: 0.1 ✗ |
| Exploration noise | 0.1 (σ · max_action) | |
| Warmup (random actions) | 300 steps | = first 3 s of sim time |
| Replay buffer | 1,000,000 | paper: 1,000,000 ✓ |
| Seeds | torch/np seed 0 | ns-3: RngRun 1 (§3) |
| Episodes / steps | 3 × 1500 steps (15 s each) | per `OSCAR_train.py` |

## 5. Metrics recorded per run

W&B (step-level, from `agents/our_ddpg/loggers.py`, logged after step 300):
Current Collision Rate (= current loss-ratio observation), Round reward,
Per-ep reward, (Round) Megabytes sent — note: actually **Mbit** (known naming
bug), Chosen CW, Station count, Current throughput, Fairness index,
Observation i, actor_loss, critic_loss. Episode-level: Cumulative reward,
Speed, MB sent.

Local artifacts:
- `CW_data.csv` — per-step `(SimulationTime, CW)` written by the ns-3 side
  (overwritten per episode; the archived copy holds the **last** episode);
- `cw.csv` — per-flow FlowMonitor throughput dump, **never produced in the
  training flow** (see §7);
- archived W&B run (offline) — full metric history is in the `.wandb`
  transaction log (wandb 0.18.7 offline writes no `wandb-summary.json`).

## 6. Reproducibility statement

- Pinned: torch/np seed 0, ns-3 `RngRun=1`, fixed hyperparameters and topology.
- NOT bit-reproducible: the ZMQ port is random per run, system timing differs,
  and the CW trace depends on the lock-step exchange. Runs are **statistically
  comparable** (throughput/reward/CW trends), which is what later multi-AP
  comparisons need.

## 7. Known quirks (documented, NOT fixed in v0.1.0)

1. `jain_index()` (cw.cc) sums uninitialized `nominator`/`denominator` doubles
   → undefined behavior; the "Fairness index" metric may be garbage. Fixing it
   changes baseline metric values → deferred to a later, deliberate change.
2. MinCw=MaxCw=0 (invalid) until the first RL action at sim-time 1.0 s.
3. Hard-coded reward normalization `5·150` (see §4).
4. `sentMbytes` in extra-info is actually Mbit.
5. The final per-flow `cw.csv` dump at the end of `main()` never runs in the
   training flow: after the last Python step the sim blocks in the ZMQ
   lock-step exchange, so `Simulator::Run()` never returns and the dump is
   skipped. Relevant later: v0.4.0 (per-AP statistics) needs its own
   statistics path anyway.
6. State uses only 1 of 300 history values (largest modeling gap vs the OSCAR
   paper; a v0.2.0 design decision, per the audit §17.4).

## 8. Reproducing the baseline

From `ns-3.29/scratch/linear-mesh/` with the project venv:

```bash
# pipeline smoke check (~5 min; nWifi=5, 3 s sim, 1 episode, random actions)
../../venv/bin/python baseline_v0_1_0.py --smoke

# the recorded baseline reproduction (3 × 15 s episodes, nWifi=40, offline W&B)
../../venv/bin/python baseline_v0_1_0.py
```

Artifacts land in `results/baseline-v0.1.0-{smoke,full}-<timestamp>/`:
`summary.json` (provenance + headline metrics), `CW_data.csv`, the `.wandb`
history log, `wandb-metadata.json`, `requirements.txt`, `runner.log`.
Use `--online` to sync to the configured W&B entity/project instead.

## 9. Measured baseline numbers (episode 1 of the interrupted full run)

The full 3-episode reproduction was started 2026-09-16 and **stopped by user
decision during episode 2** (episode 1 completed all 1500 steps; episode 2 was
partial). The complete episode-1 CW trace was saved by the user as
`CW_data_bk.csv` before the episode-2 sim truncated the live file. The full
3-episode run can be redone anytime with one command (§8).

**Source of truth:** `results/baseline-v0.1.0-full-partial-20260916/`
(`summary.json` holds provenance + all numbers below; `CW_data_bk.csv` the raw
per-step trace; `run-7y4kp9yr.wandb` the offline W&B history; code at
`84ee49b`, clean tree, offline W&B run `7y4kp9yr`, nWifi=40).

### CW behavior (authoritative — C++-side per-step trace, episode 1)

| Statistic | Value |
|---|---:|
| Steps | 1500 (sim-time 0.01 → 15.00) |
| CW mean / median | **196.9 / 188** |
| CW min / max | 46 / 460 (clamps [16,1024] never hit) |
| Warmup steps 1–300 (random actions) mean | 224.7 |
| Policy steps 301–1500 mean | 190.1 |
| First-100 mean → last-100 mean | 117.0 → **315.4** (policy drove CW upward) |

### Throughput / reward / losses (supplementary — partial W&B history, corroborated by tqdm)

| Metric (episode-1 segment, steps 301–1500) | Value |
|---|---:|
| Current throughput | mean **33.9 Mbps**, median 35.7, last 36.7 |
| Episode "Speed" (avg over full episode) | 27.5 Mbps |
| Round reward | mean 0.458, last 0.447 |
| Cumulative episode reward | 676.2 (log_episode recorded 736.1) |
| Current Collision Rate (= loss-ratio obs) | mean 0.631 |
| Fairness index | mean 0.992 (**unreliable — §7.1 UB**) |
| actor_loss (last) / critic_loss (last) | −0.954 / 0.006 |

Caveats: (a) the offline W&B per-step series is a partial sample (wandb-core
batching + the SIGKILL), so its per-step statistics are indicative only — the
CW table above is authoritative; (b) ~6 Gbps offered (40 STAs × 150 Mbps)
against a ~34 Mbps received rate is consistent with the 0.63 loss ratio and
saturation behavior.

Smoke validation record (2026-09-16): pipeline end-to-end OK — run 1
`results/baseline-v0.1.0-smoke-20260916-123416/` (offline run `45i3cmy5`,
first collector version) archived fully. Run 2 (with the collector fixes)
completed training but crashed at summary collection; its partial archive
holds `CW_data.csv` + metadata + `requirements.txt` (no `.wandb`, no
`summary.json`). The collector fix is committed (`84ee49b`); its end-to-end
validation is deferred to the next full reproduction run (§8). Provenance
verified on both runs: clean tree, `git_dirty: false`.

## 10. References

- `docs/OSCAR-forensic-audit-2026-09-15.md` — full code audit (evidence for §7)
- `docs/next-actions-results-2026-09-15.md` — environment verification, mentor decision brief D1–D6 (input to v0.2.0)
- `docs/detailed_roadmap.md` §v0.1.0 — this milestone's requirements
- `memory-bank/architecture.md` — target multi-AP architecture
