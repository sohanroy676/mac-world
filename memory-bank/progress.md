# Progress

<!-- Running log. Append, don't rewrite history. Newest at top.
     This tracks WORK STATUS (agent-facing, session to session).
     For the forward-looking feature plan, see ROADMAP.md instead —
     don't duplicate the full plan here, just what's actually in motion. -->

## Done

- **v3.2.0 Fair-protocol TOOLING + 6x10 refs DONE (2026-10-28, branches `docs/v3.1.0-6x10-refs`, `feature/v3.2.0-fair-protocol`; merged to dev + pushed; NOT tagged; no CI)** — 6x10 seed 0 BEB 27.78 / Global 36.11 (best static +3.61 vs Global, n=1). Trainer flags `--varySeeds/--saveActor/--loadActor/--eval/--algo td3/--cwMinOnly`, TD3 agent, `cw.cc --cwMinOnly` (rebuilt), runner `fair_protocol_v3_2_0.py`. All short-run acceptance checks PASS (defaults byte-identical). 20,40 pilot n=1: frozen shared 39.74 vs BEB 27.33. Report `docs/results/fair-protocol-v3.2.0.md`. Next: v3.4.0 scenario (ask first) with the n>=8 frozen-eval batch.
- **v3.1.0 Ceiling DONE (2026-10-28, branches `feature/v3.1.0-ceiling-results`, `docs/v3.1.0-handoff`; merged to dev + pushed, TAGGED `v3.1.0`; no CI)** — 50 static jobs PASS (20,40 diag + D1 at seeds 0-2, off-diagonal and 6x10 diag at seed 0). Best static common CW 512: 39.62 ± 0.21, +3.45 ± 6.77 vs Global (CI spans 0) -> rule not met, no headroom over Global; no per-AP split beats it. 6x10 has no paired refs here. Report `docs/results/ceiling-v3.1.0.md`, tables `docs/figures/v3.1.0/`. Run dirs (trace.csv + config.json, 50 jobs, 26 MB) and logs force-added with user approval; CHANGELOG regenerated (git-cliff reinstalled in `~/.venvs/changelog`). `sessionPrompt.md` rewritten for the next session. Next: ask milestone order (v3.4.0 first?), plan with go-ahead.
- **v3.1.0 PARTIAL + HANDOFF (2026-10-27, branch `feature/v3.1.0-ceiling`, merged into `dev`, pushed; no tag)** — `--mode static` + `cw.cc` static-CW fix + `ceiling_sweep_v3_1_0.py`; validated (BEB/Global traces byte-identical, static CW 32/512 held). Pilot 4/10 at 20,40 seed 0: CW 32/64/128/256 = 12.80/19.66/30.25/37.75 Mbps (n=1; refs BEB 27.30 +- 0.63, Global 36.17 +- 6.95). Parallel sweep lanes failed (cause unknown); run serially. Continue on another laptop with `sessionPrompt.md`. Report `docs/results/ceiling-v3.1.0.md`.
- **Workflow change + v3.1.0 started (2026-10-27, branch `docs/workflow-dev-branch`)** — git rules changed: `main` frozen; long-lived `dev` (created from main, pushed); work branches from `dev`, merged `--no-ff` into `dev`, both pushed under standing approval; still ask for force-push/rebase/reset --hard/deletes/tags/anything on main. Research plan `docs/research-beat-oscar.md` adopted (v3.1.0-v3.5.0 in ROADMAP). v3.1.0 ceiling sweep in progress (staged: pilot first, ask before the rest).
- **Docs restructure + cleanup (2026-10-27, merged to main c866ac9 + pushed; no tag)** — docs/ grouped into topic folders + index, report §20.4 + 5 refs, stale statuses fixed, CHANGELOG via git-cliff, 2 unused names removed. No ns-3 run, no rebuild. Open: 5 `[REF:]`, oscar-baseline-metrics header, single-AP vs BEB check.
- **A1 seeds 1-2 (2026-10-27, branch `docs/a1-seeds`, merged to main 76cedcc + pushed; no tag)** — A1 at 20,40 n=3 all `--check` PASS: 38.48 ± 2.64 Mbps, vs Global +6.9 ± 26.7 % (CI spans 0). No code change, no rebuild. `docs/results/improvement-v3.0.0.md` §5/§8/§9 and `docs/figures/v3.0.0/ablation-20-40/` updated. v3.0.0 itself is pushed + tagged.
- **Beat Global-CW (2026-10-26, merged to main b32e296, NOT pushed/tagged; ablation/3-seed follow-up on `docs/v3-ablations`)** — trainer flags `--mode shared/--obs hist/--alpha/--rewardScale/--tag`; V1-V5 screen, 3 seeds at 20,40, stress 5,55 and 5,5,5,45 (3 seeds Global/V5), 6x10 seed 0, ablations A1/A2 (seed 0). V5 = Global-level, no proven gain, CWs do not separate. `docs/results/improvement-v3.0.0.md`, ADR-0004 (ADR-0003 is the central critic). Open: 3 seeds of A1.
- **W&B sync + root README (2026-10-20, branch `docs/wandb-sync`, committed, NOT merged/pushed/tagged)** — 81 final runs online in `contention_window` (renamed + tagged), introspection workaround for wandb 0.18.7 documented in final-results §5; new root `README.md`. Open: references, report/deck review, title slide.
- **Optional follow-ups (2026-10-20, merged to main + pushed, TAGGED `v2.7.0`; no CI)** — inactive STAs at 20,40 identified (robustness §F.5b), opengym provenance resolved (final-audit §3), BEB/global seeds 1-2 and central x10/x30 at 22x10 all PASS (central-eval seventh follow-up: BEB mean 19.0, global 23.1 ± 12, central x30 38.0 s0). CHANGELOG blocked (git-cliff via Windows rejects the WSL repo).
- **Independent mode at 22x10 (2026-10-20, branch `feature/independent-22x10`, committed, NOT merged/tagged)** — seeds 0-2, 3/3 `--check` PASS (3498-3635 s): last-300-step Mbps 8.2 / 12.7 / 10.5 (mean 10.5), Jain 0.55-0.65, min AP 0.09-0.28; below BEB s0 18.0 in all seeds, about level with global s0 10.8. BEB/global still n=1. Docs `docs/results/central-eval-v1.9.0.md` sixth follow-up. Raw dirs local `results/bench-indep-22x10`, `-s12`. Docs only, no code/binary change.
- **Central reward-scale ablation (2026-10-20, merged to main + pushed, TAGGED `v2.6.0`; no CI)** — 22x10 s0: x3.67 still collapses (3.1 Mbps), x100 does not (38.0, Jain 0.98); n=1; x100 seeds 1-2, BEB/global refs at 22x10 and x100 at 4..40 added (fifth follow-up in central-eval doc).
- **Traffic-start + central-collapse session CLOSED (2026-10-19, merged to main + pushed, TAGGED `v2.5.2`; no CI)** — see activeContext HANDOFF.
- **Central collapse follow-up (2026-10-19)** — central 6x10 on fixed binary, 3/3 PASS, no collapse (30.05 ± 13.49); central 4..40 s0 on fixed binary still collapses (1.62 Mbps, n=1): CW-start bug and N alone ruled out; 22x10 equal split also collapses (2.15 Mbps, n=1): unequal split ruled out; STA count / reward scale open. `docs/results/central-eval-v1.9.0.md` follow-up.

