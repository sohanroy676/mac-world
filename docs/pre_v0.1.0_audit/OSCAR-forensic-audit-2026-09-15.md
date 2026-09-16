# OSCAR (Contention-Window RL) — Forensic Audit of the Existing Working Project

**Workspace root:** `/home/gloomyleader/college/major/ns-allinone-3.29`
**Audit date:** 2026-09-15
**Audit mode:** strictly read-only. The ONLY file created is this report. No project file was modified, renamed, moved or deleted; no training was launched; nothing was installed; no build artifacts were touched.

**Evidence legend**
- **[FACT]** — verified directly from workspace files, git metadata, or build artifacts (file:line given).
- **[INFERENCE]** — concluded from evidence; stated explicitly as an inference.
- **[PAPER-KNOWLEDGE]** — statement about the ICC-2023 OSCAR paper / upstream repo as understood from documentation; NOT verifiable from this workspace.
- **[UNKNOWN]** — cannot be determined locally; next action given in §16.

---

# 1. Executive Summary

1. The OSCAR project is a git clone at `ns-3.29/scratch/linear-mesh/` (origin: `https://github.com/sohanroy676/OSCAR-contention-window-RL.git`, upstream: `https://github.com/raoulraft/OSCAR-contention-window-RL.git`), branch `major-project`, exactly 2 local commits ahead of upstream `main` (b595c67), with 3 uncommitted modifications. **[FACT]**
2. The working training command is `python OSCAR_train.py` (from `scratch/linear-mesh`, venv Python 3.7.16 at `ns-3.29/venv`). It trains ONE DDPG agent ("OurDDPG") that controls ONE contention-window value for the WHOLE WLAN (1 AP + nWifi=40 STAs). **[FACT]**
3. ns-3 side = scratch program `linear-mesh` (source `cw.cc` + `scenario.h`); built binary exists at `ns-3.29/build/scratch/linear-mesh/linear-mesh` (mtime Aug 12 17:43, newer than `cw.cc` mtime Aug 11 21:47 → binary is current). **[FACT]**
4. Python↔ns-3 link: ns3-gym (`contrib/opengym`, tkn-tub/ns3-gym branch `app`, commit a9ee83b74, clean tree). ns-3 is the ZMQ REQ client; Python `Ns3ZmqBridge` is the ZMQ REP server. Lock-step synchronous: one RL decision per 0.01 s of simulated time; ns-3 blocks while waiting for the action. **[FACT]**
5. State to the agent = 1 scalar: the most recent per-step frame-loss ratio `(sent−received)/sent`, taken as element 0 of a 300-float history box that ns-3 sends. The other 299 values are discarded. **[FACT]**
6. Action: actor outputs a∈[−1,1]; Python scales `real_action = 6·(a+1)/2 ∈ [0,6]`; C++ computes `CW = 2^(action+4)` and clamps to [16,1024]; MinCw AND MaxCw are both set to that CW on ALL Wi-Fi devices via one wildcard `Config::Set` → one global CW shared by AP and all STAs. **[FACT]**
7. Reward: per-step received Mbit × 10 ÷ (5×150×envStepTime), held at the last value if outside [0,1]. Global (all flows pooled). **[FACT]**
8. W&B: `wandb.init(project="contention_window", entity="sohanroy676-vasavi-college-of-engineering")` (entity from `config.py`); 17 step-level metrics (incl. Chosen CW, collision rate, throughput, fairness, actor/critic losses) + episode metrics; single run, single agent. **[FACT]**
9. Multi-AP: NOT implemented anywhere. All state/action/reward plumbing is single-AP, single-CW, single-agent. §14 maps what would change. **[FACT]**
10. Notable code quirks (reported, NOT fixed): `jain_index()` uses uninitialized `nominator`/`denominator` doubles (C++ UB, cw.cc L101-102); initial MinCw=MaxCw=0 for the first ~1 s of each episode (before the first RL action at t=1.0); reward normalization constant `5*150` hard-coded; `sentMbytes` in extra-info is actually Mbit. **[FACT — code state]**

---

# 2. Actual Workspace Structure

Root `/home/gloomyleader/college/major/ns-allinone-3.29` **[FACT, `ls`]**:
- Standard ns-allinone-3.29 tarball layout: `bake/`, `netanim-3.108/`, `pybindgen-0.17.0.post58+ngcf00cc0/`, `ns-3.29/`, `build.py`, `constants.py`, `util.py`, `.config`, `README`.
- `.config` (allinone): ns-3 branch `ns-3.29`, pybindgen `0.17.0.post58+ngcf00cc0`, netanim `3.108`. **[FACT]**
- Root is NOT a git repository (`git rev-parse` fails). **[FACT]**
- `docs/` — empty before this audit (created 2026-09-15); holds this report. **[FACT]**

`ns-3.29/` **[FACT]**:
- `VERSION` = `3.29` → ns-3 version 3.29, ns-allinone 3.29.
- Waf build; `build/` artifacts include `build/lib/libns3.29-opengym-debug.so` and `libns3.29-wifi-debug.so` (debug-profile build for these modules) and `build/scratch/linear-mesh/linear-mesh` + `cw.cc.3.o` → the OSCAR ns-3 scenario IS built and up to date.
- `contrib/opengym/` = ns3-gym, independent git repo (branch `app`, HEAD a9ee83b74fee405cf7712e55d1dcd458e5f14c14, 2022-07-14, clean tree); `VERSION`="release 1.0.0", `NS3-VERSION`="release ns-3.29".
- `scratch/linear-mesh/` = THE OSCAR PROJECT (own git repo, §3).
- `venv/` = Python 3.7.16 virtualenv used for all training (confirmed by `venv/bin/python --version` and `wandb-metadata.json`).

