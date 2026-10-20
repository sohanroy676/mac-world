# Multi-AP OSCAR

Extends [OSCAR](https://doi.org/10.1109/ICC45041.2023.10279663) (DDPG contention-window optimisation for 802.11) from 1 AP / 1 agent / 1 CW to N APs in **one shared ns-3 simulation**. Each AP has its own DDPG agent (actor + critic) and its own CW, with strict per-AP isolation of observations, rewards, actions and statistics. Agents are stepped jointly through ns3-gym.

Out of scope: mobility, dynamic STAs, detailed interference modelling, per-station actors, PHY/MAC changes.

## Modes
| `--mode` | Meaning |
|---|---|
| `independent` | one DDPG agent per AP (default) |
| `global` | one shared CW agent |
| `beb` | standard 802.11 binary exponential backoff (baseline) |
| `central` | optional shared critic (negative result, see `docs/central-eval-v1.9.0.md`) |

## Stack (pinned)
ns-3.29 (C++, GCC 11.4) · ns3-gym 1.0.0 / py 0.1.0 · Python 3.7.16 (venv `ns-3.29/venv`) · PyTorch 1.13.1+cu117 · Gym 0.26.2 · NumPy 1.21.6 · protobuf 3.20.3 · pyzmq 26.2.1 · W&B 0.18.7 · Ubuntu 22.04 (WSL2). Setup and seed behaviour: `docs/reproducibility-v2.1.0.md`.

## Layout
- `ns-3.29/scratch/linear-mesh/`: project code (`cw.cc`, `scenario.h`, `OSCAR_multi_ap_train.py`, `benchmark_v1_1_0.py`, `agents/our_ddpg/`, analysis scripts). Its own `README.md` has the original OSCAR usage plus the multi-AP commands.
- `ns-3.29/contrib/opengym/`: ns3-gym (upstream, unmodified; see `docs/final-audit-v2.5.0.md` §3).
- `docs/`: design, per-version reports, results, audit. `memory-bank/`: current project state. `ROADMAP.md`: version status.
- `README`, `bake/`, `netanim-3.108/`, `pybindgen-*`, `build.py`, `constants.py`, `util.py`: upstream ns-3-allinone.

## Quickstart
```bash
cd ns-3.29 && ./waf build --target=linear-mesh        # rebuild; a stale binary is not validation
# short dry run, no gym
./waf --run "scratch/linear-mesh/linear-mesh --dryRun=true --disableGym=true --apStaCounts=20,40 --simTime=2"
cd scratch/linear-mesh
../../venv/bin/python baseline_v0_1_0.py --smoke      # baseline smoke
../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 20,20 --check   # 2-AP training
../../venv/bin/python benchmark_v1_1_0.py --help      # resumable benchmark runner
```
Run one ns-3 job at a time. W&B runs offline unless `--online` is given.

## Final results (20,40 STAs, 150 Mbps/STA, n=3 seeds, mean ± 95 % CI)
| Mode | Aggregate Mbps | Paired vs BEB |
|---|---|---|
| BEB | 27.30 ± 0.63 | n/a |
| Global-CW | 36.29 ± 7.16 | +33.0 ± 29.0 % |
| Independent | 25.78 ± 20.80 | -5.6 ± 76.0 % |

Scaling, imbalance, load sweep and limits (n=3, wide CIs): `docs/final-results-v2.2.0.md`. Full write-up: `docs/technical-report-v2.3.0.md`.

## Docs index
- Spec and design: `docs/project_description.md`, `docs/multi-ap-design-v0.2.0.md`, `docs/adr/`
- Plan: `ROADMAP.md`, `docs/detailed_roadmap.md`
- Results: `docs/final-results-v2.2.0.md`, `docs/robustness-v2.0.0.md`, `docs/central-eval-v1.9.0.md`
- Report, demo, audit: `docs/technical-report-v2.3.0.md`, `docs/presentation-v2.4.0.md`, `docs/final-audit-v2.5.0.md`

Raw run directories (traces, `.wandb`) are local only and not committed.

## Citation
Grasso, Raftopoulos, Schembra, "OSCAR: A Contention Window Optimization Approach Using Deep Reinforcement Learning", ICC 2023, pp. 459-465, doi:10.1109/ICC45041.2023.10279663.
