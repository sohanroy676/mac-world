# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **trainer**: Add RAFA inputs, station-weighted PF reward, noise dist
- **ci**: Sequence jobs and step 1 batch; pre-register step 1
- **trainer**: Add alpha input with relabelling and floor penalty
- **trainer**: Round-robin pool with per-scenario floors

### Documentation

- **plan**: Add revision 6 from mentor papers
- **changelog**: Regenerate with git-cliff
- **plan**: Add revision 7 Gumbel noise ablation
- **changelog**: Regenerate with git-cliff
- **plan**: Add revision 8 critical check fixes
- **changelog**: Regenerate with git-cliff
- **plan**: Add revision 9 second critical pass
- **changelog**: Regenerate with git-cliff
- **plan**: Rebuild plan as revision 10 on feature/v4
- **changelog**: Regenerate with git-cliff
- **actions**: Record GitHub Actions smoke test results
- **actions**: Record full-cell timing results
- **actions**: Correct beb job total time
- **results**: Record Actions vs lab comparability
- **memory-bank**: Record Actions comparability check
- **m3**: Record step 0 checks, input scales, pool refs
- **m3**: Record step 1 results and the G1 decision
- **m3**: Record step 2 lambda batch, pick lambda 1
- **m3**: Record step 2b (12 episodes, alpha-0 evals)
- **m3**: Record step 3 results, G3 fails
- **changelog**: Regenerate with git-cliff
- **handoff**: V4.0.0 handoff prompt and state

### Fixed

- **ci**: Pick the new run dir by set difference
- **trainer**: Rafa state check uses the input size
- **trainer**: End-of-run checks follow per-episode AP count
- **train**: Align pool reward check by step

### Other

- **actions**: Add smoke-test workflow for hosted runners
- **actions**: Fail steps on pipe errors, prefer deadsnakes
- **actions**: Install python shim and trim artifact
- **actions**: Build through waf --run on a clean tree
- **actions**: Add matplotlib to Python 3.7 pins
- **actions**: Add full-cell timing workflow
- **actions**: Merge Actions groundwork into v4
- **actions**: Add job-list runner with reference cmp
- **actions**: Ship run dirs in job logs, add step 0 batch
- **actions**: Pin torch/MKL kernels, add determinism batch
- **actions**: Add float probe job to find the CPU-vendor difference
- Rerun micro check
- Launch M3 step 1 batch (30 jobs)
- Pre-register and launch M3 step 2 lambda batch
- Launch step 2b (12 episodes at lambda 1, alpha-0 evals)
- Pre-register and launch M3 step 3 (pooled RAFA, gate G3)
- **m2c**: Pre-register and launch learned rivals

## [3.7.0] - 2026-11-05

### Added

- **m1**: S7-S4b, S8p3 edge grid, a5 jobs
- **m2**: KW and UCB per-AP controllers
- **m2**: BEB+RTS/CTS job list (a6)
- **m2**: Kw and ucb trainer modes, tuning jobs
- **m2**: Tuning analysis, KW and UCB eval jobs
- **m2**: Ccod trainer mode (Global form)

### Data

- **m1**: 30 s GC evaluation runs (a5)
- **m2**: KW, UCB, RTS and CCOD runs
- **m1,m2**: S7-S4b, S8p3 and tuning runs

### Documentation

- **m1**: GC tables at 30 s, seeds 100-109
- **m2**: GC tables with KW, UCB and RTS at 30 s
- **m2**: Baselines result, roadmap and memory bank
- **changelog**: Regenerate with git-cliff
- **m2**: Batch logs, manifests and actors
- **handoff**: V3.7.0 handoff, prompt for M3
- **changelog**: Regenerate with git-cliff

## [3.6.0] - 2026-11-02

### Added

- **trace**: Idle column and gym-safe DELAY with extraTraces
- **m1**: Job generator and selection-seed analysis
- **m1**: GC-table job generator (a3)

### Documentation

- **plan**: Revision 6, 5 % fair-floor slack
- **m1**: Grids, gates, partial GC table
- **changelog**: Regenerate with git-cliff
- **m1**: Complete GC tables for S2, S4, S5a
- **changelog**: Regenerate with git-cliff
- **handoff**: Commit v3.6.0 runs, rewrite prompt
- **changelog**: Regenerate with git-cliff