OSCAR project files at `ns-3.29/scratch/linear-mesh/` **[FACT, `ls`]**:

| File | Role |
|---|---|
| `README.md` | upstream README: clone into ns3-gym `scratch/linear-mesh`, edit wandb entity, run `python OSCAR_train.py` / `CCOD_train.py` / `standard_test_and_ccod_train.py` |
| `OSCAR_train.py` | THE OSCAR training entry point (currently working path) |
| `CCOD_train.py`, `standard_test_and_ccod_train.py` | CCOD baseline training (uses `agents/ddpg`, from wwydmanski/RLinWiFi) |
| `test_oscar_connection.py` | env smoke test (no RL) |
| `wrappers.py` | `EnvWrapper`: spawns ns-3 via `waf --run "linear-mesh ..."`, wraps `ns3env.Ns3Env`; multi-instance scaffolding (ports list) but 1 env used |
| `config.py` | 1 line: `wandb_entity = "sohanroy676-vasavi-college-of-engineering"` |
| `exceptions.py` | `AlreadyRunningException` |
| `cw.cc` | ns-3 scenario C++: observation/action/reward/CW + topology + main() |
| `scenario.h` | `Scenario`, `BasicScenario`, `ConvergenceScenario`, `ScenarioFactory`, traffic installation |
| `agents/our_ddpg/` | OSCAR DDPG: `Our_DDPG.py` (Actor/Critic/DDPG), `utils.py` (ReplayBuffer), `preprocessor.py`, `loggers.py` (comet_ml/wandb Logger) |
| `agents/ddpg/` | CCOD DDPG (LSTM actor/critic, Teacher loop + its own EnvWrapper, loggers, preprocessor) — NOT part of the OSCAR path |
| `wandb/` | 9 local run dirs (2026-08-13 20:13→22:30 local), latest `run-20260813_223026-ryyfog6q` (program `OSCAR_train.py`) |
| `results/` | empty (no checkpoints: `--save_model` defaults False; no `models/` dir exists) |
| `CW_data.csv` | per-step CW dump from ns-3 (`SimulationTime,CW`), gitignored |
| `__pycache__/` | `cpython-37` bytecode → Python 3.7 usage |
| `.gitignore` | ignores `__pycache__/`, `*.pyc`, `CW_data.csv`, `results/`, `models/`, `wandb/` |

ns3gym is ALSO installed into the venv (`venv/lib/python3.7/site-packages/ns3gym/`, version 0.1.0); its `ns3env.py`/`start_sim.py` are byte-identical (md5-verified) to the `contrib/opengym/model/ns3gym/ns3gym/` copies. Imports in the OSCAR path (`from ns3gym import ns3env`) resolve to the installed copy. **[FACT md5; INFERENCE resolution]**

No OSCAR/`linear-mesh` references exist outside `scratch/linear-mesh` in `scratch/` or `contrib/`. **[FACT, grep]**

---
# 3. Git / Repositories

**Repo 1 — OSCAR** (`ns-3.29/scratch/linear-mesh/.git`) **[FACT]**:
- remotes: `origin` = `https://github.com/sohanroy676/OSCAR-contention-window-RL.git`; `upstream` = `https://github.com/raoulraft/OSCAR-contention-window-RL.git`
- branches: `main` = b595c67 (tracks origin/main = upstream tip); `major-project` = CURRENT (checked out), HEAD 6e90e62
- history: `major-project` = `main` + 2 commits (merge-base = b595c67 → clean linear lineage):
  - `fce0e10` 2026-08-12 20:51 +0530 "Set up OSCAR baseline configuration" — touches `.gitignore`, `CCOD_train.py`, `OSCAR_train.py`, `config.py`, `standard_test_and_ccod_train.py`, `test_oscar_connection.py`
  - `6e90e62` 2026-08-13 20:37 +0530 "chore(wandb): update wandb entity" — `config.py`, `.gitignore`
- working tree (uncommitted, 3 files):
  - `OSCAR_train.py`: EPISODE_COUNT 12→3; nWifi loop `[40,45,50]`→`[40]`
  - `agents/our_ddpg/loggers.py`: + tensor `.detach().cpu().item()` fix before `wandb.log` (losses are torch tensors)
  - `wrappers.py`: + `from exceptions import AlreadyRunningException`
- no stashes, no submodules. wandb run metadata records commit 6e90e62.

**Repo 2 — ns3-gym** (`ns-3.29/contrib/opengym/.git`) **[FACT]**:
- remote origin = `https://github.com/tkn-tub/ns3-gym.git`
- branch `app`, up to date with origin/app, HEAD a9ee83b74 "Update README.md" (2022-07-14)
- working tree clean — NO local modifications to ns3-gym C++ or Python.

---

# 4. Versions and Dependencies

## A. Explicitly specified by project files / artifacts **[FACT]**

