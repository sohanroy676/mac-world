# Roadmap

- Read the `docs/planning/detailed_roadmap.md` for a more detailed roadmap of the project.

## Now — Core Two-AP Implementation

### v0.1.0 — Baseline
- Freeze and reproduce the existing single-AP OSCAR baseline.
- Status: ✅ CLOSED 2026-09-16 — tag `v0.1.0` on `major-project`. Freeze runner
  + docs + smoke validation + episode-1 baseline numbers recorded (full
  3-episode run stopped by user decision during episode 2; redo anytime with
  one command). See `docs/results/baseline-v0.1.0.md`.

### v0.2.0 — Design
- Define multi-AP topology, observations, actions, rewards, statistics, and ns3-gym interface.
- Status: ✅ CLOSED 2026-09-16 — design contract accepted with one shared
  ns-3 process, two APs by default, per-AP DDPG agents, AP-local observation/
  reward/CW/statistics, sequential joint stepping, and no central critic in the
  core v1 path. See `docs/design/multi-ap-design-v0.2.0.md` and ADR-0002.

### v0.3.0 — Two APs
- Create two APs in one ns-3 simulation.
- Support different station counts per AP.
- Status: ✅ CLOSED 2026-10-07 — tag `v0.3.0` on `main`. 2 APs / unequal
  STAs in one ns-3 sim, per-STA association and per-AP sink traffic verified, no RL dependency.

### v0.4.0 — Per-AP Statistics
- Separate throughput, packet, loss/collision, reward, and other required measurements by AP.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.4.0` on `main`. Per-AP rx/PHY-tx/app-tx, loss, throughput, totals and Jain; validated on 2,3 / 5,15 / 20,40 and single-AP.

### v0.5.0 — AP-Specific CW
- Give each AP independent CW control.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.5.0` on `main`. Per-AP CW via per-node paths + `--apCws` + readback check; validated on 5,15 and single-AP.

### v0.6.0 — Multi-AP ns3-gym
- Support multiple AP observations, actions, and rewards through the Python/ns-3 interface.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.6.0` on `main`. Joint per-AP obs/action/reward via ns3-gym; validated on 2,3 / 5,15 and single-AP.

### v0.7.0 — Independent Agents
- Add one independent AP-level DDPG Actor-Critic agent per AP.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.7.0` on `main`. Independent per-AP DDPG agents; `OSCAR_multi_ap_train.py --check` PASS on 2,3; single-AP unchanged.

### v0.8.0 — W&B
- Add clear per-AP and aggregate experiment logging.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.8.0` on `main`. Metrics: `APi/{CW,Reward,Throughput,LossRatio,Observation,ActorLoss,CriticLoss,CumulativeReward}`, `Global/{Throughput,Fairness,LossRatio,CumulativeReward}`, `Episode`, `Step` (design §7 names; roadmap's `LossRate`/`AggregateThroughput` map to `LossRatio`/`Throughput`). Throughput = rx·1464·8/(stepTime·1e6) Mbps; Fairness = Jain over per-AP throughput computed in Python (ns-3 jain field not used); Global/LossRatio = Σ(tx−rx)/Σtx.

### v0.9.0 — Validation
- Validate the complete two-AP system with different station distributions.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.9.0` on `main`. Tests A–F PASS (short runs); long training done for 2,3 and 5,15 only; 20,20 / 20,40 long runs deferred. See `docs/results/validation-v0.9.0.md`.

### v1.0.0 — Core Milestone
- Working, repeatable two-AP multi-agent OSCAR implementation.
- Status: ✅ CLOSED 2026-10-08; tag `v1.0.0` (closeout done; see core-v1.0.0). 20,20/20,40 long runs done (20,20 trained 30.0 vs BEB 32.2 Mbps; 20,40 trained 32.3 vs BEB 29.2). Seed-pinned identical-rerun check + BEB baseline comparison on 2,3, 5,15, 20,20, 20,40. See `docs/results/core-v1.0.0.md`.