- **Traffic-start/association dry check (2026-10-19)** — 7 BEB dry runs (n=1): final-set topologies associate by 1.12 s at t=0 start; full-size 4..40 passes with `--trafficStart=1`. Then 6x10 rerun with `--trafficStart 1` (9/9 PASS): global unchanged, independent mean 14.99 -> 20.37 (CI wide). Docs only (`docs/results/robustness-v2.0.0.md` §G.5, §G.6).

- **Active-sink count CLOSED (2026-10-19, merged to main + pushed, TAGGED `v2.5.1`; no CI)** — 20,40 seed 0, 3 modes: 19/20 + 39/40 in every mode, traces identical to benchmark runs. No code change. `docs/results/robustness-v2.0.0.md` §F.5.

- **v2.5.0 final audit CLOSED (2026-10-19, merged to main + pushed, TAGGED `v2.5.0`; no CI)** — 26-item checklist in `docs/reports/final-audit-v2.5.0.md`: Impl 9/10 PASS, Eval 7/8 PASS, Docs 4/8 PASS (3 partial, references FAIL). Five short reruns PASS; upstream import diffed against pristine ns-3.29 and ns3-gym. No code change.

- **v2.4.0 presentation CLOSED (2026-10-19, merged to main + pushed, TAGGED `v2.4.0`; no CI)** — 14-slide slides artifact from committed report/figures only, `docs/reports/presentation-v2.4.0.md` with demo script; one short demo rehearsal (32.7 s, PASS). No code change, no benchmark run.