| Component | Version | Evidence |
|---|---|---|
| ns-3 | 3.29 | `ns-3.29/VERSION`; allinone `.config` |
| ns-allinone | 3.29 | directory name, `build.py`, `.config` |
| ns3-gym / OpenGym (C++) | release 1.0.0 (for ns-3.29) | `contrib/opengym/VERSION`, `NS3-VERSION` |
| ns3gym (python pkg) | 0.1.0 | venv `site-packages/ns3gym-0.1.0-py3.7.egg-info` |
| Python | 3.7.16 | `venv/bin/python --version`; `wandb-metadata.json`; `cpython-37` pyc files |
| torch | 1.13.1+cu117 (CUDA 11.7) | `venv/.../torch/version.py` |
| gym | 0.26.2 | `pip list` |
| numpy | 1.21.6 | `pip list` |
| protobuf (python) | 3.20.3 | `pip list` |
| pyzmq | 26.2.1 | `pip list` |
| wandb | 0.18.7 | `pip list`; run `config.yaml` `cli_version` |
| comet_ml | 3.52.1 | `pip list` (imported by both loggers.py) |
| pandas | 1.3.5 | `pip list` (loggers use `DataFrame.append` — removed in pandas ≥2.0; do NOT upgrade blindly) |
| matplotlib | 3.5.3 | `pip list` |
| tqdm | 4.68.2 | `pip list` |
| CUDA runtime wheels | cudnn-cu11 8.5.0.96, cublas-cu11 11.10.3.66, nvrtc/runtime-cu11 11.7.99 | `pip list` |
| GPU (train machine) | NVIDIA GTX 1650 Ti 4 GB; driver CUDA 13.1; WSL2 | latest run `wandb-metadata.json` |

## B. Inferable from configuration/source **[INFERENCE]**
- torch CUDA build = +cu117 (`version.py`); GPU is used when available (`Our_DDPG.py` L8 `torch.device("cuda" if torch.cuda.is_available() else "cpu")`).
- C++ link deps: `contrib/opengym/wscript` L43-44 links `-lzmq -lprotobuf` and requires HAVE_ZMQ + ENABLE_PROTOBUF + ENABLE_PROTOC; the binary exists → system libzmq + libprotobuf present and compatible.
- ns3gym 0.1.0 was installed from the contrib tree (byte-identical files).
- There is NO project-level pinned requirements file for `linear-mesh`; the de-facto environment is the venv `pip list` captured above. `ns3gym/requirements.txt` is unpinned (pyzmq, numpy, protobuf, gym).

## C. Not determinable locally — run these read-only commands later **[UNKNOWN]**
- `dpkg -l | grep -E 'libzmq|protobuf'` and `g++ --version` (system C++ lib/toolchain versions)
- `venv/bin/python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"`
- `venv/bin/python -c "import ns3gym, ns3gym.messages_pb2 as pb; print(ns3gym.__file__, pb.__file__)"`

---
# 5. Current OSCAR Execution Flow (the working path)

Launch: from `ns-3.29/scratch/linear-mesh`, `python OSCAR_train.py` (venv python) — README documents the same. **[FACT]**

1. **Config** — `OSCAR_train.py` L29-58: scenario="basic", agent "OurDDPG", simTime=15, stepTime=0.01, history_length=300, steps_per_ep=1500, EPISODE_COUNT=3 (local edit; committed value 12), nWifi loop `[40]` (committed `[40,45,50]`); `sim_args` becomes the ns-3 CLI args.
2. **wandb.init** — L60: run name `"40 OurDDPG No Mean Window|No Std Window 1 OBS [128x128]"`, entity=`config.wandb_entity`, project=`"contention_window"`, tags, reinit=True.
3. **Logger / Preprocessor** — L62-64 (`agents/our_ddpg/loggers.py`, `agents/our_ddpg/preprocessor.py`).
4. **Env creation** — L69 `EnvWrapper(threads_no=1, **sim_args)` (`wrappers.py`):
   - L19: port = `13968 + randint(0..39999)` (one per env; collision possible across runs)
   - L25: `__init__` calls `self.run()` → `subprocess.Popen(['bash','-c', cmd])` with cmd = `<waf> --run "linear-mesh --simTime=15 --envStepTime=0.01 --historyLength=300 --agentType=continuous --scenario=basic --nWifi=40 --openGymPort=P"` (`_craft_commands` L40-56; `find_waf_path` walks up from CWD to ns-3.29)
   - L27: `ns3env.Ns3Env(port=P, stepTime=0.01, startSim=0, simSeed=0, simArgs=..., debug=False)` → `Ns3ZmqBridge` binds ZMQ **REP** on `tcp://*:P` and waits (`ns3env.py` L39-68)
5. **ns-3 side** (`build/scratch/linear-mesh/linear-mesh`, from `cw.cc`):
   - `main()` L433+: parses args; defaults: mcs=11, channelWidth=20, guardInterval=800 ns, offeredLoad="150" (Mbps), useRts=false, rng=1, warmup=1, simSeed=-1, CW=0 (L435-451)
   - builds topology (1 AP + nWifi STAs), connects `PhyTxBegin` trace → `packetSent` (L527); UdpServer `Rx` traces → `packetReceived`
   - `set_sim` L391-425: creates `OpenGymInterface(openGymPort)` — ZMQ **REQ** client connecting to `tcp://localhost:P` (`opengym_interface.cc` L81, L163-164) — registers 7 callbacks (action space, obs space, game over, observation, reward, extra info, execute actions) L403-409
   - schedules first `ScheduleNextStateRead` at **t=1.0 s** (L418), self-rescheduling every `envStepTime` (L248-252)