## Next — Scaling and Benchmarking

### v1.1.0
- Benchmark against relevant baseline configurations.
- Status: 🔄 ALL RUNS DONE 2026-10-15, awaiting close/tag approval. 42/42 benchmark runs PASS (20,40 extended to n=5). CI-supported gains: global-CW +26.0 ± 13.1 % vs BEB at 20,20 and +31.9 ± 11.8 % at 20,40 (n=5); independent per-AP -9.3 ± 31.0 % at 20,40 (CI includes 0). See `docs/results/benchmark-v1.1.0.md` §4c, §5.

### v1.2.0
- Scale to 4 APs.
- Status: ✅ 4 APs, n=3 (global +30.5 ± 27.2 %, CI excludes 0; independent -18.6 ± 47.6 %, CI includes 0). Tagged `v1.2.0` + pushed 2026-10-15. See `docs/results/scaling-v1.2.0.md`.

### v1.3.0
- Scale to 6 APs.
- Status: ✅ validation + 9 long runs (5,10,15,20,25,30, seeds 0-2, n=3) PASS 2026-10-15, merged to main + pushed, tagged `v1.3.0` + pushed 2026-10-15. Global +36.4 ± 49.3 % (CI includes 0, beats BEB at 3/3 seeds); independent -21.6 ± 81.0 % (bimodal). See `docs/results/scaling-v1.3.0.md`.

### v1.4.0
- Scale to 8 APs.
- Status: ✅ validation + 9 long runs (5,10,...,40, seeds 0-2, n=3) PASS 2026-10-16, merged to main + pushed 2026-10-16, tagged `v1.4.0` + pushed 2026-10-16. Global +40.1 ± 92.7 % (CI includes 0, beats BEB at 3/3 seeds); independent -37.1 ± 96.8 % (CI includes 0). See `docs/results/scaling-v1.4.0.md`.

### v1.5.0
- Scale to 10 APs.
- Status: ✅ validation + 9 long runs (4,8,...,40 = 220 STAs, seeds 0-2, n=3) PASS 2026-10-16, merged to main + pushed 2026-10-16, tagged `v1.5.0` + pushed 2026-10-16. Global +41.0 ± 83.9 % (CI includes 0, beats BEB at 3/3 seeds); independent -53.5 ± 27.6 % (CI excludes 0). Full-size dry association check FAILS (late association + deassoc bursts, see doc §3). See `docs/results/scaling-v1.5.0.md`.

### v1.6.0
- Analyze scaling behavior and performance.
- Status: 🔄 analysis done on branch `feature/v1.6.0-scaling-analysis` (merged to main + pushed 2026-10-16, tagged `v1.6.0` + pushed 2026-10-16): recomputed from raw traces v1.1.0..v1.5.0, no new runs. See `docs/results/scaling-v1.6.0.md`, `docs/figures/v1.6.0/`.

## Later — Central Critic

### v1.7.0
- Design centralized critic.
- Status: ✅ TAGGED `v1.7.0` + pushed 2026-10-16. Spec merged to main (6e482ce): one shared global-reward critic, local actors (CTDE), timeboxed v1.8/v1.9, optional. See `docs/design/central-critic-v1.7.0.md`, `docs/adr/0003-central-critic-ctde.md`.

### v1.8.0
- Implement centralized critic prototype.
- Status: 🔄 prototype on branch `feature/v1.8.0-central-critic-prototype` (code 3a292d0, merged to main + pushed; TAGGED `v1.8.0` + pushed 2026-10-16): `--mode central` passes `--check` at 2,3 (short + full) and 20,40 (short). See `docs/design/central-critic-v1.8.0.md`.

### v1.9.0
- Evaluate centralized critic against independent AP agents.
- Status: 🔄 evaluation DONE 2026-10-17 on branch `feature/v1.9.0-central-eval` (not merged/tagged): 6/6 runs PASS. Rule NOT met: N=10 central vs independent -5.80 ± 10.48 Mbps (CI includes 0, 0/3 above; central ~3.2 Mbps, below BEB). Optional/negative result; next v2.x. See `docs/results/central-eval-v1.9.0.md`.