- **v2.3.0 technical report CLOSED (2026-10-19, merged to main + pushed, TAGGED `v2.3.0`; no CI)** — `docs/reports/technical-report-v2.3.0.md` follows the 26-section roadmap structure, numbers copied from v2.2.0 tables, inherited/new labels, 21 `[REF:]` placeholders awaiting user references. No runs, no code change.

- **v2.2.0 final results CLOSED (2026-10-19, merged to main + pushed, TAGGED `v2.2.0`; no CI)** — analysis only from the 81 fixed-binary runs; new reward/fairness plots, per-seed and time-series CSVs, fixed60 scaling preset, load sweep. Regression checks identical to committed tables. W&B sync deferred, raw data local. `docs/results/final-results-v2.2.0.md`. v2.1.0 tagged + pushed.

- **v2.1.0 reproducibility and cleanup CLOSED (2026-10-19, branch `feature/v2.1.0-reproducibility`, merged to main + pushed, TAGGED `v2.1.0`; no CI)** — W&B names/tags, git_rev, trafficStart/staMaxMissedBeacons pass-through, runner flags, dependency doc. Defaults unchanged (byte-identical traces, 4 modes); seed and reset verified on short runs. No cw.cc change. `docs/reference/reproducibility-v2.1.0.md`. v2.0.0 tagged + pushed.

- **v2.0.0 robustness CLOSED (2026-10-19, branch `feature/v2.0.0-robustness`, merged to main + pushed, TAGGED `v2.0.0`; no CI configured)** — A fixed-total-STA, B imbalance, C traffic load, D association diagnostic, all rerun on the CW-start-fixed binary (63/63 PASS). Global +30..33 % vs BEB everywhere (neutral at 0.5 Mbps); independent negative at N>=4. Fixed multi-AP agent CW 0/0 start (1306e37). Large-N association failure = traffic from t=0 + MaxMissedBeacons. `docs/results/robustness-v2.0.0.md`, `docs/figures/v2.0.0/`. v1.9.0 tagged + pushed.

- **v1.9.0 central critic evaluation DONE (2026-10-17, branch `feature/v1.9.0-central-eval`, NOT merged/tagged)** — central at N=4 and N=10, seeds 0-2, 6/6 PASS. Decision rule not met (N=10 central vs independent -5.80 ± 10.48 Mbps, CI includes 0, 0/3 above; central ~3.2 Mbps). Optional/negative result; core unaffected; next v2.x. `docs/results/central-eval-v1.9.0.md`, `docs/figures/v1.9.0/`. v1.8.0 tagged + pushed.

- **v1.8.0 central critic PROTOTYPE (2026-10-16, branch `feature/v1.8.0-central-critic-prototype`, code 3a292d0, NOT merged/tagged)** — `--mode central`: N local actors + one shared `Critic(N,N)` on the global reward, joint replay, MADDPG actor update; `--check` extended (joint row, r_g, actor input isolation, finite losses/Q). Python only, no rebuild. 2,3 short + full and 20,40 short (30 steps) PASS; independent/global short traces identical to pre-change. Merged to main + pushed. v1.7.0 tagged + pushed. `docs/design/central-critic-v1.8.0.md`.