6. **Handshake** — ns-3 sends `SimInitMsg` (spaces) → Python `initialize_env` (`ns3env.py` L150-165) → `SimInitAck`. **[FACT]**
7. **Main loop** — `OSCAR_train.py` L137-196, EPISODE_COUNT=3 episodes:
   - `env.run()` inside try → raises `AlreadyRunningException` (env already running) → caught (L140-143)
   - `state = env.reset()` (L147): episode 1 → bridge already has first obs; episodes 2+ → previous `env.close()` (L198) set `SCRIPT_RUNNING=False`, so `env.run()` next episode spawns a NEW ns-3 process on the SAME port; `Ns3Env.reset` sees `envDirty`, closes old bridge (kills ns-3 pid, `ns3env.py` L82-97, L405-422) and binds again → **one ns-3 process per episode**
   - per step (1500/episode):
     a. action: if `time_step < 300` → `U(0,6)` random; else `(policy.select_action(state) + N(0, 0.1·max_action))` clipped to [−1,1]; `real_action = 6·(a+1)/2 ∈ [0,6]` (L155-165)
     b. `env.step(real_action)` (L168) → `EnvWrapper.step` → `Ns3Env.step` → ZMQ → ns-3 (blocked in `NotifyCurrentState`) → `MyExecuteActions` applies CW → ns-3 advances 0.01 s → sends `EnvStateMsg(obs, reward, gameOver, info)` → Python returns `(next_obs[300 floats], reward, done=False, info="mb|CW|stations|jain")`
     c. Preprocessor windowed mean/std — ONLY for W&B logging (L169, L182)
     d. RL state = `next_state[0][:1]` → latest loss ratio (L171-172)
     e. `replay_buffer.add(state, action(−1..1 domain), next_state, reward, done)` (L176)
     f. if `time_step >= 300`: `policy.train(replay_buffer, 32)` EVERY step (L188-189)
     g. if `step > 300`: `logger.log_round(...)` (L180-182)
   - after episode: `logger.log_episode` (L197), `env.close()` (L198)
8. `run.finish()` (L199). `Logger.end()` is NEVER called in the OSCAR path. **[FACT]**

Synchronization: ns-3 blocks on ZMQ REQ recv while Python decides; Python blocks on next obs → strictly synchronous, 1 RL decision / 0.01 s sim time / 1500 decisions per 15 s episode. **[FACT]**

---

# 6. Current RL Architecture (`agents/our_ddpg/Our_DDPG.py`)

- Algorithm: **DDPG** ("re-tuned"; header cites arXiv:1509.02971). NOT TD3 — `policy_noise`/`noise_clip`/`policy_freq` argparse entries exist but are unused for OurDDPG. **[FACT]**
- **Actor** (L14-33): MLP 1→128→128→1, ReLU hidden, output `max_action·tanh(x)`, max_action=1 → range [−1,1]. (Commented-out 256×256 variant.)
- **Critic** (L36-52): MLP (1+1)→128→128→1, ReLU, linear output.
- **DDPG class** (L55-108):
  - `actor` + `actor_target` (deepcopy), `critic` + `critic_target` (deepcopy) → **target Actor/Critic networks exist**
  - optimizers: Adam lr_actor=4e-4, lr_critic=4e-3 (hard-coded in the file, OSCAR_train kwargs only pass discount/tau)
  - discount=0.7, tau=1e-3 (comments show originals 0.99/0.005)
  - `train(replay_buffer, batch_size=32)` L75-108: standard DDPG — target Q via `critic_target(next, actor_target(next))`, MSE critic loss, DPG actor loss `−Q(s, actor(s)).mean()`, then **soft updates of both target nets every train() call** (every env step after warmup)
- **Replay buffer** (`agents/our_ddpg/utils.py`): numpy arrays, max_size=1e6, uniform sampling; stores the action in the [−1,1] domain (OSCAR_train.py L176 stores `action`, not `real_action`). **[FACT]**
- **Exploration** (OSCAR_train.py L155-165): first 300 GLOBAL steps (`start_timesteps`): action ~ U(0,6); afterwards actor + N(0, (0.1)²) clipped [−1,1], scaled ×3+3 → [0,6]. **[FACT]**
- **Checkpoints**: `save/load` (torch state_dicts) L111-126; `--save_model` defaults False and no `./models` dir exists → no checkpoints saved so far. **[FACT + INFERENCE]**
- Separate second implementation `agents/ddpg/` (LSTM actor/critic, OU noise + decaying NormalNoise, `Teacher.train` loop, `update_every` stepping) used ONLY by `CCOD_train.py` / `standard_test_and_ccod_train.py` (CCOD baseline, from wwydmanski/RLinWiFi). Not part of the OSCAR path. **[FACT]**

---
# 7. Observation (state) — exact

**C++ side** (`cw.cc`):
- Observation space (L58-70): Box, shape `[history_length]` = [300], dtype float, low 0.0, high 10.0 (declared bounds are decorative).
- `recordHistory()` (L254-293) maintains a deque of the last `history_length` per-step loss ratios:
  - `received = g_rxPktNum − last_rx` — UdpServer `Rx` traces of ALL flows (sinks at the AP)
  - `sent = g_txPktNum − last_tx` — `PhyTxBegin` trace of ALL nodes (STAs + AP)
  - `ratio = (sent − received) / sent`, pushed to the front of the deque
- `MyGetObservation` (L217-240): returns the deque as a box; values outside [−100,100] → 0; zero-padded to 300.
- Counters: `packetReceived` (L295-299) increments `g_rxPktNum` per received UDP packet; `packetSent` (L301-304) increments `g_txPktNum` per PHY transmission of ANY node. **[FACT]**

**Python side**:
- `env.reset()`/`env.step()` return the 300-float vector; OSCAR_train uses ONLY element 0 (`state_dim=1`; L105, L148, L171) → the agent sees the single most recent loss ratio. **[FACT]**
- Normalization: none beyond the ratio naturally lying in [0,1]. The Preprocessor (`agents/our_ddpg/preprocessor.py`, window=150, stride=75, clip [0,1]) output is used ONLY for W&B metrics "Observation 0/1", NOT as agent input. **[FACT]** → consistent with the run name "No Mean Window|No Std Window 1 OBS". **[INFERENCE]**
- History: 300 samples transmitted but discarded → the agent is effectively memoryless (1-D state). **[FACT]**
- Scope: fully AGGREGATED over the WLAN (one global packet counter); no per-station values. **[FACT]**

# 8. Action and CW Control — exact

