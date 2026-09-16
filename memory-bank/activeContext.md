# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

v0.2.0 is CLOSED (design contract accepted 2026-09-16). Next milestone:
**v0.3.0 — Two AP ns-3 topology**: create AP1 + AP2 in one ns-3 simulation,
support unequal station counts, and validate packet flow before RL changes.

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

Continue v0.3.0 WIP from branch `feature/v0.3.0-two-ap-topology`.

Current WIP changes:
- `cw.cc` has initial two-AP topology plumbing: `--apStaCounts=20,40`,
  `--disableGym`, two AP nodes, AP-local STA groups, per-BSS SSIDs
  (`oscar-ap-1`, `oscar-ap-2`), fixed positions, topology logging, and OpenGym
  disabled path.
- `scenario.h` has initial AP-local STA group support for `basic`, routing each
  STA's UDP uplink to its associated AP; `convergence` is explicitly single-AP
  for v0.3.0.

Validation status:
- Not complete. `./waf build` and `./waf build --target=linear-mesh` spent
  several minutes CPU-bound in Waf before compiling the touched object; both
  were interrupted to save time.
- `./waf --run "scratch/linear-mesh/cw ..."` failed because the registered
  program name is `scratch/linear-mesh/linear-mesh`.
- Running the existing binary directly showed it was stale from 2026-08-12 and
  did not include `--disableGym`; do not treat it as validation.

Next resume step:
1. Inspect the WIP diff and compile errors if any.
2. Get Waf to rebuild `linear-mesh` or use `build/compile_commands.json` to
   diagnose direct compilation.
3. Run:
   `./waf --run "scratch/linear-mesh/linear-mesh --dryRun=true --disableGym=true --apStaCounts=20,40 --simTime=2"`
4. Only after it passes, update `ROADMAP.md`/memory bank to close v0.3.0 and
   commit a final `feat(topology): add two-ap ns-3 layout` if needed.