## [3.5.0] - 2026-11-01

### Added

- **cw**: Add useRts, rewardNorm, extraTraces flags
- **sim**: Add staSchedule, scenarioPool, delay stats
- **analysis**: Add GC tables, ADR-0006/0007, pool

### Documentation

- **planning**: Add final v4 plan (revision 4)
- **planning**: Add v4 plan to beat all baselines
- **changelog**: Regenerate with git-cliff
- **planning**: Revise v4 plan and take decisions
- **changelog**: Regenerate with git-cliff
- **planning**: Apply second review to v4 plan
- **changelog**: Regenerate with git-cliff
- **changelog**: Regenerate with git-cliff
- **planning**: Apply final check to v4 plan
- **changelog**: Regenerate with git-cliff
- **handoff**: Update session prompt and memory bank for v3.3.1
- **changelog**: Regenerate with git-cliff
- **changelog**: Regenerate with git-cliff
- **claude**: Point roadmap status to the v4 plan
- **changelog**: Regenerate with git-cliff
- **m0**: Record v3.5.0 results, add tagPrefix
- **m0**: Add pool BEB reference table
- **changelog**: Regenerate with git-cliff
- **handoff**: Commit v3.5.0 runs, rewrite prompt
- **changelog**: Regenerate with git-cliff

### Fixed

- **lanes**: Unseeded free ports, unique run dirs
- **trainer**: Per-run leftover check, floor slack

## [3.3.1] - 2026-11-01

### Added

- **sensing**: Add per-AP idle-slot sensing and IdleSense

### Documentation

- **report**: Add v3.4.0 hidden-chain results
- **results**: Add TD3 and cwMinOnly policy seed 2
- **v3.3.0**: Add sensing and IdleSense results
- **report**: Add v3.3.0 sensing section
- **changelog**: Regenerate with git-cliff
- **v3.3.0**: Add run dirs for seed 2, sensing and calibration
- **v3.3.0**: Flag IdleSense rule as a variant
- **v3.3.1**: Add corrected IdleSense results
- **changelog**: Regenerate with git-cliff
- **v3.3.1**: Add IdleSense results on 20,40
- **changelog**: Regenerate with git-cliff
- **v3.3.1**: Add run dirs for corrected IdleSense arms
- **claude**: Update roadmap status to v3.3.1
- **changelog**: Regenerate with git-cliff

### Fixed

- **sensing**: Use the published Idle Sense AIMD rule

## [3.4.1] - 2026-10-31

### Documentation

- **v3.4.0**: Mark milestone tagged
- **v3.4.0**: Add paired static oracle at eval seeds
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add oracle run dirs and handoff prompt
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add trainSeed 1 policy-seed variance
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add trainSeed 1 run dirs
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add trainSeed 2 policy-seed results
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add trainSeed 2 run dirs (G, H)
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add TD3, cwMinOnly and apLoads results
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add unsaturated uneven-load result
- **changelog**: Regenerate with git-cliff
- **v3.4.0**: Add TD3/cwMinOnly second policy seed
- **changelog**: Regenerate with git-cliff
- **v3.4.1**: Add run dirs for algo, seed 1 and load arms
- **handoff**: Update session prompt and memory bank for v3.4.1
- **changelog**: Regenerate with git-cliff

## [3.4.0] - 2026-10-29

### Added

- **cw**: Opt-in hidden BSS pairs and per-AP loads
- **trainer**: Scenario flags and proportional-fair reward
- **bench**: Chain3 grid, PF/min-AP and Wilcoxon tables
- **bench**: Runner --variant, custom static grid, ADR-0005

### Documentation

- **v3.4.0**: Add chain3 static gate result
- **v3.4.0**: Add n=8 frozen-eval batch results
- **handoff**: Rewrite session prompt for v3.4.0 follow-ups
- **v3.4.0**: Add run dirs, logs, manifests and actors
- **changelog**: Regenerate with git-cliff

## [3.2.0] - 2026-10-28

### Added

- **cw**: Add --cwMinOnly for agent actions
- **agents**: Add TD3 learner
- **trainer**: Add fair-protocol flags
- **runner**: Add v3.2.0 fair-protocol runner

### Documentation