- Action space (`cw.cc` L75-87): Box [1] float, low 0.0 high 10.0 (not enforced).
- Actor output a ∈ [−1,1] (tanh). `OSCAR_train.py` L163: `real_action = real_max_action * (action + 1) / 2` with `real_max_action = 6` → [0,6]. Random warmup: `np.random.uniform(0,6)` (L156).
- `EnvWrapper.step` → `Ns3Env.step(actions[i].tolist())` → ZMQ → `MyExecuteActions` (`cw.cc` L146-186):
  - `type == "continuous"` → **`CW = pow(2, action + 4)`** (L158-161)
  - global clamp `CW = min(1024, max(16, CW))` (L172-175)
  - → CW ∈ {16, 32, …, 1024} (2⁴…2¹⁰). The agent effectively chooses the exponent in [0,6].
- Application (L178-184, only if `!dry_run`):
  `Config::Set("/$ns3::NodeListPriv/NodeList/*/$ns3::Node/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::RegularWifiMac/BE_Txop/$ns3::QosTxop/MinCw", UintegerValue(cwmin))` and the same for MaxCw.
  → wildcard matches EVERY WifiNetDevice on EVERY node (AP + all STAs); `cwmin == cwmax == CW` (they are EQUAL). ONE global CW for the whole BSS. **[FACT]**
- ns-3 API: the attribute system — attributes `MinCw`/`MaxCw` of `ns3::Txop` (`src/wifi/model/txop.cc` L48-50); setters `Txop::SetMinCw`/`SetMaxCw` (L175-193) store the value and call `ResetCw()` when changed. No custom MAC code exists in the repo — stock ns-3.29 wifi is used. **[FACT]**
- Initial CW: `main` binds `--CW` (L458, default 0); `set_nodes` sets MinCw=MaxCw=CW=0 for `!dry_run` (L378-382). ns-3.29 `Txop::SetMinCw` stores 0 verbatim (no guard) → **MinCw=MaxCw=0 during the first ~1.0 s of each episode** (first RL action lands at t=1.0). The Python wrapper never passes `--CW` (nor `--mcs`, `--channelWidth`, `--guardInterval`, `--offeredLoad`, `--rng`, `--seed`, `--useRts`, `--nonZeroStart`) → cw.cc defaults apply. **[FACT — quirk reported, NOT fixed]**
- dry_run (802.11 baseline): sets MinCw=16, MaxCw=1024 (L383-388) and still executes the received action on the C++ variable but skips the Config::Set → BEB continues. **[FACT]**
- CW logging: every applied CW appended to `scratch/linear-mesh/CW_data.csv` (L176, header `SimulationTime,CW`); also sent in extra-info → W&B "Chosen CW". **[FACT]**
- Reset/restore: nothing restores CW defaults in C++ between decisions; per-episode reset happens only because the process restarts. Python has no CW reset logic. **[FACT]**
- **One action controls ALL stations (and the AP)** — exactly one action value, one CW. **[FACT]**

# 9. Reward — exact

`MyGetReward` (`cw.cc` L188-211), called on every `NotifyCurrentState`:
```
res    = g_rxPktNum - last_packets                     // packets received this step
reward = res * (1500-20-8-8) * 8.0 / 1024 / 1024       // Mbit received this step
         / (5 * 150 * envStepTime) * 10
if (ticks <= 2*envStepTime) return 0.0                 // first 2 steps
if (reward > 1.0f || reward < 0.0f) reward = last_reward
last_reward = reward; return last_reward               // hold within [0,1]
```
- Scope: **GLOBAL** — `g_rxPktNum` counts received packets of ALL flows at the AP. Not per-station, not per-AP. **[FACT]**
- Raw vs normalized: pseudo-normalized to [0,1] via the hold trick. **[FACT]**
- Contributions: UDP goodput only (received packets). Collisions/losses are NOT directly rewarded; they enter through the observation (loss ratio) and through reduced goodput. **[FACT]**
- Units: comment says "bits/s" but the formula is Mbit-per-step scaled by a hard-coded constant (5·150·0.01 = 7.5 at stepTime 0.01, ×10) → effective reward ≈ 1.333 × Mbit received in the last 10 ms. **[FACT math]**
- Python: `env.step` returns it as a scalar; `episode_reward` accumulates it (OSCAR_train L179). **[FACT]**

---
# 10. ns-3 Network Topology (`cw.cc` + `scenario.h`) **[FACT unless noted]**