- **v1.7.0 central critic DESIGN written (2026-10-16, branch `feature/v1.7.0-central-critic-design`, merged to main + pushed, NOT tagged)** — `docs/design/central-critic-v1.7.0.md` + ADR-0003 (Proposed). User decisions: one shared critic on global reward; spec + timeboxed build (v1.8 <= 1 session, v1.9 small eval; else optional/negative result). No code, no runs. v1.6.0 TAGGED + pushed.

- **v1.6.0 scaling analysis DONE (2026-10-16, branch `feature/v1.6.0-scaling-analysis`, merged to main + pushed, NOT tagged; raw traces force-committed)** — `scaling_analysis.py` + `docs/results/scaling-v1.6.0.md` + `docs/figures/v1.6.0/` (table, per-seed CSV, 10 figures). Recomputed from raw traces N=2 (20,40 n=5), 4, 6, 8, 10 (n=3); cross-check vs per-version tables PASS. No new runs. v1.5.0 tagged + pushed. Assoc cause deferred.

- **v1.5.0 10 APs DONE at n=3 (2026-10-16, branch `feature/v1.5.0-ten-aps`, merged to main + pushed, NOT tagged)** — 4,8,...,40 (220 STAs), seeds 0-2, 9/9 PASS, no code change. BEB 19.24 ± 1.85, global 27.04 ± 15.20 (+41.0 ± 83.9 %, CI includes 0, above BEB 3/3), independent 9.00 ± 6.16 (-53.5 ± 27.6 %, CI excludes 0, below BEB 3/3). Runs 3223-4315 s. Full-size dry association check FAILS (late association, AP10 deassoc bursts; cause unproven; recorded as open). Trainer full check 13:41, 478 MB. v1.4.0 tagged + pushed. `docs/results/scaling-v1.5.0.md`, `docs/figures/v1.5.0/`.

- **v1.4.0 8 APs DONE at n=3 (2026-10-16, branch `feature/v1.4.0-eight-aps`, merged to main + pushed, NOT tagged)** — 5,10,15,20,25,30,35,40 (180 STAs), seeds 0-2, 9/9 PASS, no code change. BEB 20.05 ± 0.94, global 27.99 ± 17.20 (+40.1 ± 92.7 %, CI includes 0, above BEB 3/3 seeds), independent 12.54 ± 18.74 (-37.1 ± 96.8 %, CI includes 0; seed 1 21.1, seeds 0,2 6.8/9.7). Runs 2733-3796 s. Full-size trainer check 11:56, 367 MB. v1.3.0 tagged + pushed. `docs/results/scaling-v1.4.0.md`, `docs/figures/v1.4.0/`.

- **v1.3.0 6 APs DONE at n=3 (2026-10-15, branch `feature/v1.3.0-six-aps`, merged to main + pushed, NOT tagged)** — 5,10,15,20,25,30, seeds 0-2, 9/9 PASS. BEB 23.83 ± 1.15, global 32.53 ± 12.48 (+36.4 ± 49.3 %, CI includes 0, 3/3 seeds above BEB), independent 18.72 ± 19.75 (-21.6 ± 81.0 %, bimodal). No code change. Runs 1514-1676 s (independent s1 2617 s). Full-size trainer check 6:19, 365 MB. `docs/results/scaling-v1.3.0.md`, `docs/figures/v1.3.0{,-b2}/`. v1.2.0 tagged + pushed.

- **v1.2.0 4-AP EXTENDED to n=3 (2026-10-15, branch `feature/v1.2.0-benchmarks-b2`, NOT merged/tagged)** — seeds 1,2 PASS (6 runs, 716-850 s each). BEB 28.63 ± 2.26, global 37.29 ± 4.81 (+30.5 ± 27.2 %, CI excludes 0), independent 23.27 ± 13.19 (-18.6 ± 47.6 %, CI includes 0). `docs/figures/v1.2.0-b2/`, `docs/results/scaling-v1.2.0.md` §2b.

