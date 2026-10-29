Continue the mac-world project (Multi-AP OSCAR, ns-3.29). Done and merged into `dev` (pushed): v3.1.0 ceiling (tagged), v3.2.0 fair-protocol tooling (**not tagged**), **v3.4.0 hidden-chain scenario + static gate + n=8 frozen-eval batch + paired static oracle at eval seeds 100-107 (TAGGED `v3.4.0` at 66cf363; the oracle was added after the tag)**. Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then `docs/results/per-ap-scenario-v3.4.0.md` (§3 gate, §4 batch, §4b oracle, limits, §5 next), `docs/adr/0005-coarse-loss-matrix.md`, and `docs/results/fair-protocol-v3.2.0.md` §2-3 if you touch the runner.
2. Check the toolchain against CLAUDE.md "Stack" (Python 3.7.16 venv at `ns-3.29/venv`; no scipy, Wilcoxon is implemented in `aggregate_bench.py`). If the venv is missing, ask; do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, then confirm the binary mtime changed. Do not edit `cw.cc` or the trainer while a batch runs (each job calls `waf --run`).
4. Branch each piece of work from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it.
- Branch from `dev`, commit with Conventional Commits and specific files, validate, `git merge --no-ff` into `dev`, push the feature branch and `dev`. Standing approval.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating tags (unless I say "tag"), anything on `main`, and **any `rm -rf`** (never glob-delete under `results/`; the sandbox also blocks it). Committing run dirs (`trace.csv` + `config.json`, force-added) needs my approval each time.
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets.
- CHANGELOG: commit first, then `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`, never hand-written. No CI is configured.
- Commit trailer: use the one in the session reminder.

## State at handoff (facts; details in `docs/results/per-ap-scenario-v3.4.0.md`)
- Scenario (ADR-0005, all opt-in, defaults byte-identical): `cw.cc --apHidden a-b --hiddenLoss dB --apLoads l1,l2,..`; trainer `--apHidden --hiddenLoss --apLoads --reward pf` (independent/shared, PF team reward); `ceiling_sweep_v3_1_0.py --grid chain3|custom --topo --cws --extraArgs`, table `--pf`; `aggregate_bench.py --pf --refs <keys>` (PF utility, min-AP, exact Wilcoxon; `--refs` accepts any tag key, e.g. `cw256-128-256`); `fair_protocol_v3_2_0.py --variant=-pf` (use `=`, a leading `-` is read as a flag).
- Topology: `10,10,10 --apHidden 1-3`. BEB (n=8): aggregate 71.6, per-AP 35.0 / 1.4 / 35.2 (middle starved). One 15 s job takes about 460-600 s.
- Static gate (n=3, seeds 0-2): 256,128,256 beats best common CW on PF by +0.15 ± 0.02; 256,64,256 on min-AP by +7.62 ± 0.27.
- Frozen-eval batch (eval seeds 100-107, 2 training episodes, `--trainSeed 0`): independent `--reward pf` PF +1.36 ± 0.04 / min-AP +8.56 ± 0.52 vs BEB, +0.68 ± 0.08 / +7.41 ± 0.35 vs Global (p = 0.008), aggregate -8.8 / -13.6 Mbps; shared pf in between; independent `--alpha 0` below BEB.
- Paired static oracle (same 8 seeds, 16 jobs PASS): 256,128,256 PF 8.87, min-AP 13.25, aggregate 59.58; 256,64,256 PF 8.66, min-AP 17.37, aggregate 53.90. Independent pf vs 256,128,256: PF -0.03 ± 0.01, min-AP -3.26 ± 0.51, aggregate +3.23 ± 1.13; shared pf PF -0.29 ± 0.06; Global -0.71 ± 0.07; BEB -1.39 ± 0.04 (all p = 0.008). Tables: `docs/figures/v3.4.0-oracle/`.
- Run dirs (trace.csv + config.json, logs, manifests, `actors/`) are committed: `results/ceiling-v3.4.0`, `results/ceiling-v3.4.0-eval` (oracle at seeds 100-107), `results/fair-v3.4.0-{A-shared-pf,B-indep-pf,C-global,D-indep-a0}`. Tables: `docs/figures/v3.4.0/`, `-gate/`, `-oracle/`.
- NOT done: policy-seed variance (one `--trainSeed 0`, CIs cover only evaluation-seed variance), TD3 / `--cwMinOnly` arms, `--apLoads` batch, v3.3.0, tag `v3.2.0`.
- Untracked leftovers to ignore: `docs/figures/v3.4.0-A`, `-AB`, `-ABC` (interim duplicates of `docs/figures/v3.4.0`; deleting needs my OK), `.python-version`, `netanim-3.108/*`, `ns-3.29/*.pcap`, `ns-3.29/scratch/linear-mesh/results_gate_*.out`. A stash `old local --staticCws static mode` is obsolete; do not apply it.
- Unknown: why 3 parallel sweep lanes failed earlier (run ONE ns-3 job at a time; the runner refuses if `linear-mesh` is running).

## Task (ask me which to do first, and the time budget before any batch)
1. Policy-seed variance: repeat independent-pf and shared-pf with `--trainSeed 1` and `2` (separate `--benchDir`s, same eval seeds 100-107; about 1.4 h per arm; BEB already exists, use `--no-beb`). Then aggregate the arms together with the existing A/B/C/D and oracle dirs.
2. Optional: `--algo td3` / `--cwMinOnly` for independent pf; v3.3.0 sensing + heuristics (IdleSense/Bianchi, residual RL); `--apLoads` uneven-load check; write the v3.4.0 conclusion into the technical report; tag `v3.2.0` (only if I say "tag").

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons against BEB (and Global, oracle) on the same seed; ns-3 seed = python seed + 1.
- Kill processes by PID. For batch progress use the Monitor tool (`tail -n 0 -F batch.log | grep -E --line-buffered " -> (PASS|FAIL)|^FAIL|^ABORT|^STOP|^DONE"`), re-arm at its 30 min expiry and check the log for missed lines.
- Long batches: ask for the time budget (IST wall-clock deadline; the system clock is IST), write a driver in the scratchpad that checks time left before each arm or seed, and run serially.
- At the end: short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