- **APs: exactly ONE** — `wifiApNode.Create(1)` (`set_phy`, cw.cc L312); `wifiApNode.Get(0)` used in every scenario (scenario.h L223, L235, L239).
- **Stations:** nWifi STA nodes (cw.cc L311); nWifi=40 in the current `OSCAR_train.py`.
- **Wi-Fi standard:** `WIFI_PHY_STANDARD_80211ax_5GHZ` (L504). ns-3.29 default for this standard = 5210 MHz / channel 42 (`src/wifi/model/wifi-phy.cc` L795-800); channel number NOT overridden in the scenario.
- **Rate:** `ConstantRateWifiManager`, DataMode = ControlMode = `HeMcs11` (L506-509).
- **Channel width:** 20 MHz — `Config::Set(.../Phy/ChannelWidth)` (L346; default arg 20).
- **Guard interval:** 800 ns default (L440; `phy.Set("GuardInterval", ...)` L323).
- **Propagation:** `YansWifiChannel` + `MatrixPropagationLossModel` with `SetDefaultLoss(50)` dB + `ConstantSpeedPropagationDelayModel` (L308-317).
- **Mobility:** `ConstantPositionMobilityModel`; AP at (0,0,0), **ALL STAs at (1,0,0)** — co-located 1 m from the AP, 0 m apart pairwise (L349-359); everyone gets the default 50 dB loss.
- **MAC:** `StaWifiMac` (ActiveProbing=false, `BE_MaxAmpduSize=0` → NO A-MPDU aggregation on STAs, L331-334); `ApWifiMac` (EnableBeaconJitter=false, L339-341; AP aggregation attribute not explicitly set).
- **RTS/CTS:** disabled (`useRts=false` default; if true → `RtsCtsThreshold=0`, L491-494).
- **IP:** 192.168.1.0/24 single subnet (L370-376); ARP cache pre-populated (scenario.h L168-217); `Ipv4GlobalRoutingHelper::PopulateRoutingTables`.
- **Traffic:** per-STA ONE uplink flow STA_i → AP: `OnOffHelper` over **UDP**, constant rate `offeredLoad` = "150" Mbps, packet 1464 bytes (1500−20−8−8), TOS 0x70 (AC_BE), ports starting at 1025 incrementing per flow; `UdpServer` sink on the AP; sink `Rx` trace → `packetReceived` (scenario.h L125-166). **NO downlink traffic.**
- **App start/stop:** BasicScenario — all flows start 0.0 s, stop `simulationTime + 2 + envStepTime·history_length` (L219-225). ConvergenceScenario — first 5 STAs at t=0, remaining STAs staggered every `simulationTime/(nWifi−4)` (L227-247). OSCAR_train uses **"basic"**; convergence is available but unused.
- **Simulation bounds:** `Simulator::Stop(simulationTime + end_delay + 1.0 + envStepTime·(history_length+1))` (L421); `non_zero_start` = false → end_delay = 0.
- **FlowMonitor:** `InstallAll()`, StartTime = warmup = 1 s (`set_sim` L393-394) — used for the final per-flow throughput print (L542-554) and `jain_index()`.
- **Randomness:** `RngRun = 1` always (default; wrapper passes no rng/seed), `simSeed = −1` → no seed set. **[FACT]** Variation across episodes relies on process restarts + the CW feedback loop. **[INFERENCE]**
- **Decision timing:** `envStepTime` = 0.01 s → one RL decision per 10 ms of sim time; 1500 decisions per 15 s episode; first decision at t=1.0 s. **[FACT]**

**Bottom line: ONE AP, ONE global CW shared by AP and all 40 STAs, ONE RL agent, ONE env, ONE ZMQ port, ONE global reward.**

# 11. W&B Metrics (local code + local run files; no account access)

**wandb.init call sites [FACT]:** `OSCAR_train.py` L60; `CCOD_train.py` L76; `standard_test_and_ccod_train.py` L77 — all project `"contention_window"`, entity from `config.py` = `"sohanroy676-vasavi-college-of-engineering"`. The `Logger` class (`agents/our_ddpg/loggers.py`; identical copy in `agents/ddpg/loggers.py`) is a dual comet_ml/wandb backend; wandb is active because `comet_ml=False` is passed.

**Per-step metrics** (`Logger.log_round`, called when step>300 in OSCAR_train):

| Metric | Meaning | Source |
|---|---|---|
| Current Collision Rate | latest per-step frame-LOSS ratio (state[0]); NOT a MAC collision counter | Python state |
| Round reward | reward of current step (np.mean of a scalar) | env |
| Per-ep reward | cumulative episode reward so far (running) | env |
| Megabytes sent | running total (actually Mbit — mislabel) | info[0] accum |
| Round megabytes sent | Mbit received in the last step | info[0] |
| Chosen CW | current CW after this step's action | info[1] |
| Station count | active station count (= nWifi in basic scenario) | info[2] |
| Current throughput | mean of last 100 `round_mb/step_time` (Mb/s) | computed |
| Fairness index | Jain index over per-flow throughputs (C++ `jain_index`) | info[3] |
| Observation 0 / Observation 1 | windowed mean / std of the raw obs (preprocessor) | preprocessor |
| actor_loss / critic_loss | DDPG losses (tensor→float via the uncommitted detach fix) | policy |

- Commit pattern: all `commit=False` except Fairness index (commit=True) and — per observation loop iteration — `log_metrics(loss, commit=True)` → actor_loss+critic_loss each committed twice per step. **[FACT]**
- **Per-episode** (`log_episode`): Cumulative reward, Speed (= sent_mb/simTime), MB sent; counters reset. **[FACT]**
- **Parameters** (`begin_logging`): Episode count, Steps per episode, theta=None, sigma=None, Step time. **[FACT]**
- **Frequency:** per RL step (~1470 of 1500 steps/episode) + per-episode; latest local run reached `_step`=18006. Values are per-step and per-episode; **reward IS logged**, **throughput IS logged**, **collision/loss rate IS logged** (as loss ratio + fairness), **CW IS logged** ("Chosen CW" + local CW_data.csv), **actor/critic losses ARE logged**. **[FACT]**
- **Multi-agent:** NOT supported in the OSCAR path — one run, one Logger, scalar metrics. `log_round` does `np.mean` over info rows, hinting the wrapper was originally written for N parallel instances (CCOD/RLinWiFi lineage), but OSCAR_train feeds it a single env. **[FACT + INFERENCE]**
- **Local run artifacts:** `wandb/` holds 9 run dirs (2026-08-13 20:13→22:30 local). Latest `run-20260813_223026-ryyfog6q` (`OSCAR_train.py`, commit 6e90e62, python 3.7.16, GTX 1650 Ti) final summary (`files/wandb-summary.json`): Current throughput 37.43, Speed 30.11, MB sent 451.62, Chosen CW 408, Station count 40, Fairness 0.9994, Current Collision Rate 0.5676, Per-ep reward = Cumulative reward 750.33, actor_loss −1.349, critic_loss 0.00279, Observation 0 = 0.5670, Observation 1 = 0.0274, _step 18006, runtime ≈ 3673 s. **[FACT — local file]**
- Dashboard-side truth (how the 9 runs map to the wandb.ai project, history curves) — NOT accessible from this machine. **[UNKNOWN → §16]**

