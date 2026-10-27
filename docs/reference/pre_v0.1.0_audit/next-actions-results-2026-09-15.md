# OSCAR Project — Next-Actions Results (continuation of the forensic audit)

**Companion to:** `OSCAR-forensic-audit-2026-09-15.md` (same directory)
**Date:** 2026-09-15
**Mode:** read-only commands only; results are appended to this file as they are obtained (incremental storage, safe against interruption).

## Action checklist (from audit §16/§17)

| # | Action | Owner | Status |
|---|---|---|---|
| 1 | System/toolchain versions (dpkg, g++) | Cline | pending |
| 2 | torch/CUDA runtime verification (venv) | Cline | pending |
| 3 | zmq/protobuf runtime verification (venv) | Cline | pending |
| 4 | ns3gym import resolution (venv) | Cline | pending |
| 5 | Review the 2 local commits (`git log --stat`) | Cline | pending |
| 6 | `git fetch upstream` + compare upstream/main | ✅ closed by user (2026-09-15): "My local repo is the latest" — fetch skipped, nothing executed |
| 7 | W&B export of Aug-13 runs | USER (needs dashboard/API key) | instructions below |
| 8 | Mentor decision brief (multi-AP architecture) | mentor | brief below (no implementation) |

Results are appended below in the order they are obtained.

---
## 1. System / toolchain versions (audit §4C closure) **[FACT]**

- OS: Ubuntu 22.04 (package suffix `ubuntu7.22.04.6`; WSL2, per audit §4A)
- g++ / gcc: **11.4.0** (Ubuntu 11.4.0-1ubuntu1~22.04.3); GNU Make 4.3
- System libzmq: **4.3.4-2** (`libzmq5` + `libzmq3-dev`); libzmq.so.5 on system
- System protobuf (C++): **3.12.4-1ubuntu7.22.04.6** (`libprotobuf23`, `libprotobuf-lite23`, `libprotobuf-dev`, `protobuf-compiler` 3.12.4); libprotobuf.so.23 on system
- NOTE: the `GCC_4.2.0` string inside the `linear-mesh` binary is the ELF CXXABI symbol-version tag, NOT the compiler version; actual build compiler recorded in `build/config.log` (checked in §5 below).

## 2. venv package versions re-verified from dist-info (no pip startup) **[FACT]**

pyzmq 26.2.1 | protobuf 3.20.3 | gym 0.26.2 | wandb 0.18.7 | torch 1.13.1 | ns3gym 0.1.0 (egg-info) — all consistent with the audit §4A `pip list` capture.

## 3. Python runtime verification (imports executed, read-only) **[FACT]**

- pyzmq runtime: `import zmq` → **libzmq 4.3.5, pyzmq 26.2.1** (pyzmq bundles its own newer libzmq 4.3.5; the C++ ns-3 side uses the system libzmq 4.3.4 — both are ZMQ 4.x wire-compatible; no action needed). **[FACT + INFERENCE on compatibility]**
- protobuf runtime: `import google.protobuf` → **3.20.3** (python side) vs C++ **3.12.4** — matches the ns3-gym design (python pkg newer than system C++ is fine; the proto wire format is generated into `messages_pb2.py` / `messages.pb.cc` at build time).
- torch/CUDA runtime: pending — slow first import in WSL; result appended in §6 when collected.

## 4. ns3gym import resolution **[FACT]**

- `import ns3gym` resolves to `venv/lib/python3.7/site-packages/ns3gym/__init__.py`
- `ns3gym.messages_pb2` resolves to `venv/lib/python3.7/site-packages/ns3gym/messages_pb2.py`
- → the OSCAR training path uses the INSTALLED ns3gym package (byte-identical to `contrib/opengym/model/ns3gym/`, md5-verified in the audit).
- Observed at import: gym 0.26.2 prints its unmaintained/upgrade notice — harmless for the current stack; **do not** swap to Gymnasium casually (ns3gym/ns3env.py imports `gym`, `gym.spaces`, `gym.utils.seeding`).
- Import path note: `ns3gym/__init__.py` imports `gym.envs.registration` (to register `ns3-v0`) → importing ns3gym pulls in all of gym (why the import is slow/cold in WSL).