- **v1.2.0 4-AP validated (2026-10-15, merged to main + pushed, NOT tagged)** — dry/CW/gym/trainer checks PASS at 2,3,4,5 and 5,10,15,20; long runs seed 0 PASS (BEB 27.64, global 39.53, independent 23.34 Mbps; n=1). `docs/results/scaling-v1.2.0.md`. v1.1.0 tagged + pushed.

- **v1.1.0 20,40 EXTENDED to n=5 (2026-10-15, branch `feature/v1.1.0-benchmarks-b7`, NOT merged/tagged)** — seeds 3,4 PASS. BEB 27.96 ± 1.26, global 36.89 ± 3.62 (+31.9 ± 11.8 %, CI excludes 0), independent 25.27 ± 8.21 (-9.3 ± 31.0 %). `docs/figures/v1.1.0-b5/`.

- **v1.1.0 ALL RUNS DONE (2026-10-14, branch `feature/v1.1.0-benchmarks-b6`, NOT merged/tagged)** — 20,40 9/9 PASS. BEB 27.30 ± 0.63, global 35.61 ± 8.13 (+30.5 ± 32.3 %), independent 28.57 ± 9.37 (+4.6 ± 33.8 %), paired CIs include 0. Only CI-supported gain: global +26 % at 20,20. Independent throughput drifts down late in run. `docs/figures/v1.1.0-b4/`, `docs/results/benchmark-v1.1.0.md` §4c, §5.

- **v1.1.0 batch 3 PARTIAL 5/9 (2026-10-14, branch `feature/v1.1.0-benchmarks-b5`, NOT tagged)** — 20,40: BEB 27.16 ± 1.05 (n=2), global 36.66 ± 34.66 (n=2; paired +35 ± 133 %), independent 32.41 (n=1). No 20,40 claim supportable yet. 4 runs left. `docs/figures/v1.1.0-b3/`, `docs/results/benchmark-v1.1.0.md` §4c, §5.

- **v1.1.0 batch 3 PARTIAL (2026-10-13, branch `feature/v1.1.0-benchmarks-b4`, NOT tagged)** — 20,40 beb seed 0 PASS (27.25 Mbps, Jain 0.891, ~42 min); global s0 killed by terminal restart; 8 runs remain. 20,40 BEB also shows the t=1.144 s deassociation. Data: `docs/figures/v1.1.0-b3-partial/`. `docs/results/benchmark-v1.1.0.md` §4c.

- **v1.1.0 batch 2 DONE (2026-10-13, branch `feature/v1.1.0-benchmarks-b3`, NOT tagged)** — 20,20 9/9 PASS (3 modes x 3 seeds). Policy-window Mbps: BEB 30.10 ± 0.20, global 37.93 ± 4.17 (+26.0 ± 13.1 %), independent 30.19 ± 21.60 (+0.2 ± 71.1 %). Figures inspected. Trainer check fixed to mirror cw.cc float32 `4+a` (2/3000 rows had CW 139 vs 140; cw.cc unchanged). Batch 3 (20,40) pending. `docs/results/benchmark-v1.1.0.md` §4b, `docs/figures/v1.1.0-b2/`.

- **v1.1.0 batch 2 PARTIAL (2026-10-12, branch `feature/v1.1.0-benchmarks-b2`, second laptop, NOT tagged)** — 20,20 seed 0 (3 modes) + seed 1 BEB PASS (~19 min each); seed 1 global/independent, seed 2, batch 3 pending. Aggregated to `docs/figures/v1.1.0-b2/`. Seed-0 aggregate: BEB 30.06 (n=2 seeds incl. s1), global 38.20, independent 30.41 Mbps (n=1 each). Binary rebuilt; regressions hold. Details `docs/results/benchmark-v1.1.0.md` §4b.

