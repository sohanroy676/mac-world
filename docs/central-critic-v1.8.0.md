# v1.8.0 Central critic prototype

Status: prototype implemented, 2-AP validation only. Not evidence of benefit (that is v1.9). Spec: `docs/central-critic-v1.7.0.md`.

## 1. What was built (fact)
- `agents/our_ddpg/central.py`: `CentralDDPG(n)`: N `Actor(1,1)` (lr 4e-4, own optimizer + target each), one shared `Critic(n, n)` (lr 4e-3) + target. Critic target `r_g + not_done*0.7*Q'(s', mu'(s'))`; MADDPG actor update (slot i replaced by `mu_i(s_i)`, only actor i's optimizer steps); tau 1e-3 soft updates.
- `agents/our_ddpg/utils.py`: `JointReplayBuffer` (s[N], a[N], s'[N], r_g, r_local[N], not_done; one shared index set).
- `OSCAR_multi_ap_train.py`: `--mode central`; `global_reward()` helper shared with global mode. Trace columns unchanged; per-AP actor loss and the shared critic loss go to the trace and W&B.
- `Critic(state_dim=N, action_dim=N)` needed no change (checked N=2/4/10: input 4/8/20, output (B,1)).
- Upstream ns-3 / ns3-gym / `cw.cc` untouched; no rebuild.

## 2. `--check` additions (central)
Joint replay row equals traced (s, a, r_g, r_local, s'); `r_g` in [0,1]; actor forward-pre-hooks assert input `[B,1]` and, at execution, the batch is 1 and equals the AP's own loss; actors/critic share no parameters; Q, critic loss and actor losses finite every training step. Existing per-AP CW, Test A/D/E and W&B readback checks run unchanged.

## 3. Results (seed 0, n=1)
| run | result |
|---|---|
| 2,3 short (simTime 3, step 0.1), independent / global | PASS, trace.csv byte-identical to pre-change |
| 2,3 short, central | PASS (30 steps) |
| 2,3 full (1500 steps, 1200 training), central | PASS; W&B 1500 rows x 19 keys; no NaN; critic loss max 0.028, ~0 after step 600 |
| 20,40 short (simTime 3, step 0.1; 30 steps, 20 training), central | PASS; W&B 30 rows x 19 keys; 4m39s wall; no leftover ns-3 process |

Full 2,3 central policy window (`summarize_run.py`): 41.5 Mbps total (AP1 0.34, AP2 41.15), Jain 0.56; AP1 CW ends ~940, AP2 ~17. BEB 2,3 reference is 40.47 (`docs/benchmark-v1.1.0.md`). One seed: not a claim.

## 4. Observations and open items
- The shared global reward lets the larger AP win and the 2-STA AP starve: the fairness risk named in spec §11. v1.9 must report per-AP throughput and Jain.
- 20,40 only ran 20 training steps: it proves the plumbing at 60 STAs, not learning. Not run: full-length 20,40, N=4/10, other seeds (v1.9).
- `benchmark_v1_1_0.py --modes central` not tried (v1.9).