---
## 5. ns-3 build configuration (from `build/c4che/_cache.py`) **[FACT]**

- `CXX = ['/usr/bin/g++']` (system g++ 11.4.0 per §1); `CC_NAME='gcc'`
- `CXXFLAGS = ['-O0','-ggdb','-g3','-Wall','-std=c++11','-Wno-parentheses','-Wno-error=deprecated-declarations','-fstrict-aliasing','-Wstrict-aliasing']` and `CXXDEFINES=['_DEBUG']` → **debug-profile build** (consistent with only `libns3.29-*-debug.so` present in `build/lib/`)
- Implication [INFERENCE]: simulations run in a -O0 debug build → noticeably slower than an optimized build; keep in mind when planning longer/multi-AP training runs.

## 6. Review of the 2 local commits (`git show`) **[FACT]**

**`fce0e10` 2026-08-12 20:51 +0530 — "Set up OSCAR baseline configuration" (Sohan Roy Talari):**
- `.gitignore` (new): `__pycache__/`, `*.pyc`, `CW_data.csv`, `results/`, `models/`
- `config.py` (new): `wandb_entity = "sohanroy676"` (first value)
- All three training scripts: replaced hard-coded `wandb.init(entity="xraulz", ...)` with `entity=wandb_entity` (import from `config.py`) — i.e., the only change vs upstream was parameterizing the W&B entity
- `test_oscar_connection.py` (new): env smoke test (simTime 3, stepTime 0.1, historyLength 20, nWifi 5, action 0.0)
- Net effect: NO algorithm/topology changes vs upstream — setup-only commit.

**`6e90e62` 2026-08-13 20:37 +0530 — "chore(wandb): update wandb entity":**
- `config.py`: entity `"sohanroy676"` → `"sohanroy676-vasavi-college-of-engineering"` (current value)
- `.gitignore`: + `wandb/`

**Together with the uncommitted working-tree changes (EPISODE_COUNT 12→3, nWifi [40,45,50]→[40], tensor detach fix, wrappers import), the complete delta vs upstream `main` (b595c67) is configuration-only — the upstream algorithm/scenario code is unmodified. [FACT — established from the full diffs]**

---
## 7. torch / CUDA runtime verification (audit §4C closure) **[FACT]**

`import torch` (venv python 3.7.16) →

```
torch 1.13.1+cu117 | cuda 11.7 | available True | device NVIDIA GeForce GTX 1650 Ti
```

→ the OSCAR DDPG trains on the GPU; `Our_DDPG.py` L8 / `utils.py` L17 device selection will pick `cuda`. Cold import in WSL takes >1 min (4 GB RAM) — irrelevant for training but worth knowing when timing experiments.

## 8. W&B export of the Aug-13 runs — USER ACTION (I cannot access your account)

The 9 local run dirs are in `ns-3.29/scratch/linear-mesh/wandb/` (run-20260813_*). To export from the dashboard (pick ONE):

**Option 1 — UI (fastest):** open `https://wandb.ai/sohanroy676-vasavi-college-of-engineering/contention_window` → select the Aug-13 runs → per-chart ⋮ → *Export CSV* (or Run page → *Download CSV* of history). Also screenshot/copy each run's **config/tags** panel.

