Continue the mac-world project (Multi-AP OSCAR, ns-3.29). Done and merged into `dev` (pushed, not tagged): v3.1.0 ceiling, v3.2.0 fair-protocol tooling, **v3.4.0 hidden-chain scenario + static gate + n=8 frozen-eval batch**. Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then `docs/results/per-ap-scenario-v3.4.0.md` (§3 gate, §4 batch, limits, §5 next), `docs/adr/0005-coarse-loss-matrix.md`, `docs/results/fair-protocol-v3.2.0.md` §2-3 if you touch the runner.
2. Check the toolchain against CLAUDE.md "Stack" (Python 3.7.16 venv at `ns-3.29/venv`; no scipy, Wilcoxon is implemented in `aggregate_bench.py`). If the venv is missing, ask; do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, then confirm the binary mtime changed. Do not edit `cw.cc` or the trainer while a batch runs (each job calls `waf --run`).
4. Branch each piece of work from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it.
- Branch from `dev`, commit with Conventional Commits and specific files, validate, `git merge --no-ff` into `dev`, push the feature branch and `dev`. Standing approval.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating tags (unless I say "tag"), anything on `main`, and **any `rm -rf`** (never glob-delete under `results/`; the sandbox also blocks it). Committing run dirs (`trace.csv` + `config.json`, force-added) needs my approval each time.
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets.
- CHANGELOG: `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`, never hand-written. No CI is configured.
- Commit trailer for this model: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` (use the one in the session reminder).

## State at handoff (facts; details in `docs/results/per-ap-scenario-v3.4.0.md`)
- Scenario (ADR-0005, all opt-in, defaults byte-identical): `cw.cc --apHidden a-b --hiddenLoss dB --apLoads l1,l2,..`; trainer `--apHidden --hiddenLoss --apLoads --reward pf` (independent/shared, PF team reward); `ceiling_sweep_v3_1_0.py --grid chain3|custom --topo --cws --extraArgs`, table `--pf`; `aggregate_bench.py --pf --refs beb fz-global` (PF utility, min-AP, exact Wilcoxon); `fair_protocol_v3_2_0.py --variant=-pf` (use `=`, a leading `-` is read as a flag).
- Topology: `10,10,10 --apHidden 1-3` (edges hidden from each other, middle AP hears both). BEB (n=8): aggregate 71.6, per-AP 35.0 / 1.4 / 35.2 (middle starved). One 15 s job = about 490 s.
- Static gate (n=3): 256,128,256 beats best common CW on PF utility by +0.15 ± 0.02; 256,64,256 beats it on min-AP by +7.62 ± 0.27 Mbps. Aggregate falls (62.9 common 256 -> 53.9-59.5).
- Batch (frozen, 2 training episodes, eval seeds 100-107, paired with BEB, p = 0.008 for every row): independent `--reward pf` PF +1.36 ± 0.04 / min-AP +8.56 ± 0.52 vs BEB and +0.68 ± 0.08 / +7.41 ± 0.35 vs Global, aggregate -8.8 / -13.6 Mbps; shared pf PF +1.10 / min-AP +3.05 vs BEB, aggregate +1.8; Global PF +0.69 vs BEB (highest aggregate 76.5); independent `--alpha 0` below BEB on all four metrics.
- Run dirs (`results/ceiling-v3.4.0`, `results/fair-v3.4.0-{A-shared-pf,B-indep-pf,C-global,D-indep-a0}` with logs, manifests and `actors/`) are committed (trace.csv + config.json only). Tables: `docs/figures/v3.4.0/` and `docs/figures/v3.4.0-gate/`.
- NOT done: policy-seed variance (one `--trainSeed 0`, CIs cover only evaluation-seed variance), static oracle at eval seeds 100-107, TD3 / `--cwMinOnly` arms, `--apLoads` batch, v3.3.0, tagging.
- Untracked leftovers to ignore: `docs/figures/v3.4.0-A`, `-AB`, `-ABC` (interim duplicates of `docs/figures/v3.4.0`; deleting needs my OK), `.python-version`, `netanim-3.108/*`, `ns-3.29/*.pcap`, `ns-3.29/scratch/linear-mesh/results_gate_*.out` (copies are in `docs/figures/v3.4.0-gate/`). A stash `old local --staticCws static mode` is obsolete; do not apply it.
- Unknown: why 3 parallel sweep lanes failed earlier (run ONE ns-3 job at a time; the runner refuses if `linear-mesh` is running).

## Task (ask me which to do first)
1. Policy-seed variance: repeat independent-pf and shared-pf with `--trainSeed 1` and `2` (separate `--benchDir`s, same eval seeds 100-107; about 1.4 h per arm; BEB already exists, use `--no-beb`). Then aggregate the arms together.
2. Static oracle at eval seeds 100-107 (`ceiling_sweep_v3_1_0.py run --grid custom --topo 10,10,10 --cws "256,128,256;256,64,256" --seeds 100 .. 107 --extraArgs "--apHidden 1-3"`, about 1 h per setting) for a paired oracle gap.
3. Optional: `--algo td3` / `--cwMinOnly` for independent pf; v3.3.0 sensing + heuristics (IdleSense/Bianchi, residual RL); `--apLoads` uneven-load check; write the v3.4.0 conclusion into the technical report; tag `v3.4.0` (only if I say "tag").

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons against BEB (and Global) on the same seed; ns-3 seed = python seed + 1.
- Kill processes by PID. Monitor filters: no trailing `tail` (it buffers); for one end-of-arm notification use a background `until grep` loop.
- Long batches: ask for the time budget (the user gave IST wall-clock deadlines last time; the system clock is IST), write a driver that checks time left before each arm, and run arms serially.
- At the end: short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
