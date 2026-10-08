# Progress

<!-- Running log. Append, don't rewrite history. Newest at top.
     This tracks WORK STATUS (agent-facing, session to session).
     For the forward-looking feature plan, see ROADMAP.md instead —
     don't duplicate the full plan here, just what's actually in motion. -->

## Done

- **v1.0.0 CLOSED (closeout 2026-10-08, branch `fix/v1.0.0-closeout`)** — audit vs roadmap: no required item missing in code. Reruns on rebuilt binary: 2,3 trained 40.4 Mbps (doc 40.3), 5,15 seed-pinned trained 39.6 vs BEB 36.8 (+7.5%, AP1 ~83%), BEB 5,15 reproduced exactly; v0.5 CW check + v0.6 gym tests PASS. Docs: README multi-AP section, CLAUDE.md roadmap line, reward-scale note (core-v1.0.0 §5). CHANGELOG not regenerated (`conventional-changelog` fails in WSL: `node: not found`). Next: v1.1.0.

- **v1.0.0 long runs done (2026-10-08, branch `feature/v1.0.0-long-runs`, not merged; tag still pending user approval)** — binary rebuilt (regressions: smoke 10.59458, `--nWifi=5` dry 10533 pkts). BEB vs trained (policy phase, seed 0/ns-3 seed 1): 20,20 32.2 vs 30.0 Mbps (no gain); 20,40 29.2 vs 32.3 Mbps, Jain 0.886 -> 0.972. Both trained `--check` PASS. 20,40 trained log: 6 STAs deassoc from AP2 at t=1.144 s, back by 1.31 s (cause unproven; BEB not checked). Each run took ~13-18 min. Details `docs/core-v1.0.0.md` §3.

- **v1.0.0 implemented (merged to main + pushed 2026-10-08; NOT tagged — tag after 20,20/20,40 long runs)** — trainer passes ns-3 seed (py seed+1; ns-3 rejects 0); new `baseline_beb.py`. Two 2,3 long runs seed 0: trace.csv identical (all 17 cols). BEB vs trained: 2,3 43.5 vs 40.3 Mbps; 5,15 36.8 vs 38.4 (trained split inverted, AP1 ~80%). Regressions unchanged. 20,20/20,40 + global-CW baseline deferred to v1.1. Details `docs/core-v1.0.0.md`.

- **v0.9.0 CLOSED (tag `v0.9.0`, 2026-10-08)** — Tests A–F PASS on short runs (details `docs/validation-v0.9.0.md`).
  Trainer `--check` extended (Test A obs, Test D reward, Test E per-episode); new `summarize_run.py`; `.wandb` copy race fixed; `cw.cc` prints STA deassoc/re-assoc
  (rebuilt; `--nWifi=5` dry still 10533 pkts; smoke 10.59458). Deassoc at 20,40: STA nodeId=42 off AP2 at t=1.144s, back to the same BSSID at 1.277s (cause unproven).
  Long runs done: 2,3 (3m46s, both CWs -> ~16, 40.3 Mbps) and 5,15 (8m33s, AP1 CW~17 30.8 Mbps vs AP2 7.7 Mbps, Jain 0.846).
  NOT done: long runs 20,20 / 20,40 (60 STAs, very slow; 2 s dry run >10 min). 20,20 is the closest match to the 40-STA baseline.

- **v0.8.0 CLOSED (tag `v0.8.0`, code 4d72bed, merged to main + pushed, 2026-10-08)** — `OSCAR_multi_ap_train.py` logs per-AP + Global metrics to W&B (offline default, `--online`, `--wandb_project`); helpers `jain`, `step_metrics` in `multi_ap.py`. `--check` now reads the `.wandb` file back and asserts all keys per step, Global/Throughput == Σ AP, Fairness == Jain(per-AP thr). Validation: `--apStaCounts 2,3 --simTime 3 --stepTime 0.1 --historyLength 20 --start_timesteps 10 --batch_size 8 --check` -> PASS, 30 rows x 19 keys. Regression: smoke 10.59458, `--nWifi=5` dry 10533 pkts. No cw.cc/wrapper/agent changes. Results dir prefix now `results/multi-ap-<ts>`. Online sync untested.

- **v0.7.0 CLOSED (tag `v0.7.0`, code fc9c432, 2026-10-08)** —
  new `OSCAR_multi_ap_train.py` (one DDPG + replay per AP, state_i = newest loss_i, reward_i from parse_ap_info, per-AP
  Preprocessor for logging only, CSV trace in `results/v0.7.0-<ts>/`). No cw.cc/wrapper/agent changes. Validation:
  `--apStaCounts 2,3 --simTime 3 --stepTime 0.1 --historyLength 20 --start_timesteps 10 --batch_size 8 --check` -> RESULT PASS
  (30 steps, per-AP replay rows/CW/reward asserted every step, disjoint params, finite losses, no leftover ns-3 process).
  Regression: gym smoke 10.59458, `--nWifi=5` dry 10533 pkts. Deliberate difference: warm-up actions stored in [-1,1] (baseline stores U(0,6)).

- **v0.6.0 CLOSED (tag `v0.6.0`, 2026-10-08)** — joint per-AP obs/action/reward in cw.cc,
  `multi_ap.py`, `test_multi_ap_gym.py`. Validation: gym test PASS on 2,3 (64/512 then swapped) and 5,15 (64/512, 1024/16): readback
  CW matches action per AP every step, rewards in [0,1]. Regression: `--nWifi=5` dry 10533 pkts / 117.65 MB, `5,15` dry 9000 pkts,
  stats+CW checks PASS, gym smoke cumulative reward 10.59458 unchanged.

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

- v0.9.0 validation (next, not started): 2-AP runs with different STA distributions (e.g. 5,15 / 20,40), longer training, compare vs baseline.
