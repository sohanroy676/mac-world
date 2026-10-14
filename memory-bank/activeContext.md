# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

**2026-10-14 (evening) handoff:** v1.1.0 ALL 36 runs PASS (20,40 batch 3 complete, 9/9), aggregated to `docs/figures/v1.1.0-b4/`, figures inspected, `docs/benchmark-v1.1.0.md` §4c + §5 final. 20,40 (n=3): BEB 27.30, global 35.61 (paired +30.5 ± 32.3 %, CI includes 0), independent 28.57 (+4.6 ± 33.8 %). Only CI-supported claim: global-CW +26 % at 20,20. t=1.144 s deassoc at 20,40: beb 1/0/0, global 7/14/4, independent 6/12/0; cause unproven (test in §4c). Branch `feature/v1.1.0-benchmarks-b6`, not merged/pushed. Merged to main + pushed (not tagged). Raw `results/` stay gitignored (60 MB local only; aggregated tables, figures, manifest are committed). Next: user approval to tag `v1.1.0` (or run more 20,40 seeds first), then v1.2.0 (4 APs).

**2026-10-14 handoff:** v1.1.0 batch 3 (20,40) PARTIAL, 5 of 9 runs PASS (beb s0 s1, global s0 s1, independent s0); aggregated to `docs/figures/v1.1.0-b3/`, figures inspected, `docs/benchmark-v1.1.0.md` §4c + provisional conclusion written. Runs take only 16-21 min each now. Remaining 4: independent s1, beb s2, global s2, independent s2 (~70-85 min): `cd ns-3.29/scratch/linear-mesh && ../../venv/bin/python benchmark_v1_1_0.py --topos 20,40 --seeds 1 2 --benchDir results/bench-v1.1.0` (ask first; resumes PASS rows; one job at a time; stop it by killing the trainer `OSCAR_multi_ap_train.py` too, not only the runner; `pkill -f` inside a watcher kills itself). Then aggregate to NEW dir `docs/figures/v1.1.0-b4`, update §4c, close/tag v1.1.0 only with approval. t=1.144 s deassoc at 20,40: beb 1/0, global 7/14, independent 6; always re-associates; cause unproven (§4c). `results/` is gitignored; manifest copied to the figures dir (16 rows).

**2026-10-13 (second laptop, evening) handoff:** v1.1.0 batch 3 (20,40) PARTIAL: only `beb` seed 0 PASS (27.25 Mbps policy window, Jain 0.891, 2500 s). A terminal restart killed the background job during `global` seed 0 (lost; not in manifest). 8 runs left: beb s1 s2, global s0 s1 s2, independent s0 s1 s2; ~42 min each (~5.5 h; 60 STAs is ~2x the 20,20 time). Partial data in `docs/figures/v1.1.0-b3-partial/` (final aggregate must go to NEW dir `docs/figures/v1.1.0-b3`). Deassoc at t=1.144 s ALSO occurs in 20,40 BEB (1 event, nodeId 42), so the earlier "trained-only" hint is falsified; cause still unproven. `results/` (gitignored) on this laptop holds the 20,20 and 20,40-beb-s0 raw dirs plus manifest (12 rows). Resume: `cd ns-3.29/scratch/linear-mesh && ../../venv/bin/python benchmark_v1_1_0.py --topos 20,40 --seeds 0 1 2 --benchDir results/bench-v1.1.0` (resumes PASS rows; ask first; launch from a terminal that will not be restarted). Then aggregate, look at figures, finish `docs/benchmark-v1.1.0.md` §4c + conclusion, tag only with approval.

**2026-10-13 (second laptop) handoff:** v1.1.0 batch 2 (20,20) DONE, 9/9 PASS, aggregated + figures inspected (`docs/figures/v1.1.0-b2/`, `docs/benchmark-v1.1.0.md` §4b): BEB 30.10, global 37.93 (+26.0 ± 13.1 % paired, CI excludes 0), independent 30.19 ± 21.6 (seed spread 21.4-38.8). Merged to main + pushed, NOT tagged. Trainer `--check` expected-CW now mirrors cw.cc float32 `4+a` (seed 2 global had failed on 139 vs 140; check-only fix, cw.cc/binary unchanged). Remaining: batch 3 (20,40; 9 runs, ask first, ~19 min each): `cd ns-3.29/scratch/linear-mesh && ../../venv/bin/python benchmark_v1_1_0.py --topos 20,40 --seeds 0 1 2 --benchDir results/bench-v1.1.0`; aggregate to NEW dir `docs/figures/v1.1.0-b3`; check 20,40 BEB logs for t=1.144 s deassoc; write §4c + conclusion; tag only with approval. Note: `results/` lives under `ns-3.29/scratch/linear-mesh/results/` (gitignored); on a new machine it is empty, so batch 3 needs only its own runs. Poller tip: `pgrep -f` self-matches inside a bash loop, poll the manifest line count instead.

