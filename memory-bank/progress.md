# Progress

<!-- Running log. Append, don't rewrite history. Newest at top.
     This tracks WORK STATUS (agent-facing, session to session).
     For the forward-looking feature plan, see ROADMAP.md instead —
     don't duplicate the full plan here, just what's actually in motion. -->

## Done

- **v0.5.0 CLOSED (tag `v0.5.0`, code 592b603, 2026-10-08)** — wildcard
  MinCw/MaxCw `Config::Set` replaced by per-node paths (`setApCw`, AP_i + its STAs). New `--apCws=A,B` (non-dryRun only,
  clamped 16..1024, count must equal #APs) and end-of-run `Per-AP CW check: PASS/FAIL` (readback at t=0, warm-up, end).
  Validation (dryRun/disableGym, seed 1, simTime 2): `--nWifi=5` dry and `--CW=64`, and `5,15` dry are byte-identical to
  pre-change output (10533 / 10263 / 9000 pkts). `5,15 --apCws=32,256`: AP1 32, AP2 256, per-AP received 7580 vs 2805,
  stats check PASS. `--apCws=1024,256`: AP2 stays 256 while AP1 goes 1024 (received 747 vs 9017). Gym smoke 10.59458 unchanged.

- **v0.4.0 CLOSED (tag `v0.4.0`, merge 98bbf79, 2026-10-08; code 97d99eb)** — per-AP sent_phy/sent_app/received/loss/
  throughput + totals + Jain. Runs (dryRun, disableGym, seed 1, simTime 2): `--nWifi=5` identical to
  pre-change (10533 pkts); 2,3 / 5,15 / 20,40 all `Per-AP statistics check: PASS` (Σ per-AP == globals
  exactly, sinkMatch yes, 0 cross-AP flows). Gym smoke passes, reward unchanged.

- **v0.3.0 CLOSED (tag `v0.3.0`, 2026-10-07)** — two APs in one ns-3 sim, unequal STA counts
  (20/40, 5/15, 2/3 all PASS): each STA associated with its own AP (Assoc trace
  check), per-AP UdpServer sink packets sum exactly to the global handler,
  0 cross-AP flows, clean exit with `--disableGym`. Single-AP (`--nWifi=5`)
  unchanged. Root-caused a real bug: both APs beaconed at identical times
  (`EnableBeaconJitter=false`) so nothing ever associated; fixed by enabling
  jitter only when AP count > 1. Also fixed the `--apStaCounts` default
  (was `20,40`, silently overriding `--nWifi`; now empty = single AP).
- **v0.2.0 CLOSED** — multi-AP design specification accepted: 2 APs in one
  ns-3 process, default STA split 20/40, per-AP observation/reward/statistics/
  CW contract, joint ns3-gym shape, sequential stepping, independent per-AP
  DDPG agents, no central critic for core v1 — 2026-09-16
- **v0.1.0 CLOSED (tag `v0.1.0`)** — baseline freeze: non-behavioral runner `baseline_v0_1_0.py`, `.gitignore` for CW artifacts, `docs/baseline-v0.1.0.md`, smoke-validated pipeline, episode-1 baseline numbers (nWifi=40: CW mean 196.9, throughput ≈34 Mbps, loss ratio 0.63) — 2026-09-16
- Full-run artifact archive `results/baseline-v0.1.0-full-partial-20260916/` (CW_data_bk.csv + run-7y4kp9yr.wandb + summary.json) — run stopped by user decision during episode 2; redo anytime with one command

## In progress

- v0.6.0 multi-AP ns3-gym (next, not started).
