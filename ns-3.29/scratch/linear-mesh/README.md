# OSCAR: a Contention Window Optimization approach using Deep Reinforcement Learning
OSCAR: a Contention Window Optimization approach using Deep Reinforcement Learning to quickly learn the optimal policies under different network conditions

### Requisites
A working [ns3-gym](https://github.com/tkn-tub/ns3-gym) environment is required.
Moreover, a [wandb](https://wandb.ai/) account is required to show the results.

### Installation 
Clone this repository so that it lands inside ns3-gym/scratch/linear-mesh.
Edit ```run = wandb.init(entity="xraulz", project="contention_window", tags = wtags)``` in each training/test file and change ```entity=xraulz``` with ```entity=your_wandb_username```, where ```your_wand_username``` is the wandb account username.

### Start training 
Launch ```python OSCAR_train.py``` to train the OSCAR algorithm.

Launch ```python CCOD_train.py``` to train the CCOD algorithm.

Launch ```python standard_test_and_ccod_train.py``` to test the 802.11 algorithm and train the CCOD algorithm.

### Multi-AP (project extension)
Run from this directory with the project venv (`../../venv/bin/python`); build first with `cd ../.. && ./waf build --target=linear-mesh`. Run one ns-3 job at a time. Setup, pinned versions and seed/reset behaviour: `docs/reproducibility-v2.1.0.md`.

- Train one DDPG agent per AP: ```python OSCAR_multi_ap_train.py --apStaCounts 20,20 --check```. `--mode independent|global|beb|central` (default independent; `global` = one shared CW agent, `beb` = standard 802.11, `central` = optional shared critic). `--seed S` seeds torch/numpy and ns-3 seed S+1; `--trafficStart`, `--offeredLoad`, `--staMaxMissedBeacons` are forwarded to ns-3 only when set. W&B is offline unless `--online`.
- Standard 802.11 BEB baseline, single process: ```python baseline_beb.py --apStaCounts 20,20 --seed 1```.
- Resumable benchmark runner (modes x seeds x topologies): ```python benchmark_v1_1_0.py --help```; aggregate with `aggregate_bench.py`, scaling analysis with `scaling_analysis.py`.
- Summarize a run: ```python summarize_run.py results/multi-ap-<timestamp>```.
- Deterministic joint-action gym test: ```python test_multi_ap_gym.py --staCounts 5,15```.
- Design and results (repo root `docs/`): `multi-ap-design-v0.2.0.md`, `core-v1.0.0.md`, `scaling-v1.6.0.md`, `final-results-v2.2.0.md`, `technical-report-v2.3.0.md`, `final-audit-v2.5.0.md`. Demo command: `presentation-v2.4.0.md`.

### Reference this paper
```
@INPROCEEDINGS{10279663,
  author={Grasso, Christian and Raftopoulos, Raoul and Schembra, Giovanni},
  booktitle={ICC 2023 - IEEE International Conference on Communications}, 
  title={OSCAR: A Contention Window Optimization Approach Using Deep Reinforcement Learning}, 
  year={2023},
  volume={},
  number={},
  pages={459-465},
  doi={10.1109/ICC45041.2023.10279663}}
```