- **ceiling**: Add paired 6x10 BEB/Global refs
- **results**: Add 6x10 refs and 20,40 fair-protocol pilot runs
- **v3.2.0**: Add fair-protocol report and handoff

### Fixed

- **runner**: Keep learner flags away from BEB jobs

## [3.1.0] - 2026-10-28

### Added

- **sweep**: Add static CW mode and ceiling sweep pilot

### Documentation

- **research**: Add plan to beat OSCAR and BEB
- **workflow**: Adopt dev branch and push rule
- **ceiling**: Add v3.1.0 static CW sweep results
- **handoff**: Commit v3.1.0 runs and next-session prompt

## [main-at-v3.4.1] - 2026-10-27

### Changed

- **scratch**: Drop two unused names
- **changelog**: Add git-cliff config and generate
- **changelog**: Regenerate
- Remove unused pre-deploy checklist
- **changelog**: Regenerate

### Documentation

- **baseline**: Add OSCAR baseline metrics note
- **results**: Add A1 seeds 1-2 at 20,40
- **memory**: Update state after v3.0.0
- **memory**: Mark a1-seeds merged and pushed
- Group docs/ into topic folders
- Add v3.0.0 report section, fill refs, fix stale status
- **memory**: Record restructure and cleanup state
- **memory**: Mark restructure merged and pushed

## [3.0.0] - 2026-10-26

### Added

- **train**: Add shared mode, hist obs, mixed reward

### Documentation

- **adr**: Add ADR-0004 relaxed isolation
- **results**: Add v3.0.0 improvement report
- **memory**: Update after beat-oscar experiments
- **results**: Add v3.0.0 ablations and 3-seed stress

## [2.7.2] - 2026-10-20

### Added

- **wandb**: Add final-run sync launcher

### Documentation

- **memory**: Handoff after wandb sync script

## [2.7.1] - 2026-10-20

### Documentation

- **memory**: Handoff after v2.7.0
- **readme**: Add project root README
- **results**: Record W&B sync of final runs
- **memory**: Handoff after W&B sync and README

## [2.7.0] - 2026-10-20

### Added

- **cw**: Log inactive sinks in CW readback

### Documentation

- **audit**: Resolve opengym upstream provenance
- **central**: 22x10 seeds and reward scales

## [2.6.1] - 2026-10-20

### Documentation

- **central**: Independent mode at 22x10
- **memory**: Handoff after independent 22x10

## [2.6.0] - 2026-10-20

### Added

- **train**: Add --rewardScale for central ablation

### Documentation

- **central**: Reward-scale ablation at 22x10
- **central**: X100 seeds, references, 4..40
- **memory**: Handoff after reward-scale ablation

## [2.5.2] - 2026-10-19

### Documentation

- **robustness**: Traffic start vs association
- **robustness**: 6x10 rerun with traffic start 1
- **central**: Collapse follow-up on fixed binary
- **central**: 4..40 collapse persists on fixed binary
- **central**: 22x10 equal split also collapses
- **memory**: Handoff after traffic-start and central work

## [2.5.1] - 2026-10-19

### Documentation

- **robustness**: Measure active sinks per mode
- **memory**: Active-sink count closed

## [2.5.0] - 2026-10-19

### Documentation

- **audit**: Add v2.5.0 final audit
- Refresh README, AGENTS.md and ADR-0003
- **memory**: V2.5.0 closed

## [2.4.0] - 2026-10-19

### Documentation

- **presentation**: V2.4.0 deck outline and demo
- **memory**: V2.4.0 closed

## [2.3.0] - 2026-10-19

### Documentation

- **report**: V2.3.0 technical report draft
- **memory**: V2.3.0 closed

## [2.2.0] - 2026-10-19

### Added

- **analysis**: Reward/fairness plots, CSV export
- **analysis**: Fixed60 scaling preset

### Documentation

- **claude**: Fix repo root path
- **results**: V2.2.0 final results
- **memory**: V2.2.0 handoff
- **memory**: V2.2.0 closed

## [2.1.0] - 2026-10-19

### Added

- **train**: Meaningful W&B names and diag flags

### Documentation

- **repro**: V2.1.0 reproducibility notes
- **memory**: V2.1.0 handoff

## [2.0.0] - 2026-10-19

