# v3.2.0 Fair protocol: tooling and validation

Status: tooling DONE and validated on short runs (2026-10-28). No n >= 8 batch has been run (hybrid order chosen by the user: tooling now, the n >= 8 evaluation is spent on the v3.4.0 scenario). Plan: `docs/research-beat-oscar.md` §5 #2, #3, #8, #9 and §6.

Labels: **fact** = observed in a run or read from code; **inference** = reasoning, untested; **unknown** = needs a run.

## 1. What was added (fact)
All new behaviour is opt-in; defaults are unchanged (§3, check 2).

| Item | Where | Notes |
|---|---|---|
| `--varySeeds` | `OSCAR_multi_ap_train.py` | Episode e uses ns-3 seed `(seed+1) + 1000*e`; episode 0 is unchanged. Seeds are printed and stored as `ns3_seeds` in `config.json`. |
| `--saveActor DIR` | trainer | After training, writes `DIR/agent<i>_{actor,critic}[_optimizer]` (existing `DDPG.save`). |
| `--loadActor DIR --eval` | trainer | Frozen evaluation: loads the agents, exploration noise 0, no random warm-up, no replay add, no training. Same trace format as a training run, so `summarize_run.py` and `aggregate_bench.py` work unchanged. Each needs the other. |
| `--algo td3` | `agents/our_ddpg/TD3.py` | Subclass of `DDPG`: twin critics, policy delay 2, target noise 0.2 clipped at 0.5. Same attribute names, so the trainer's isolation checks and save/load work. Its `critic_loss` is the sum of the two MSE terms and `actor_loss` is 0 until the first delayed update, so loss columns are not comparable with DDPG. |
| `--cwMinOnly` | `cw.cc` + trainer | Multi-AP agent actions set MinCw only; MaxCw becomes `max(cw, 1023)` so BEB doubling is kept and MinCw never exceeds MaxCw at CW 1024. Default off. |
| `--alpha 0` | existing flag | Independent with a network-goodput reward (repaired baseline, idea #3). No code change; covered by the short TD3 shared `--alpha 0` run in §3. |
| `fair_protocol_v3_2_0.py` | runner | Per learned mode: train K episodes (`--varySeeds`, `--saveActor`), then evaluate the frozen policy and BEB on the same held-out python seeds (default 100-107). Resumable, one ns-3 job at a time. `--trainerArgs` goes to every job, `--learnerArgs` only to learned modes (not BEB). `manifest.csv` has the columns `aggregate_bench.py` reads; eval runs carry `--tag fz-<mode>[-td3]`; training rows go to `train_manifest.csv`. |

`cw.cc` was rebuilt (binary mtime 2026-10-27 20:14 -> 2026-10-28 08:15).

## 2. Protocol (decision)
1. Train one policy per mode for K episodes with different ns-3 seeds (`--varySeeds`).
2. Save the actors. Evaluate frozen (no noise, no training) on held-out seeds, with BEB on the same seeds, so the comparison is paired by seed.
3. Aggregate with `aggregate_bench.py <benchDir> --topo <topo>` (paired deltas with a Student-t 95 % CI).

Limits (fact): one trained policy per mode and `--trainSeed`, so policy-seed variance is not in the CI unless the runner is repeated with other `--trainSeed` values in separate `--benchDir`s. The Wilcoxon test named in the research plan is not implemented. The aggregate still uses the steps >= 300 policy window for every mode, including frozen runs and BEB.

## 3. Validation (fact, all on `2,3`, `--simTime 3 --stepTime 0.1 --historyLength 20 --obsWindow 20 --start_timesteps 10 --batch_size 8 --check`)
1. Build and regressions: `waf build --target=linear-mesh` rebuilt the binary. `--nWifi=5` dry seed 1: 10533 packets; `--apStaCounts=5,15` dry: 9000; per-AP statistics check PASS in both. Gym smoke (`baseline_v0_1_0.py --smoke`): cumulative reward 10.59458.
2. Defaults unchanged: beb, global, independent and shared, pre-change baseline traces (old binary, old trainer) against the same commands on the new code: `trace.csv` byte-identical in all four, `--check` PASS.
3. `--episodes 2 --varySeeds` (independent): PASS, 60 rows, ns-3 seeds `[1, 1001]`, the two episodes' `rx` columns differ.
4. Save then eval: `--saveActor` (2 agents), then two `--loadActor --eval --seed 100` runs PASS with byte-identical traces; ns-3 seed 101; in the eval trace the action equals `actor(state)` exactly (max difference 0) and the loss columns are all 0 (no training). Global mode save/eval also PASS.
5. `--algo td3` PASS for independent, global and shared (`--alpha 0`). `--cwMinOnly` independent PASS; with `--cwReadbackEvery 0.5`, the readback after actions shows MinCw = action and MaxCw 1023 on APs and STAs (`other=0`), e.g. `AP2 set=596/1023 ap=596/1023`; the control without the flag shows `set=596/596`.
6. Runner end to end (independent and global, `--trainEpisodes 2`, eval seeds 100 and 101, BEB): 8 of 8 jobs PASS; `aggregate_bench.py` produced the paired table (frozen modes vs BEB). These numbers come from 3 s runs and 2 seeds and are plumbing evidence, not a result.

## 4. Pilot at 20,40

Setup (fact): `fair_protocol_v3_2_0.py --topo 20,40 --modes shared --trainEpisodes 2 --evalSeeds 100 --learnerArgs "--rewardScale 100 --alpha 0"` (shared mode with the A1 settings, DDPG, simTime 15, stepTime 0.01). Training seed 0, ns-3 seeds `[1, 1001]`, 2 episodes (1766 s); frozen eval and BEB on python seed 100 (ns-3 seed 101). All three jobs `--check` PASS. Policy window = steps >= 300.

| Run (seed 100) | Aggregate Mbps | AP1 / AP2 | Jain | phy loss | Job time |
|---|---|---|---|---|---|
| BEB | 27.33 | 9.13 / 18.19 | 0.901 | 0.746 | 805 s |
| Frozen shared (A1, 2 train episodes) | 39.74 | 13.38 / 26.36 | 0.904 | 0.562 | 833 s |

- Fact (n=1, no CI possible): frozen shared minus BEB = +12.41 Mbps. Nothing is claimed beyond "the pipeline works at real scale".
- Inference, not tested: 39.74 is at the static common-CW ceiling of v3.1.0 (512,512 = 39.62 ± 0.21, seeds 0-2). This is different seeds and an unpaired comparison, so it says only that a frozen policy trained for 2 episodes can reach the ceiling region. It is not a gain over Global.
- Fact (timing, for batch estimates): one 15 s job takes about 800-880 s here (BEB 805 s, eval 833 s); one training episode about 880 s (2 episodes 1766 s). The BEB and eval jobs started from a clean runner state, so these are single measurements.
- Unknown: whether frozen eval beats Global or BEB at n >= 8; policy-seed variance (one `--trainSeed`).

Bug found and fixed during the pilot (fact): the first launch failed at the BEB job (rc=1 after 2 s) because `--trainerArgs` carried `--alpha 0` to BEB and the trainer asserts `--alpha` is only for independent/shared. The runner now has `--learnerArgs` (learned modes only, train and eval); `--trainerArgs` stays for flags every job needs. The training job was already PASS and was reused on resume; the failed row is kept in `manifest.csv` as the first line.

Batch estimate for v3.4.0 (inference from the timings above): per topology and per learned mode, train K=3 episodes ≈ 2650 s, plus 8 eval jobs ≈ 6700 s; BEB 8 jobs ≈ 6450 s. Three learned modes + BEB ≈ 3 x 9350 + 6450 ≈ 34,500 s ≈ 9.6 h per topology. Split it by mode; user pre-approved long runs for the session that wrote this, so the next session must ask again.

## 5. Committed artifacts
Run dirs (`trace.csv`, `config.json`) and logs/manifests for the 6x10 references and the 20,40 pilot, plus the pilot's saved actors (`actors/shared`), force-added with the user's approval. The toy `fair-v3.2.0-demo` runs are local only.

## 6. Next
- v3.4.0 per-AP scenario (needs the user's go-ahead for the `set_phy` / `scenario.h` change); the n >= 8 frozen-eval batches are spent there.
- The batch estimate is in §4.