---
# 12. Comparison with Original OSCAR

Column "Original OSCAR paper" = what the ICC-2023 paper / upstream README describe, from repo docs and paper knowledge; several paper-side details are **[PAPER-KNOWLEDGE]** and NOT verifiable from this workspace. The implementation column is **[FACT]**. Where they differ, the implementation is authoritative for extension work.

| Feature | Original OSCAR paper | Current implementation | Difference / unknown |
|---|---|---|---|
| Topology | 1 AP, N STAs, uplink UDP | 1 AP, N=40 STAs, uplink UDP OnOff 150 Mbps | match |
| Number of APs | 1 | 1 | match |
| Stations | several, varied (paper) [PAPER-KNOWLEDGE] | 40 now; committed loop [40,45,50] | exact paper set [UNKNOWN] |
| Observation | windowed mean/std stats of loss-ratio history | RAW scalar = latest loss ratio; 300-float history sent but discarded; mean/std computed only for W&B logging | **DIFFERS** (run name admits "No Mean Window\|No Std Window 1 OBS") |
| Action | CW exponent, continuous | actor ∈[−1,1] → ×3+3 → [0,6] → CW=2^(a+4), clamp [16,1024] | same idea |
| CW mapping | AP's CW applies to its stations | MinCw=MaxCw=CW via ONE wildcard Config::Set on ALL devices (AP included) | match (single global CW) |
| Reward | normalized throughput | Mbit received ×10 ÷ (5·150·0.01), hold [0,1] | same spirit; constant hard-coded |
| DDPG / Actor-Critic | DDPG | DDPG (Our_DDPG): 128×128 MLP, targets, per-step training | match |
| Decision epoch | periodic (10 ms) | 0.01 s envStepTime; first decision at t=1.0 s | match |
| Replay buffer | yes | numpy replay, max 1e6 | match |
| Target networks | yes | actor_target + critic_target, soft update every step | match |
| Exploration | noise | 300 random-warmup steps, then Gaussian σ=0.1 on [−1,1] | match (RLinWiFi lineage) |
| Training | episodes | 3 ep × 1500 steps (local edit; upstream 12 ep) | config only |
| Traffic | uplink UDP saturation | uplink UDP OnOff 150 Mbps, 1464 B, no downlink | match |
| PHY/MAC | 802.11ax [PAPER-KNOWLEDGE] | 802.11ax 5 GHz (5210 MHz), 20 MHz, HeMcs11, GI 800 ns, no STA A-MPDU, no RTS/CTS, all STAs at one point | match; exact paper GI/MCS [UNKNOWN] |
| W&B metrics | throughput / CW / reward curves | 17 step metrics + episode metrics (§11) | superset |
| Multi-AP | NOT in paper | NOT in code | match (absent) |

# 13. Single-AP Assumptions in the Code (each = risk for multi-AP)

**C++ (`cw.cc`, `scenario.h`)** **[FACT]**:
1. ONE AP: `wifiApNode.Create(1)` (L312); `wifiApNode.Get(0)` everywhere.
2. ONE global CW: `uint32_t CW` file-global (L44); single `CW_data.csv` stream.
3. Wildcard `Config::Set` MinCw/MaxCw on ALL devices (L182-183; initial L380-381) — cannot target one AP's subset without path changes.
4. ONE global observation: `g_rxPktNum`/`g_txPktNum` file-globals (L92-93); traces connected once (L527; per-flow UdpServer Rx).
5. ONE history deque, ONE reward, ONE extra-info string `"mb|CW|stations|jain"` (L121-140) — 4 scalars, no AP identifier.
6. ONE `OpenGymInterface`, ONE port, ONE callback set (L402-409).
7. `jain_index()` pools ALL flows (L95-119) — no per-AP split; also uses uninitialized `nominator`/`denominator` (UB).
8. `getActiveStationCount` counts all scenario flows (scenario.h L110-117).
9. Scenario classes assign EVERY station to AP 0 (scenario.h L223/235/239); `ScenarioFactory` (L59-98) has one AP container.
10. Reward normalization constant `5*150` hard-coded (L196).

**Python (`OSCAR_train.py`, `wrappers.py`, `loggers.py`)** **[FACT]**:
11. `state_dim=1`, `action_dim=1`; one policy, one replay buffer, one wandb run.
12. Single-env indexing: `state[0][:1]` (L148, L171), scalar reward.
13. `EnvWrapper` HAS multi-env scaffolding (self.envs list, per-env ports, per-env `actions[i]` in step L65-75) — but each extra "thread" would be a FULL separate WLAN (own ns-3 process), NOT an AP of a shared network.
14. Logger: one CW/stations/fairness per step; `np.mean` over info rows (log_round L79-83) would silently AVERAGE multiple APs if reused.
15. Metric names are AP-agnostic (no per-AP prefix); single wandb run per training.
16. Hard-coded numbers: real_max_action=6, start_timesteps=300, batch 32, discount 0.7, tau 1e-3, lr 4e-4/4e-3, EPISODE_COUNT=3, nWifi [40], simTime 15, stepTime 0.01, history 300, port base `13968+randint(40000)` (collision-prone), `Logger.stations` default 5 (loggers.py L12).
17. Seeds: `rng=1`, `simSeed=−1` → identical RngRun every episode. **[FACT]**

---
# 14. Potential Multi-AP Architecture (analysis ONLY — nothing implemented)