## Later — Finalization

### v2.0.0
- Additional robustness experiments.
- Fixed-total-STA sweep (separate AP count from load; deferred from v1.6.0).
- Status: ✅ CLOSED 2026-10-19 (branch `feature/v2.0.0-robustness`, merged to main + pushed, TAGGED `v2.0.0` after merge; no CI is configured on the repo): fixed-total-STA, AP imbalance, traffic load, rerun on the CW-start-fixed binary, and the large-N association diagnostic. Write-up `docs/results/robustness-v2.0.0.md`. v1.9.0 TAGGED + pushed.

### v2.1.0
- Reproducibility and cleanup.
- Status: ✅ CLOSED 2026-10-19 (branch `feature/v2.1.0-reproducibility`, merged to main + pushed, TAGGED `v2.1.0`; no CI is configured): W&B names/tags, `--trafficStart`/`--staMaxMissedBeacons` pass-through in the trainer, `--trafficStart`/`--offeredLoad` in the runner, `git_rev` in config.json, seed/reset verified, dependencies documented. Defaults unchanged (4 modes byte-identical traces). `docs/reference/reproducibility-v2.1.0.md`.

### v2.2.0
- Final experimental results.
- Status: ✅ CLOSED 2026-10-19 (merged to main + pushed, TAGGED `v2.2.0`; no CI configured). Analysis only, no new runs: final set = fixed-binary v2.0.0 `*-cwfix` runs (81, n=3). `docs/results/final-results-v2.2.0.md`, `docs/figures/v2.2.0/`. Raw data local, W&B sync deferred.

### v2.3.0
- Technical report.
- Status: ✅ CLOSED 2026-10-19 (merged to main + pushed, TAGGED `v2.3.0`; no CI configured). `docs/reports/technical-report-v2.3.0.md`, Markdown; citations are `[REF:key]` placeholders for the user to fill.

### v2.4.0
- Presentation and demonstration.
- Status: ✅ CLOSED 2026-10-19 (merged to main + pushed, TAGGED `v2.4.0`; no CI configured). 14-slide deck (private slides artifact, link in `docs/reports/presentation-v2.4.0.md`), outline + demo script, one 33 s demo rehearsal PASS. Open: title slide team/course names, user review.

### v2.5.0
- Final project audit.
- Status: ✅ CLOSED 2026-10-19 (merged to main + pushed, TAGGED `v2.5.0`; no CI configured). `docs/reports/final-audit-v2.5.0.md`: 26 items, short reruns PASS, src identical to ns-3.29, opengym core identical to ns3-gym db016f8b3. FAIL: references (21 placeholders). PARTIAL: W&B online sync, README, report/deck review, raw-data reproducibility.

### v3.0.0
- Beat Global-CW OSCAR with per-AP-CW agents (trainer-only: `--mode shared`, `--obs hist`, `--alpha`, `--rewardScale`, `--tag`).
- Status: ✅ experiments DONE 2026-10-26, merged to main, pushed, tagged `v3.0.0`. A1 3-seed follow-up (2026-10-27, branch `docs/a1-seeds`): +6.9 ± 26.7 % vs Global, CI spans 0. Best variant V5 is Global-level with lower seed variance at 20,40 and 5,55, not a proven gain: 20,40 +2.8 ± 16.9 %; imbalance 3 seeds +5.0 ± 13.6 % (5,55), +3.8 ± 10.8 % (5,5,5,45) vs Global; 6x10 seed 0 -0.9 %. Ablations (seed 0): shared mode needs neither hist obs nor x100 (A1 39.09, A2 37.38). Per-AP CWs do not separate. `docs/results/improvement-v3.0.0.md`, `docs/adr/0004-relaxed-isolation.md`.

## Not Planned for v1

- Mobility
- Dynamic station addition
- Detailed AP interference modeling
- Per-station Actor agents