- **v1.1.0 IN PROGRESS (2026-10-09, branch `feature/v1.1.0-benchmarks`, merged to main + pushed, NOT tagged)** — trainer `--mode independent|global|beb`; `benchmark_v1_1_0.py` (resumable runner), `aggregate_bench.py` (95% CI, paired delta); `summarize_run.py` has `summarize()`. Found + fixed seed bug: `--seed`/`--rng` had no effect (SetSeed after node creation); fixed in `cw.cc`, rebuilt, regressions hold (10533, 9000, smoke 10.59458). Batch 1 done (18/18 PASS): 2,3 BEB 40.47 / global 40.41 / indep 39.98; 5,15 34.48 / 37.95 / 33.57 Mbps; all paired CIs include 0. Batches 2 (20,20) and 3 (20,40) NOT run. Details `docs/results/benchmark-v1.1.0.md`.

- **v1.0.0 CLOSED (closeout 2026-10-08, branch `fix/v1.0.0-closeout`)** — audit vs roadmap: no required item missing in code. Reruns on rebuilt binary: 2,3 trained 40.4 Mbps (doc 40.3), 5,15 seed-pinned trained 39.6 vs BEB 36.8 (+7.5%, AP1 ~83%), BEB 5,15 reproduced exactly; v0.5 CW check + v0.6 gym tests PASS. Docs: README multi-AP section, CLAUDE.md roadmap line, reward-scale note (core-v1.0.0 §5). CHANGELOG not regenerated (`conventional-changelog` fails in WSL: `node: not found`). Next: v1.1.0.

- **v1.0.0 long runs done (2026-10-08, branch `feature/v1.0.0-long-runs`, not merged; tag still pending user approval)** — binary rebuilt (regressions: smoke 10.59458, `--nWifi=5` dry 10533 pkts). BEB vs trained (policy phase, seed 0/ns-3 seed 1): 20,20 32.2 vs 30.0 Mbps (no gain); 20,40 29.2 vs 32.3 Mbps, Jain 0.886 -> 0.972. Both trained `--check` PASS. 20,40 trained log: 6 STAs deassoc from AP2 at t=1.144 s, back by 1.31 s (cause unproven; BEB not checked). Each run took ~13-18 min. Details `docs/results/core-v1.0.0.md` §3.

- **v1.0.0 implemented (merged to main + pushed 2026-10-08; NOT tagged — tag after 20,20/20,40 long runs)** — trainer passes ns-3 seed (py seed+1; ns-3 rejects 0); new `baseline_beb.py`. Two 2,3 long runs seed 0: trace.csv identical (all 17 cols). BEB vs trained: 2,3 43.5 vs 40.3 Mbps; 5,15 36.8 vs 38.4 (trained split inverted, AP1 ~80%). Regressions unchanged. 20,20/20,40 + global-CW baseline deferred to v1.1. Details `docs/results/core-v1.0.0.md`.

- **v0.9.0 CLOSED (tag `v0.9.0`, 2026-10-08)** — Tests A–F PASS on short runs (details `docs/results/validation-v0.9.0.md`).
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
- **v0.1.0 CLOSED (tag `v0.1.0`)** — baseline freeze: non-behavioral runner `baseline_v0_1_0.py`, `.gitignore` for CW artifacts, `docs/results/baseline-v0.1.0.md`, smoke-validated pipeline, episode-1 baseline numbers (nWifi=40: CW mean 196.9, throughput ≈34 Mbps, loss ratio 0.63) — 2026-09-16
- Full-run artifact archive `results/baseline-v0.1.0-full-partial-20260916/` (CW_data_bk.csv + run-7y4kp9yr.wandb + summary.json) — run stopped by user decision during episode 2; redo anytime with one command

## In progress

- v0.9.0 validation (next, not started): 2-AP runs with different STA distributions (e.g. 5,15 / 20,40), longer training, compare vs baseline.