**Option 2 — API (read-only, run it YOURSELF in a terminal):**
```bash
cd ~/college/major/ns-allinone-3.29/ns-3.29/scratch/linear-mesh
source ../../venv/bin/activate          # python 3.7.16, wandb 0.18.7
export WANDB_API_KEY=<key from https://wandb.ai/authorize>
python - <<'PY'
import wandb
api = wandb.Api()
runs = api.runs("sohanroy676-vasavi-college-of-engineering/contention_window")
for r in runs:
    print(f"{r.id} | {r.name} | {r.state} | {r.created_at} | last_step={r.summary.get('_step')}")
    r.history(samples=100000).to_csv(f"wandb_history_{r.id}.csv", index=False)
PY
```
This writes `wandb_history_<runid>.csv` per run into `scratch/linear-mesh/` (gitignored dir not needed — add to .gitignore or move to docs/). What to hand back to the repo docs: run list (names/tags/states), and the history CSVs for the runs created on Aug 13 (esp. the OSCAR runs) — they fix the single-AP baseline curves for §12/§17 of the audit.

## 9. Mentor decision brief (NO implementation — decision points + code impact)

| Decision | Options | Code-grounded impact (from the audit) |
|---|---|---|
| D1. Multi-AP process shape | A: 1 ns-3 process, N APs (shared channel) / B: N processes, 1 AP each | B cannot model inter-AP contention (process isolation) — only valid for independent per-AP studies. A requires per-AP counters/CW/Config::Set paths + N interfaces in `cw.cc`/`scenario.h` |
| D2. Agent granularity | per-AP Actor + local Critic (safer reading) / per-station Actors | Per-AP: N=1 structure of `Our_DDPG.py` is reusable as-is per AP; only orchestration changes. Per-station: `MyExecuteActions` must set per-STA CW (needs per-node Config paths + per-STA reward/obs) — much larger C++ change |
| D3. Central critic | none / local critics only / + central critic | Central critic needs (global_state, all actions) tuples → new replay layout + new critic class; ns-3 must export a global metric (today: single 4-scalar info string) |
| D4. Reward | per-AP goodput / network-wide | `MyGetReward` uses one global counter; per-AP needs per-AP Rx counters; also fix the hard-coded `5*150` normalization per AP count |
| D5. Observation | keep 1 raw scalar per AP / restore paper-style windowed mean+std per AP | ns-3 already sends 300-float history per env — per-AP needs one history deque per AP; Python currently reads only element 0 |
| D6. Stepping semantics | sequential env.step loop (current wrapper) / parallel ports | Sequential is simplest and already supported by `EnvWrapper`; parallel needs threading + care with ZMQ REP blocking |

Recommended default until the mentor decides (matches your stated safer interpretation): **A + per-AP Actor/local Critic + optional central critic, sequential stepping, per-AP reward** — smallest code delta from the current implementation.

## 10. Checklist status (updated)

| # | Action | Status |
|---|---|---|
| 1 | System/toolchain versions | ✅ done (§1) |
| 2 | torch/CUDA runtime | ✅ done (§7) |
| 3 | zmq/protobuf runtime | ✅ done (§3) |
| 4 | ns3gym import resolution | ✅ done (§4) |
| 5 | Review 2 local commits | ✅ done (§6) — delta vs upstream is configuration-only |
| 6 | `git fetch upstream` + compare | ✅ closed by user (2026-09-15): "My local repo is the latest" — no fetch run, no refs changed |
| 7 | W&B export | 👤 user action — instructions in §8 |
| 8 | Mentor decision brief | ✅ delivered (§9) — decisions D1–D6 pending mentor |

--- end of next-actions results ---

## 11. Post-audit resolution — upstream repository state

- **User statement (2026-09-15):** "My local repo is the latest."
- Decision: **NO `git fetch` was executed** — no network op, no refs written; the git state of `scratch/linear-mesh` is exactly as audited (branch `major-project` @ 6e90e62, `main`/origin/main @ b595c67, upstream configured but unfetched).
- Consequence for the audit: the §16.5 unknown *"whether upstream raoulraft has commits newer than b595c67"* is **closed by user assertion — [UNVERIFIED-LOCALLY, per user]**.
- If this ever needs re-checking later, the safe command is: `git fetch upstream && git log --oneline main..upstream/main` (fetch only updates remote-tracking refs).

--- final status: all Cline-executable next actions are COMPLETE. Remaining open items are user-side (§8 W&B export) and mentor-side (§9 decisions D1–D6). ---