**2026-10-12 (second laptop):** v1.1.0 batch 2 (20,20) PARTIAL. Done (PASS): seed 0 beb/global/independent, seed 1 beb. Seed 1 global was running at handoff (may have been lost; manifest is authoritative); seed 1 independent + seed 2 x3 not run; batch 3 (20,40) not run. Batch 1 raw traces stay on the first laptop (results/ gitignored; decision: skip). Outputs in `docs/figures/v1.1.0-b2/` (separate from batch 1 `docs/figures/v1.1.0/`). Binary rebuilt, regressions hold. Resume: `cd ns-3.29/scratch/linear-mesh && ../../venv/bin/python benchmark_v1_1_0.py --topos 20,20 --seeds 1 2 --benchDir results/bench-v1.1.0` (ask first; ~19 min/run here; resumes PASS rows). Interim: global seed 0 +27% vs BEB (n=1), independent +1%. Figures not inspected. See `docs/benchmark-v1.1.0.md` §4b.

**2026-10-09:** v1.1.0 in progress (merged to main, pushed, NOT tagged). Done: tooling, seed fix, batch 1 (2,3 + 5,15). Next: batch 2 (20,20) then batch 3 (20,40) via `benchmark_v1_1_0.py --benchDir results/bench-v1.1.0` (resumes; ask before each; one ns-3 job at a time; ~2.5 h+ each, WSL timing erratic). Then aggregate, look at figures, finish `docs/benchmark-v1.1.0.md`, close/tag only with approval. Note `results/bench-v1.1.0/` is gitignored; its manifest is copied to `docs/figures/v1.1.0/manifest.csv`.

**2026-10-08 closeout:** v1.0.0 closed (merged, tagged `v1.0.0`, pushed). Next: v1.1.0 baseline benchmarking (global-CW OSCAR baseline, multi-seed, per-step BEB window). Open: reward scale ~0.003-0.07 (see core-v1.0.0 §5), 20,40 deassoc cause, W&B online sync, CHANGELOG generator needs node on PATH in WSL.

**2026-10-08 update:** 20,20 and 20,40 long runs DONE on branch `feature/v1.0.0-long-runs` (results in `docs/core-v1.0.0.md` §3; trained ~ BEB at 20,20, +11% at 20,40). Awaiting user approval to merge, push, and tag `v1.0.0`. Local clone only has tag v0.3.0 (origin has v0.4.0-v0.9.0; not fetched). Then v1.1.0.

**v1.0.0 implemented, merged to `main` and pushed (2026-10-08) but NOT TAGGED.** User decision: run the 20,20 / 20,40 long trainings in a new session first (ask before starting; one ns-3 job at a time; 2 s dry run alone >10 min), add results to `docs/core-v1.0.0.md`, then tag `v1.0.0` only with user approval. After that: v1.1.0 (global-CW OSCAR baseline, multi-seed). BEB baseline: `baseline_beb.py --apStaCounts 20,20`. Trainer seed: ns-3 seed = python seed + 1.

**v0.9.0 validation CLOSED (2026-10-08): merged to `main`, tagged `v0.9.0`, pushed.** Next: v1.0.0 core milestone (bundle + 2-AP results + baseline comparison); optionally the 20,20 / 20,40 long runs first. Run one ns-3 job at a time (trainer leftover-process check false-positives).

