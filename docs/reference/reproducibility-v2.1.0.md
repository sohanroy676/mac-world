# v2.1.0 Reproducibility & cleanup

Status: validated on branch `feature/v2.1.0-reproducibility` (short runs only; no benchmark was rerun).

## 1. Stack (verified from the venv on this machine)

| Item | Version |
|---|---|
| OS | Ubuntu 22.04 on WSL2 |
| Compiler | GCC 11.4.0 |
| ns-3 / ns3-gym | 3.29 / 1.0.0 (py 0.1.0) |
| Python (venv `ns-3.29/venv`) | 3.7.16 |
| torch | 1.13.1 (+cu117) |
| gym | 0.26.2 |
| numpy | 1.21.6 |
| protobuf | 3.20.3 |
| pyzmq | 26.2.1 |
| wandb | 0.18.7 |
| matplotlib / pandas / comet_ml | 3.5.3 / 1.3.5 / 3.52.1 (needed by the baseline and analysis scripts) |

No dependency was changed in v2.1.0. The upstream `contrib/opengym/model/ns3gym/requirements.txt` is not the project's pin list; this table is.

## 2. Build and run

```
cd ns-3.29 && ./waf build --target=linear-mesh        # confirm the binary was rebuilt
cd scratch/linear-mesh
../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --check         # one trainer run
../../venv/bin/python benchmark_v1_1_0.py --topos 2,3 --seeds 0 1 2             # benchmark matrix
```

Run target is `scratch/linear-mesh/linear-mesh`. Run one ns-3 job at a time (`pgrep -x linear-mesh`).

## 3. Seeds and defaults

- Python seed S seeds torch and numpy. The ns-3 seed is S + 1 (ns-3 rejects 0). Every mode of a benchmark uses the same S, so runs are paired by seed.
- Default traffic starts at t = 0 (inherited). Every number in v1.1.0 to v2.0.0 uses this. Large-N association failure comes from it (`docs/results/robustness-v2.0.0.md` section G). `--trafficStart` is available but off by default; this was a deliberate choice to keep results comparable.
- Each trainer run writes `results/multi-ap-<ts>/config.json` with all arguments, `ns3_seed`, and `git_rev` (`git describe --tags --always --dirty`, `unknown` if git is unavailable). A `-dirty` suffix means uncommitted changes.

## 4. Knobs

| Layer | Option | Default |
|---|---|---|
| cw.cc | `--apStaCounts`, `--apCws`, `--simTime`, `--envStepTime`, `--seed`, `--offeredLoad` (150), `--historyLength`, `--dryRun`, `--disableGym`, `--openGymPort` (5555) | see `cw.cc` |
| cw.cc (diagnostic, off) | `--trafficStart` (0), `--staMaxMissedBeacons` (10 = ns-3 default), `--cwReadbackEvery` (0) | off |
| Trainer | `--apStaCounts` (20,40), `--mode independent/global/beb/central`, `--seed`, `--simTime` (15), `--stepTime` (0.01), `--historyLength` (300), `--start_timesteps`, `--batch_size`, `--expl_noise`, `--discount`, `--tau`, `--episodes`, `--offeredLoad`, `--check`, `--online`, `--wandb_project` | see `--help` |
| Trainer (new, diagnostic) | `--trafficStart`, `--staMaxMissedBeacons` | 0 = not sent to ns-3 |
| Runner | `--topos`, `--modes`, `--seeds`, `--simTime`, `--stepTime`, `--benchDir`, `--trainerArgs`, new `--trafficStart`, `--offeredLoad` | not sent unless given |

The new trainer and runner options are forwarded only when set, so default runs send the same ns-3 arguments as before.

## 5. W&B

- Run name is `<apStaCounts> <mode> s<seed>` (for example `2,3 independent s1`). Tags are `multi-ap`, `mode-<mode>`, and the git revision. Before, every run was named `... v1.0.0` with a stale `v0.9.0` tag.
- Offline by default; `--online` syncs.
- Entity comes from `config.py` (an account name, not a secret). `WANDB_ENTITY` overrides it. No API key is stored in the repo.

## 6. Remaining hard-coded assumptions (kept on purpose)

- Trainer default `--apStaCounts 20,40` (design default, ADR-0002).
- Single-AP reward constant `5*150` in `cw.cc` (baseline quirk, `docs/results/baseline-v0.1.0.md` section 7). Changing it would change the single-AP baseline.
- Multi-AP gym supports only `scenario=basic` (per-AP reward fixes the STA count).
- One /24 subnet limits the topology to about 253 nodes (10 APs with 220 STAs fits).
- Debug output: per-step prints in `cw.cc` are already behind `--verbose` (default off). The remaining output lines are end-of-run checks that the tools parse, so none were removed. No `cw.cc` change, so no rebuild.

## 7. Verification (2026-10-19, binary built from the v2.0.0 `cw.cc`; the binary contains the diagnostic switches, `cw.cc` unchanged since 72d7087)

Command: `--apStaCounts 2,3 --simTime 3 --stepTime 0.1 --historyLength 20 --start_timesteps 10 --batch_size 8 --check`, seed 0.

| Check | Result |
|---|---|
| independent / global / beb / central, before and after the edit | 8/8 `RESULT: PASS`; the four `trace.csv` pairs are byte-identical, so the defaults did not change |
| Seed: repeat seed 0 | identical trace (the before/after pair above is that repeat) |
| Seed: seed 1 | trace differs from seed 0 |
| Reset: `--episodes 2` | PASS (60 steps); episode 1 step 1 has the same observation as episode 0 step 1 (0.5625 / 0.5815); the CW differs because the learned policy carries over |
| `--trafficStart 2` through the runner | AP1 rx is 0 in steps 1 to 5 and nonzero by step 21; the default run receives packets from step 1 |
| W&B | run `2,3 independent s1`, tags `mode-independent` and `v2.0.0-dirty` found in the `.wandb` file |

Not done: the regression pkts (10533 / 9000 / smoke 10.59458) were not rerun, because `cw.cc` and the binary are unchanged. Large runs were not rerun.

## 8. Backlog

- Central-critic N=10 collapse (v1.9.0): cause untested, left in the v2.x backlog by user decision.
- Benchmarks with traffic started after association: not run; the flag now exists for it.
