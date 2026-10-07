# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

v0.3.0 (two-AP ns-3 topology) is implemented and validated (2026-10-07), pending
merge/tag approval. Next milestone: **v0.4.0 per-AP statistics**.

## Recent decisions

- v0.1.0 changes nothing behavioral: only the freeze runner
  (`baseline_v0_1_0.py`, pinned to `OSCAR_train.py` defaults), docs, and
  `.gitignore` entries (`cw.csv`, `CW_data*`).
- W&B defaults to offline in the runner (`--online` to sync). wandb 0.18.7
  offline writes no `wandb-summary.json` — metrics come from the run object or
  by parsing the `.wandb` log (`rec.history.item`, keys in `nested_key`).
- Full 3-episode reproduction run was STOPPED by user decision during
  episode 2 (2026-09-16); episode 1 (1500 steps) completed and its CW trace
  was saved by the user as `CW_data_bk.csv`. Archived in
  `results/baseline-v0.1.0-full-partial-20260916/` (incl. `run-7y4kp9yr.wandb`
  and a hand-written `summary.json` with all extracted numbers).
- Episode-1 baseline: CW mean 196.9 (warmup 224.7 → policy 190.1, upward
  trend), throughput ≈ 34 Mbps (episode avg 27.5), loss ratio 0.631, reward
  mean 0.458. CW file = authoritative; wandb per-step series = partial/biased
  sample (documented caveat).
- Known quirks (jain_index UB, MinCw=MaxCw=0 start, hard-coded 5·150 reward
  constant, `cw.csv` never produced in the training flow, 1-of-300 history
  state) documented in `docs/baseline-v0.1.0.md` §7 — NOT fixed in v0.1.0.
- v0.2.0 accepted defaults from the audit: one ns-3 process, per-AP DDPG
  Actor-Critic agents, local critics only for core v1, per-AP goodput reward,
  one raw local loss scalar per AP initially, and sequential joint stepping.
  See `docs/multi-ap-design-v0.2.0.md` and `docs/adr/0002-multi-ap-v0-2-0-defaults.md`.

## Blockers / open questions

- Optional: redo the full 3-episode baseline run for a stronger reference
  (`python baseline_v0_1_0.py`); episode-1 data is already recorded.

## Next step

v0.3.0 technically validated 2026-10-07 (see progress.md). Remaining before
closing: optional gym-path regression `../../venv/bin/python baseline_v0_1_0.py --smoke`
(run from `ns-3.29/scratch/linear-mesh/`), then user-approved merge to `main`
and tag `v0.3.0` (tags start fresh from here; old v0.1.0 tag references are obsolete).

Then **v0.4.0 per-AP statistics** (`cw.cc`): per-AP rx via bound callbacks on each
AP's UdpServer, per-AP tx, globals = sums. Open question for the user: count STA
data tx only, or also AP control frames (`g_txPktNum` currently counts PhyTxBegin
on ALL devices incl. beacons/ACKs).

Validation notes for later milestones:
- Run binary directly: `LD_LIBRARY_PATH=ns-3.29/build/lib ns-3.29/build/scratch/linear-mesh/linear-mesh <args>`
  from a scratch dir (writes `cw.csv` to cwd). A 2-AP, 60-STA, simTime=2 run takes ~2.5 min CPU.
- FlowMonitor rx counts only cover the post-warmup window and disagree with the sink
  handler (e.g. 0 vs ~9000 pkts) — use UdpServer counts / handler, not FlowMonitor rx.
- Single /24 subnet fits ~253 nodes; widen before scaling to 10 APs.
- CW is still a wildcard `Config::Set` over all nodes (v0.5 replaces it).