### Added

- **sim**: Add --offeredLoad knob
- **sim**: Optional periodic STA CW readback
- **sim**: Log active sinks in CW readback
- **sim**: Association diagnostics switches

### Documentation

- **robust**: V2.0.0 fixed-total-STA results
- **robust**: V2.0.0 AP imbalance results
- **robust**: Clarify B.3 small-AP wording
- **robust**: V2.0.0 traffic load and CW-start finding
- **robust**: V2.0.0 reruns on the fixed binary
- **robust**: V2.0.0 association diagnostic and status
- **memory**: V2.0.0 handoff

### Fixed

- **sim**: Start multi-AP agent runs at BEB CW

## [1.9.0] - 2026-10-17

### Added

- **bench**: Aggregate central mode, multi-dir

### Documentation

- **cc**: V1.9.0 central critic evaluation

## [1.8.0] - 2026-10-16

### Added

- **cc**: Add central critic mode (v1.8.0)

### Documentation

- **cc**: V1.8.0 prototype notes and handoff
- **cc**: Record v1.8.0 20,40 short check
- **cc**: V1.8.0 handoff and central traces

## [1.7.0] - 2026-10-16

### Documentation

- **cc**: V1.7.0 central critic design spec
- **memory**: V1.7.0 handoff

## [1.6.0] - 2026-10-16

### Added

- **analysis**: Add cross-N scaling script

### Data

- **results**: Commit v1.1-v1.5 benchmark traces

### Documentation

- **scale**: V1.6.0 scaling analysis
- **memory**: V1.6.0 closeout handoff
- **scale**: Defer fixed-STA sweep to v2.0.0

## [1.5.0] - 2026-10-16

### Documentation

- **scale**: V1.5.0 10-AP validation and n=3 results
- **memory**: V1.5.0 closeout handoff

## [1.4.0] - 2026-10-16

### Documentation

- **scale**: V1.4.0 8-AP validation and n=3 results
- **memory**: V1.4.0 closeout handoff

## [1.3.0] - 2026-10-15

### Documentation

- **scale**: V1.3.0 6-AP validation and n=3 results

## [1.2.0] - 2026-10-15

### Data

- **bench**: Raw 4-AP runs seeds 1,2

### Documentation

- **scale**: V1.2.0 four-AP validation
- **memory**: V1.2.0 handoff and raw 4-AP results
- **scale**: V1.2.0 4-AP seeds 1,2 (n=3)
- **memory**: V1.2.0 n=3 handoff
- **memory**: V1.2.0 n=3 closeout handoff

### Fixed

- **train**: Generalise check to N APs
- **bench**: Per-AP bar plot for N APs

## [1.1.0] - 2026-10-15

### Added

- **bench**: Add beb/global modes and benchmark tools

### Documentation

- **bench**: Add v1.1.0 batch 1 results
- **bench**: V1.1.0 batch 2 partial 20,20 results
- **bench**: V1.1.0 batch 2 complete 20,20 results
- **memory**: Handoff after v1.1.0 batch 2
- **bench**: V1.1.0 batch 3 partial (20,40 beb s0)
- **bench**: V1.1.0 batch 3 partial 5/9 (20,40)
- **bench**: V1.1.0 batch 3 complete, 20,40 9/9
- **memory**: V1.1.0 handoff after merge
- **bench**: V1.1.0 20,40 n=5 seeds

### Fixed

- **sim**: Seed RNG before nodes are created
- **train**: Mirror cw.cc float32 CW in --check

## [1.0.0] - 2026-10-08

### Added

- **core**: V1.0.0 seed pinning and BEB baseline

### Documentation

- V1.0.0 handoff, tag pending long runs
- **core**: Add 60-STA long-run results
- V1.0.0 close-out

## [0.9.0] - 2026-10-08

### Added

- **train**: V0.9.0 validation checks and summary

### Documentation

- V0.9.0 validation results so far
- Add 5,15 long run to v0.9.0 validation
- Close v0.9.0 handoff

## [0.8.0] - 2026-10-08

### Added

- **train**: Per-AP W&B logging

### Documentation

- Close v0.8.0 handoff

## [0.7.0] - 2026-10-08

### Added

- **train**: Independent per-AP DDPG agents

### Documentation

