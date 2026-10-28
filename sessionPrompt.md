# Session prompt: next research milestone after v3.2.0 tooling

Paste everything below the line into Claude Code, started in the repo root (`~/mac-world`).

---

Continue the mac-world project (Multi-AP OSCAR, ns-3.29). Done and merged into `dev` (pushed, not tagged): v3.1.0 Ceiling follow-up (paired 6x10 refs) and **v3.2.0 fair-protocol TOOLING**. Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then `docs/results/fair-protocol-v3.2.0.md` (what exists, how it was validated, pilot, batch estimate), `docs/results/ceiling-v3.1.0.md` §6-7, and `docs/research-beat-oscar.md` §5 #4-#7, #14 and §6.
2. Check the toolchain against CLAUDE.md "Stack" (Python 3.7.16 venv at `ns-3.29/venv`). If the venv is missing, ask me; do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, then confirm the binary mtime changed. A stale binary is not validation. Do not edit `cw.cc` or the trainer while a batch is running (each job calls `waf --run`, which rebuilds).
4. Branch each piece of work from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it.
- Branch each piece of work from `dev`, commit with Conventional Commits and specific files, validate, then `git merge --no-ff` into `dev` and push the feature branch and `dev`. Standing approval; do not wait to be asked.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating tags (unless I say "tag"), anything on `main`, committing run dirs (`trace.csv` + `config.json` only, force-added), and any `rm -rf` (never glob-delete under `results/`: it holds raw data that exists nowhere else).
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets.
- CHANGELOG: `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`, never hand-written. No CI is configured.

## State at handoff (facts; details in `docs/results/fair-protocol-v3.2.0.md`)
- New trainer flags (all opt-in, defaults byte-identical): `--varySeeds`, `--saveActor DIR`, `--loadActor DIR --eval` (frozen, noise 0, no warm-up, no training), `--algo td3`, `--cwMinOnly` (cw.cc: MinCw = action, MaxCw 1023). Runner: `fair_protocol_v3_2_0.py` (`--trainerArgs` for all jobs, `--learnerArgs` for learned modes only; resumable; eval runs tagged `fz-<mode>`; aggregate with `aggregate_bench.py <benchDir> --topo T`).
- 20,40 pilot (shared, A1 settings, 2 train episodes, eval seed 100, n=1): frozen 39.74 vs BEB 27.33 Mbps. One 15 s job takes about 800-880 s on this 2-core laptop. Estimated n=8 batch: about 9.6 h per topology for 3 learned modes + BEB (inference).
- Ceiling (v3.1.0): no aggregate headroom over Global at 20,40 (+3.45 +- 6.77) and 6x10 (+3.61, n=1). The unequal STA split does not create a per-AP advantage; v3.4.0 needs APs that differ in more than STA count.
- NOT done: n >= 8 frozen-eval batch, Wilcoxon test in `aggregate_bench.py`, policy-seed variance (one `--trainSeed`), v3.3.0, v3.4.0.
- Unknown: why 3 parallel sweep lanes failed earlier. Inference only: `EnvWrapper` draws its port from `np.random` seeded by `--seed`, so same-seed lanes may collide on a port. Run ONE ns-3 job at a time.
- A stash `old local --staticCws static mode` is obsolete; do not apply it.

## Task
1. Plan v3.4.0 Per-AP scenario (ideas #7 + #14: `cw.cc` `set_phy` per-pair `SetLoss` partial overlap, uneven offered load per AP, cooperative fairness reward) with acceptance criteria and a time estimate. This changes the scenario (`cw.cc` / `scenario.h`, a coarse loss matrix; CLAUDE.md lists detailed interference modelling as out of scope for v1), so **ask me before any code change**. Re-validate association and per-AP stats as in v0.3 / v0.4, and check BEB/Global regressions on the old topology stay byte-identical (new scenario must be opt-in).
2. After my go-ahead and a validated scenario: the n >= 8 frozen-eval batch with `fair_protocol_v3_2_0.py` there (BEB, Global, independent `--alpha 0`, shared, optionally `--algo td3` / `--cwMinOnly`). Ask before any batch longer than about 2 h; split it by mode; one ns-3 job at a time. Add the Wilcoxon test to the aggregation first if you want it in the report.
3. Optional if I ask: v3.3.0 sensing + heuristics (IdleSense/Bianchi, residual RL), or tag `v3.2.0`.

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons against BEB (and Global) on the same seed; ns-3 seed = python seed + 1 (trainer does this).
- Kill processes by PID, not `pkill -f` patterns that appear in your own command line.
- Use a Monitor for long batches (30 min max per arm; a job's earlier rows stay in the manifest, so skip lines already seen).
- At the end: short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
