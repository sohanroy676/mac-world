# Progress

<!-- Running log. Append, don't rewrite history. Newest at top.
     This tracks WORK STATUS (agent-facing, session to session).
     For the forward-looking feature plan, see ROADMAP.md instead —
     don't duplicate the full plan here, just what's actually in motion. -->

## Done

- **v0.2.0 CLOSED** — multi-AP design specification accepted: 2 APs in one
  ns-3 process, default STA split 20/40, per-AP observation/reward/statistics/
  CW contract, joint ns3-gym shape, sequential stepping, independent per-AP
  DDPG agents, no central critic for core v1 — 2026-09-16
- **v0.1.0 CLOSED (tag `v0.1.0`)** — baseline freeze: non-behavioral runner `baseline_v0_1_0.py`, `.gitignore` for CW artifacts, `docs/baseline-v0.1.0.md`, smoke-validated pipeline, episode-1 baseline numbers (nWifi=40: CW mean 196.9, throughput ≈34 Mbps, loss ratio 0.63) — 2026-09-16
- Full-run artifact archive `results/baseline-v0.1.0-full-partial-20260916/` (CW_data_bk.csv + run-7y4kp9yr.wandb + summary.json) — run stopped by user decision during episode 2; redo anytime with one command

## In progress

- v0.3.0 — Two-AP ns-3 topology (next milestone)
