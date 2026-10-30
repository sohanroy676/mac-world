# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [3.4.0] - 2026-10-29

### Added

- **cw**: Add --cwMinOnly for agent actions
- **agents**: Add TD3 learner
- **trainer**: Add fair-protocol flags
- **runner**: Add v3.2.0 fair-protocol runner
- **cw**: Opt-in hidden BSS pairs and per-AP loads
- **trainer**: Scenario flags and proportional-fair reward
- **bench**: Chain3 grid, PF/min-AP and Wilcoxon tables
- **bench**: Runner --variant, custom static grid, ADR-0005

### Documentation

- **ceiling**: Add paired 6x10 BEB/Global refs
- **results**: Add 6x10 refs and 20,40 fair-protocol pilot runs
- **v3.2.0**: Add fair-protocol report and handoff
- **v3.4.0**: Add chain3 static gate result
- **v3.4.0**: Add n=8 frozen-eval batch results
- **handoff**: Rewrite session prompt for v3.4.0 follow-ups
- **v3.4.0**: Add run dirs, logs, manifests and actors
- **changelog**: Regenerate with git-cliff

### Fixed

- **runner**: Keep learner flags away from BEB jobs

## [3.1.0] - 2026-10-28

### Added

- **sweep**: Add static CW mode and ceiling sweep pilot

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
- **research**: Add plan to beat OSCAR and BEB
- **workflow**: Adopt dev branch and push rule
- **ceiling**: Add v3.1.0 static CW sweep results
- **handoff**: Commit v3.1.0 runs and next-session prompt

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

[unreleased]: https://github.com/sohanroy676/mac-world/compare/v3.4.0..HEAD
[3.4.0]: https://github.com/sohanroy676/mac-world/compare/v3.1.0..v3.4.0
[3.1.0]: https://github.com/sohanroy676/mac-world/compare/v3.0.0..v3.1.0
[3.0.0]: https://github.com/sohanroy676/mac-world/compare/v2.7.2..v3.0.0
[2.7.2]: https://github.com/sohanroy676/mac-world/compare/v2.7.1..v2.7.2
[2.7.1]: https://github.com/sohanroy676/mac-world/compare/v2.7.0..v2.7.1
[2.7.0]: https://github.com/sohanroy676/mac-world/compare/v2.6.1..v2.7.0
[2.6.1]: https://github.com/sohanroy676/mac-world/compare/v2.6.0..v2.6.1
[2.6.0]: https://github.com/sohanroy676/mac-world/compare/v2.5.2..v2.6.0
[2.5.2]: https://github.com/sohanroy676/mac-world/compare/v2.5.1..v2.5.2
[2.5.1]: https://github.com/sohanroy676/mac-world/compare/v2.5.0..v2.5.1
[2.5.0]: https://github.com/sohanroy676/mac-world/compare/v2.4.0..v2.5.0
[2.4.0]: https://github.com/sohanroy676/mac-world/compare/v2.3.0..v2.4.0
[2.3.0]: https://github.com/sohanroy676/mac-world/compare/v2.2.0..v2.3.0
[2.2.0]: https://github.com/sohanroy676/mac-world/compare/v2.1.0..v2.2.0
[2.1.0]: https://github.com/sohanroy676/mac-world/compare/v2.0.0..v2.1.0
[2.0.0]: https://github.com/sohanroy676/mac-world/compare/v1.9.0..v2.0.0
[1.9.0]: https://github.com/sohanroy676/mac-world/compare/v1.8.0..v1.9.0
[1.8.0]: https://github.com/sohanroy676/mac-world/compare/v1.7.0..v1.8.0
[1.7.0]: https://github.com/sohanroy676/mac-world/compare/v1.6.0..v1.7.0
[1.6.0]: https://github.com/sohanroy676/mac-world/compare/v1.5.0..v1.6.0
[1.5.0]: https://github.com/sohanroy676/mac-world/compare/v1.4.0..v1.5.0
[1.4.0]: https://github.com/sohanroy676/mac-world/compare/v1.3.0..v1.4.0
[1.3.0]: https://github.com/sohanroy676/mac-world/compare/v1.2.0..v1.3.0
[1.2.0]: https://github.com/sohanroy676/mac-world/compare/v1.1.0..v1.2.0
[1.1.0]: https://github.com/sohanroy676/mac-world/compare/v1.0.0..v1.1.0
[1.0.0]: https://github.com/sohanroy676/mac-world/compare/v0.9.0..v1.0.0
[0.9.0]: https://github.com/sohanroy676/mac-world/compare/v0.8.0..v0.9.0
[0.8.0]: https://github.com/sohanroy676/mac-world/compare/v0.7.0..v0.8.0
[0.7.0]: https://github.com/sohanroy676/mac-world/compare/v0.6.0..v0.7.0
[0.6.0]: https://github.com/sohanroy676/mac-world/compare/v0.5.0..v0.6.0
[0.5.0]: https://github.com/sohanroy676/mac-world/compare/v0.4.0..v0.5.0
[0.4.0]: https://github.com/sohanroy676/mac-world/compare/v0.3.0..v0.4.0
[0.3.0]: https://github.com/sohanroy676/mac-world/tree/v0.3.0

<!-- generated by git-cliff -->
