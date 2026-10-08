# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

v0.3.0 (two-AP ns-3 topology) is CLOSED (2026-10-07): merged to `main`, tagged `v0.3.0`.
**v0.4.0 per-AP statistics CLOSED (2026-10-08): merged to `main` (98bbf79), tagged `v0.4.0`, pushed to GitHub.**
**v0.5.0 per-AP CW CLOSED (2026-10-08): merged to `main`, tagged `v0.5.0`.**
**v0.6.0 multi-AP ns3-gym CLOSED (2026-10-08): merged to `main`, tagged `v0.6.0`, pushed.**
**v0.7.0 independent per-AP DDPG agents CLOSED (2026-10-08): merged to `main`, tagged `v0.7.0`, pushed.** Next: v0.8.0 W&B per-AP logging (design §7 metric names AP1/CW etc.). Trainer: `OSCAR_multi_ap_train.py --apStaCounts 2,3 --check`; writes CSV trace to results/v0.7.0-<ts>/ (no W&B yet).
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