Based ONLY on the existing code, for the mentor's framing (per-AP agents managing decentralized networks; possible local critics; possible central critic):

**Option A — one ns-3 process, N APs, per-AP OpenGym interfaces/ports:**
- `cw.cc`: build N APs; per-AP packet counters (must be separated — today `g_rxPktNum`/`g_txPktNum` are file-globals), per-AP history deque / observation / reward / info string, per-AP CW variable; **targeted** `Config::Set` paths per AP node (`/NodeList/<apNodeId>/.../MinCw`) instead of the wildcard; N `OpenGymInterface` instances (one port each) OR one interface with an N-wide action/observation Box.
- `scenario.h`: `Scenario`/`ScenarioFactory` must accept per-AP station groups (today EVERY station is installed against AP 0); `jain_index` and `getActiveStationCount` need per-AP flow subsets.
- Python: `EnvWrapper` already supports N ports/instances (`threads_no>1`) — each env would talk to ONE AP; `OSCAR_train.py` must keep a LIST of policies/replay buffers (one per AP), produce per-env actions (wrapper.step already indexes `actions[i]`), and log per-AP metric names.
- Risks: ZMQ port collisions (random ports); wrapper.step is SERIAL (APs stepped one after another → interleaved sim time); process/lifetime coupling; per-AP seed control (today rng=1 fixed).

**Option B — N separate ns-3 processes, one AP each (least C++ change):**
- Reuse `EnvWrapper(threads_no=N)`; each process = one independent single-AP WLAN.
- Python: N agents; optional central critic consumes concatenated per-AP states/actions.
- **Critical risk [INFERENCE]: separate processes cannot hear each other → NO shared channel / inter-AP contention modeling.** Only valid if APs are studied as independent scenarios.

**Central critic (MADDPG-like) add-ons, if chosen:**
- Replay storage must hold (global_state, per-agent actions, reward, next global_state) — `utils.py ReplayBuffer` is single-agent shaped.
- `Our_DDPG.train()` assumes one (s,a,r,s′) — a centralized-critic variant needs a new critic taking concatenated inputs + per-agent actor updates (new class in `agents/our_ddpg/`); Actors remain per-AP.
- Information flow ns-3→Python for a global state requires per-AP observations plus a network-wide metric — today only the single-AP 4-scalar info string exists (`MyGetExtraInfo`).

**What stays single-AP-specific regardless:** the wildcard CW Config::Set, the global counters, the hard-coded reward normalization, the 1-scalar state, and the single wandb run/metric names.

# 15. Files Likely to Require Changes Later

- **ns-3 C++:** `scratch/linear-mesh/cw.cc` (topology, per-AP CW/obs/reward, Config::Set paths, interfaces), `scratch/linear-mesh/scenario.h` (multi-AP scenarios + traffic); possibly `contrib/opengym` (if vectorized action/obs spaces are preferred).
- **Python OSCAR path:** `OSCAR_train.py` (N policies/replays, per-env loop, seeds), `wrappers.py` (verify step/reset/close for N>1), `agents/our_ddpg/Our_DDPG.py` (only if central/shared critic), `agents/our_ddpg/loggers.py` (per-AP metric names), `config.py` (entity/project).
- **Likely new components:** per-AP agent registry, central critic class, per-AP reward/obs demux, multi-port process manager, per-AP CW application helper.
- NOT touched by the extension: `agents/ddpg/` (CCOD baseline), `test_oscar_connection.py`.

# 16. UNKNOWN / NEEDS CONFIRMATION

1. **Determinable from local code — resolved in this audit** (no further action).
2. **Determinable by safe read-only commands (run later):**
   - `dpkg -l | grep -E 'libzmq|protobuf'` ; `g++ --version` — system C++ deps
   - `venv/bin/python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"`
   - `venv/bin/python -c "import ns3gym, ns3gym.messages_pb2 as pb; print(ns3gym.__file__, pb.__file__)"`
   - `git -C ns-3.29/scratch/linear-mesh log --stat -2` — review the 2 local commits in detail
   - `git fetch upstream && git log --oneline upstream/main -5` (network op; ask before running)
3. **Requires W&B information (from your dashboard):** exact project/entity as seen on wandb.ai; the run list for Aug 13 (9 local run dirs vs dashboard count); per-run history (throughput/CW/reward curves); whether any run was resumed; loss values before the detach fix.
4. **Requires project/mentor decision:**
   - multi-AP shape: N processes (isolated) vs 1 process with N APs (shared channel)
   - per-AP Actor only vs per-station Actors (explicitly NOT assumed)
   - local critic(s) + central critic? what exactly enters the central critic?
   - reward: per-AP throughput vs network-wide; fairness target per AP or global
   - simultaneous vs sequential stepping of AP envs
5. **Cannot currently be determined:** upstream repo state newer than b595c67 (needs fetch); runtime effect of the `jain_index` UB on your recorded fairness metrics; the ns-3 default channel number actually used at runtime (code says 5210 MHz / ch 42 default; a `--verbose` run would confirm — NOT run here).

# 17. Recommended Next Investigation Step

1. Get mentor sign-off on Option A vs B (§14) — this decides ~80% of the extension design.
2. Run the read-only commands in §16(2) to pin system dependency versions.
3. Export the Aug-13 W&B runs (project `contention_window`) as CSV to fix the single-AP baseline (throughput/CW/reward at 40 STAs).
4. Decide the per-AP observation redesign FIRST — the single-scalar state is the largest modeling gap vs the paper, and it must be settled before APs multiply.

--- end of audit ---

---
**Continuation (2026-09-15):** follow-up action results are in `next-actions-results-2026-09-15.md` (same directory).