- Record v0.7.0 status
- Close v0.7.0 handoff

## [0.6.0] - 2026-10-08

### Added

- **gym**: Per-AP obs, action and reward

### Documentation

- Record v0.6.0 status
- Close v0.6.0 handoff

### Tests

- **gym**: Add joint-step per-AP mapping test

## [0.5.0] - 2026-10-08

### Added

- **cw**: Set contention window per AP

### Documentation

- Close v0.4.0 handoff
- Mark v0.4.0 pushed
- Record v0.5.0 per-ap cw status
- Close v0.5.0 handoff

## [0.4.0] - 2026-10-08

### Added

- **stats**: Add per-ap tx/rx accounting

### Documentation

- Record v0.4.0 per-ap stats status

## [0.3.0] - 2026-10-07

### Added

- **topology**: Validate two-ap layout

### Changed

- **topology**: Checkpoint two-ap layout

### Documentation

- **design**: Define multi-ap v0.2.0
- Add CLAUDE.md and close v0.3.0 handoff

[unreleased]: https://github.com///compare/v3.7.0..HEAD
[3.7.0]: https://github.com///compare/v3.6.0..v3.7.0
[3.6.0]: https://github.com///compare/v3.5.0..v3.6.0
[3.5.0]: https://github.com///compare/v3.3.1..v3.5.0
[3.3.1]: https://github.com///compare/v3.4.1..v3.3.1
[3.4.1]: https://github.com///compare/v3.4.0..v3.4.1
[3.4.0]: https://github.com///compare/v3.2.0..v3.4.0
[3.2.0]: https://github.com///compare/v3.1.0..v3.2.0
[3.1.0]: https://github.com///compare/main-at-v3.4.1..v3.1.0
[main-at-v3.4.1]: https://github.com///compare/v3.0.0..main-at-v3.4.1
[3.0.0]: https://github.com///compare/v2.7.2..v3.0.0
[2.7.2]: https://github.com///compare/v2.7.1..v2.7.2
[2.7.1]: https://github.com///compare/v2.7.0..v2.7.1
[2.7.0]: https://github.com///compare/v2.6.1..v2.7.0
[2.6.1]: https://github.com///compare/v2.6.0..v2.6.1
[2.6.0]: https://github.com///compare/v2.5.2..v2.6.0
[2.5.2]: https://github.com///compare/v2.5.1..v2.5.2
[2.5.1]: https://github.com///compare/v2.5.0..v2.5.1
[2.5.0]: https://github.com///compare/v2.4.0..v2.5.0
[2.4.0]: https://github.com///compare/v2.3.0..v2.4.0
[2.3.0]: https://github.com///compare/v2.2.0..v2.3.0
[2.2.0]: https://github.com///compare/v2.1.0..v2.2.0
[2.1.0]: https://github.com///compare/v2.0.0..v2.1.0
[2.0.0]: https://github.com///compare/v1.9.0..v2.0.0
[1.9.0]: https://github.com///compare/v1.8.0..v1.9.0
[1.8.0]: https://github.com///compare/v1.7.0..v1.8.0
[1.7.0]: https://github.com///compare/v1.6.0..v1.7.0
[1.6.0]: https://github.com///compare/v1.5.0..v1.6.0
[1.5.0]: https://github.com///compare/v1.4.0..v1.5.0
[1.4.0]: https://github.com///compare/v1.3.0..v1.4.0
[1.3.0]: https://github.com///compare/v1.2.0..v1.3.0
[1.2.0]: https://github.com///compare/v1.1.0..v1.2.0
[1.1.0]: https://github.com///compare/v1.0.0..v1.1.0
[1.0.0]: https://github.com///compare/v0.9.0..v1.0.0
[0.9.0]: https://github.com///compare/v0.8.0..v0.9.0
[0.8.0]: https://github.com///compare/v0.7.0..v0.8.0
[0.7.0]: https://github.com///compare/v0.6.0..v0.7.0
[0.6.0]: https://github.com///compare/v0.5.0..v0.6.0
[0.5.0]: https://github.com///compare/v0.4.0..v0.5.0
[0.4.0]: https://github.com///compare/v0.3.0..v0.4.0
[0.3.0]: https://github.com///tree/v0.3.0

<!-- generated by git-cliff -->