v0.3.0 (two-AP ns-3 topology) is CLOSED (2026-10-07): merged to `main`, tagged `v0.3.0`.
**v0.4.0 per-AP statistics CLOSED (2026-10-08): merged to `main` (98bbf79), tagged `v0.4.0`, pushed to GitHub.**
**v0.5.0 per-AP CW CLOSED (2026-10-08): merged to `main`, tagged `v0.5.0`.**
**v0.6.0 multi-AP ns3-gym CLOSED (2026-10-08): merged to `main`, tagged `v0.6.0`, pushed.**
**v0.7.0 independent per-AP DDPG agents CLOSED (2026-10-08): merged to `main`, tagged `v0.7.0`, pushed.** **v0.8.0 W&B per-AP logging CLOSED (2026-10-08): merged to `main`, tagged `v0.8.0`, pushed. Next: v0.9.0 validation.** Run: `OSCAR_multi_ap_train.py --apStaCounts 2,3 --check` (offline W&B; `.wandb` copied to results/multi-ap-<ts>/). Trainer: `OSCAR_multi_ap_train.py --apStaCounts 2,3 --check`; writes CSV trace to results/v0.7.0-<ts>/ (no W&B yet).
v0.6.0 interface (N>1 APs only; N==1 path untouched): obs Box [N,H] flat, row i = AP i loss history (newest first);
action Box [N] (exponent domain, CW=2^(a+4) clamped 16..1024, size mismatch -> return false); scalar reward = mean of
per-AP rewards; per-AP rewards in extraInfo 5th `|` field `cwSet,cwReadbackAp,reward,loss,rxDelta,phyTxDelta;...`.
loss_i=(txΔ-rxΔ)/txΔ from g_apPhyTxPkt/g_apRxPkt (0 if no tx); reward_i=rxΔ*1464*8/(offeredLoad*1e6*stas_i*envStep) clamped [0,1].
Helpers: `multi_ap.py` (reshape_obs, parse_ap_info); test: `test_multi_ap_gym.py [--staCounts 5,15 --phases "2,5;6,0"]`.
Known for v0.7: EnvWrapper.observation_space parses repr and breaks on 2-D shapes; EnvWrapper.step feeds one env, so use
np.array([[a1,a2]]) with 1 env. Multi-AP gym is `basic` scenario only (stas_i fixed for reward).

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

Start v0.6.0 multi-AP ns3-gym: per-AP observations/actions/rewards through ns3-gym; use `setApCw(ap, cw, cw)` in cw.cc for per-AP actions (today MyExecuteActions applies one global action to all APs). Per-AP counters from v0.4.0 (g_apRxPkt etc.) feed per-AP obs/reward.

**v0.5.0 finding (verified in ns-3.29 source + readback):** STAs overwrite their BE MinCw/MaxCw from their own AP's
beacon/assoc-resp EDCA set, encoded 2^floor(log2(CW+1))-1 (16->15, 32->31, 1024->1023). Readback confirms STAs read the
rounded value after warm-up; APs keep the exact value. Pre-existing (v0.1 too); per-AP isolation holds (STAs only take
beacons of their own BSSID). Decision: accept + document, no upstream patch. Single-AP baseline unchanged.

(Historical, superseded by the above:)

Start **v0.5.0
per-AP CW** (branch `feature/v0.5.0-per-ap-cw`): replace the wildcard `Config::Set` (cw.cc, set_nodes + MyExecuteActions) with
per-node paths for AP_i + its STAs; verify by attribute readback per AP.

v0.4.0 facts (cw.cc only, no scenario.h change): per-AP rx via UdpServer "Rx" bound callbacks,
per-AP PHY tx (PhyTxBegin on AP_i + its STAs, incl. beacons/ACKs) and per-AP app tx (OnOff "Tx"),
end-of-run `Per-AP statistics check: PASS/FAIL`. Globals/observation/reward untouched (v0.6).
Reported `throughput` uses elapsed sim time (~3.21 s at simTime=2, incl. warm-up), so it differs from
the legacy `Throughput:` line (divides by simulationTime). loss_app ~0.95-0.99 because offered load
saturates (app tx counts packets generated, incl. MAC-queue drops); loss_phy matches OSCAR's definition.
Observed (not investigated): 20,40 run showed AP2 deassoc=1 (association still PASS).

Venv repair (user-approved 2026-10-08): venv lacked matplotlib/comet_ml/pandas; installed
matplotlib==3.5.3, comet_ml==3.52.1, pandas==1.3.5 (audit versions). Core pins unchanged.
Gym smoke regression PASSES (cumulative reward 10.59458 before and after the v0.4.0 change).
Unconfirmed: smoke progress bar shows MB sent/Speed 0.
Repo-local git identity set to Sohan Roy Talari <sohanroy676@gmail.com> (user-approved).

Validation notes for later milestones:
- Run binary directly: `LD_LIBRARY_PATH=ns-3.29/build/lib ns-3.29/build/scratch/linear-mesh/linear-mesh <args>`
  from a scratch dir (writes `cw.csv` to cwd). A 2-AP, 60-STA, simTime=2 run takes ~2.5 min CPU.
- FlowMonitor rx counts only cover the post-warmup window and disagree with the sink
  handler (e.g. 0 vs ~9000 pkts) — use UdpServer counts / handler, not FlowMonitor rx.
- Single /24 subnet fits ~253 nodes; widen before scaling to 10 APs.
- CW is still a wildcard `Config::Set` over all nodes (v0.5 replaces it).
