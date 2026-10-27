# v1.7.0 Central critic design (spec only)

Status: design. No code and no ns-3 run in v1.7.0. Decision record: `docs/adr/0003-central-critic-ctde.md`.
Values below were read from `OSCAR_multi_ap_train.py` and `agents/our_ddpg/` (facts). Anything marked *inference* or *unknown* is not verified.

## 0. Why, scope, timebox
- Motivation (fact, `docs/results/scaling-v1.6.0.md`): independent agents are below BEB at every N (-9 % -> -54 %, CI excludes 0 only at N=10); global-CW is above BEB at 17/17 seed pairs. Whether a central critic fixes the independent deficit is **untested** (unknown).
- Scheme: CTDE. Centralized training critic, decentralized execution actors. One **shared** critic, trained on the **global** reward (user decision 2026-10-16).
- Optional. It must never block core completion. Timebox: v1.8 prototype <= 1 session; v1.9 small evaluation. If the timebox runs out or v1.9 shows no benefit (rule in §10), document as an optional/negative result and continue to v2.x.
- Existing modes (`independent`, `global`, `beb`) are untouched; the new one is `--mode central`.

## 1. Central state
`s = [s_1 .. s_N]`, where `s_i` is AP i's raw loss scalar `(tx-rx)/tx` (the same value actor i sees, `S[i, :state_dim]`, state_dim = 1). Dimension N. STA counts are static and not included.

## 2. Joint action
`a = [a_1 .. a_N]`, each `a_i` in [-1, 1] (actor output domain, before the `real = real_max_action*(a+1)/2` mapping and CW = 2^(a+4) clamp 16..1024). Dimension N. The stored action is the pre-mapping value, as in the current replay buffers.

## 3. Rewards
- **Global reward (learning signal):** `r_g = clamp(sum_i rx_i * 1464*8 / (offeredLoad*1e6 * sum_i STAs_i * stepTime), 0, 1)`; the exact formula already used in `--mode global`.
- **Local reward:** `r_i` unchanged (per-AP normalized goodput). Logged and stored in the replay row for fairness analysis; **not used for learning** in v1.8.

## 4. Critic input and architecture
One critic `Q(s, a)`; input = concat(s, a), dimension 2N, output 1. Same MLP as the existing `Critic` in `Our_DDPG.py` (2N -> 128 -> 128 -> 1, ReLU); reuse the class with `Critic(state_dim=N, action_dim=N)`. Adam lr 4e-3 (the current critic lr). Note: `Critic.l1` is `nn.Linear(state_dim+action_dim, 128)`, so no class change is needed (to be confirmed when coding).

## 5. Actors and actor update
- N local actors `mu_i(s_i)`: the existing `Actor` (1 -> 128 -> 128 -> 1, tanh), Adam lr 4e-4 each, one optimizer per actor.
- **Execution:** actor i sees only `s_i`; per-AP isolation holds. The critic is training-only.
- **Update (MADDPG style):** for each i, build `a^(i)` = the sampled batch actions with slot i replaced by `mu_i(s_i)` (other slots fixed at replayed values). `loss_i = -Q(s, a^(i)).mean()`. Backprop; step only actor i's optimizer (zero the critic grad so it is not applied).

## 6. Critic update and target networks
- Target: `y = r_g + not_done * gamma * Q'(s', [mu'_1(s'_1) .. mu'_N(s'_N)])`, gamma = 0.7. Loss: MSE(Q(s,a), y).
- Target networks: one target critic + N target actors. Soft update `theta' <- tau*theta + (1-tau)*theta'`, tau = 1e-3, after every training step (matches `DDPG.train`).

## 7. Replay format
One joint buffer (max 1e6). Row = `(s[N], a[N], r_g, r_local[N], s'[N], not_done)`. Critic and all actors use the **same** sampled indices each step. A new joint-buffer class is needed (the existing `ReplayBuffer` is single-agent); put it next to `utils.py`. `not_done` follows the existing `done[0]` handling.

## 8. Training frequency and exploration
- First `start_timesteps` = 300 steps: uniform random actions, no training (as now).
- Afterwards, each env step: 1 critic update, then N actor updates, batch 32, then target soft updates. Same per-step cadence as independent mode.
- Exploration: Gaussian noise `0.1*max_action`, drawn independently per AP.
- Other parameters match the trainer defaults: 1500 steps per episode (simTime 15, step 0.01), seed handling unchanged (ns-3 seed = python seed + 1).

## 9. v1.8 prototype checklist (`--check` extensions)
- Replay row equals the traced `(s, a, r_g, r_i, s')`.
- Per-AP CW = `2^(4+a_i)` clamp 16..1024 as in the existing check.
- Actor forward input is `s_i` only (no joint tensor reaches an actor at execution).
- `Q`, critic loss, actor losses finite; `r_g` in [0, 1].
- Order: `--apStaCounts 2,3 --check` short run first, then 20,40.
- Done when: a short run trains with valid losses/Q (roadmap v1.8.0 criterion).

## 10. v1.9 evaluation and decision rule
- Conditions: N=4 (5,10,15,20) and N=10 (4,8,...,40), seeds 0-2, same config as the existing independent/BEB runs. 6 new runs, about 3.5 h total (inference from ~13 min and ~55 min per run in earlier docs; re-check).
- Compare against the committed independent and BEB traces via `scaling_analysis.py` / `summarize_run.py`: aggregate and per-AP throughput, Jain fairness, loss, convergence, run time, stability across seeds.
- Rule: central counts as beneficial only if the paired CI vs independent excludes 0 at N=10 (n=3 is low power: state this limit). Otherwise document as optional/negative.

## 11. Invariant exception and risks
- ADR-0002 invariant "no AP sees another AP's local obs" is relaxed **only for the critic during training in `--mode central`**. Execution stays isolated.
- Global reward may favor large APs and hurt small ones; Jain checked in v1.9.
- Critic input grows 2N; with ~1500 transitions per run it may be data-starved (*inference*).
- Differences vs `--mode global` (one agent, one broadcast CW) must be kept in mind: central keeps per-AP CWs.
- Association/deassociation confound at large N stays deferred (v2.x).

## 12. Roadmap item map
central state §1 · joint action §2 · global reward §3 · local reward §3 · critic input §4 · critic architecture §4 · actor update §5 · replay format §7 · target networks §6 · training frequency §8.
