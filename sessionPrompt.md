Continue the mac-world project (Multi-AP OSCAR, ns-3.29). Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then `docs/results/per-ap-scenario-v3.4.0.md` (§4 batch, §4b oracle, §4c-§4d policy seeds, §4e/§4h TD3 + cwMinOnly, §4f-§4g uneven loads, §5 next) and `docs/adr/0005-coarse-loss-matrix.md`. Read `docs/results/fair-protocol-v3.2.0.md` §2-3 only if you touch the runner.
2. Toolchain per CLAUDE.md "Stack" (Python 3.7.16 venv `ns-3.29/venv`; no scipy, Wilcoxon is in `aggregate_bench.py`). If the venv is missing, ask; do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, then confirm the binary mtime changed (waf compares content hashes, an unchanged mtime after a no-op build is fine). Do not edit `cw.cc` or the trainer while a batch runs (each job calls `waf --run`).
4. Branch each piece of work from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it. (Tags on it were created once on user request, see below.)
- Branch from `dev`, commit with Conventional Commits and specific files, validate, `git merge --no-ff` into `dev`, push the feature branch and `dev`. Standing approval.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating tags (unless the user says "tag"), anything on `main`, and **any `rm -rf`** (never glob-delete under `results/`; the sandbox also blocks it). Committing run dirs (`trace.csv` + `config.json`, force-added) needs approval each time.
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets.
- CHANGELOG: commit first, then `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`, never hand-written. No CI is configured (no `.github/`), so "tag after CI" means tag after the push.
- If `git push` fails with HTTP 408 / "unexpected disconnect", retry with `git -c http.version=HTTP/1.1 push ...` (worked every time here; do not change git config).
- Commit trailer: use the one in the session reminder.

## State at handoff (facts; details in the report and memory-bank)
- Tags: `v3.0.0`, `v3.1.0`, `v3.2.0` (1ee5127), `v3.4.0` (66cf363), **`v3.4.1`** on `dev` (end of this work) and **`main-at-v3.4.1`** on `origin/main` (7df8322, the remote main, which is an ancestor of `dev`; local `main` 511acfe is 24 commits behind it and was not touched). Both pushed.
- Scenario (ADR-0005, all opt-in, defaults byte-identical): `cw.cc --apHidden a-b --hiddenLoss dB --apLoads l1,l2,..` (per-STA Mbps; `150,150,20` still saturates AP3, `150,150,1` does not); trainer `--reward pf`, `--algo td3`, `--cwMinOnly`, `--trainSeed`; `ceiling_sweep_v3_1_0.py --grid custom ...`; `aggregate_bench.py --pf --refs <tag keys>`; `fair_protocol_v3_2_0.py` (use `--variant=-xyz`, `--no-beb`, `--trainerArgs`, `--learnerArgs`).
- Main topology `10,10,10 --apHidden 1-3`. BEB (n=8): aggregate 71.6, per-AP 35.0 / 1.4 / 35.2. One 15 s job takes 350-600 s. Run ONE ns-3 job at a time (the runner refuses otherwise).
- Results that are stable: a PF-reward independent per-AP learner (DDPG, TD3, cwMinOnly; seeds 0-2 for DDPG, 0-1 for TD3/cwMinOnly) beats BEB and Global on PF utility and min-AP in all 8 eval seeds (p = 0.008) at lower aggregate. Unstable across policy seeds: independent-vs-shared PF ordering, "matches the 256,128,256 oracle", and the TD3 / cwMinOnly ranking (do not rank them without more seeds). Unsaturated load `150,150,1`: independent pf ties static 256,128,256 on PF (+0.00 ± 0.01) and beats BEB by +0.31.
- All run dirs are committed (arms A-P, static sweeps). Local-only leftovers to ignore: `docs/figures/v3.4.0-A`, `-AB`, `-ABC` (interim duplicates; deleting needs OK), `.python-version`, `netanim-3.108/*`, `ns-3.29/*.pcap`, `ns-3.29/scratch/linear-mesh/results_gate_*.out`. A stash `old local --staticCws static mode` is obsolete; do not apply it.
- Unknown: why 3 parallel sweep lanes failed earlier (run lanes=1).

## Update (after v3.3.0 session, 2026-10-31)
v3.3.0 sensing/IdleSense/residual/idle-obs done (`docs/results/sensing-heuristics-v3.3.0.md`), seed-2 TD3/cwMinOnly done (report §4i), technical report §20.5 written. Tasks 1-3 below are complete; remaining optional work: `--trainSeed 1/2` for residual and idle-obs arms, IdleSense on a single-domain topology (20,40), Bianchi (needs a fetchable Heusse/Bianchi source), v3.5.0 items.

## Open tasks (ask me which to do first, and the time budget before any batch)
1. v3.3.0 sensing + heuristics (IdleSense / Bianchi, residual RL) as a non-RL baseline: plan first (roadmap `docs/planning/detailed_roadmap.md`, `docs/research-beat-oscar.md` §6), likely touches `cw.cc` or the trainer, so a rebuild and regression checks.
2. Write the v3.4.0 conclusion into the technical report.
3. Optional: a third policy seed (`--trainSeed 2`) for TD3 and `--cwMinOnly` if a ranking claim is wanted (about 1.4 h per arm); `--apLoads` with the trained policy on a second load vector.

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons against BEB (and Global, oracle) on the same seed; ns-3 seed = python seed + 1.
- Kill processes by PID. For batch progress use the Monitor tool (`tail -n 0 -F batch.log | grep -E --line-buffered " -> (PASS|FAIL)|FAIL|^ABORT|^STOP|^DONE|^START"`), re-arm at its 30 min expiry and check the log for missed lines.
- Long batches: ask for the time budget (IST wall-clock deadline; the system clock is IST), write a driver in the scratchpad that runs serially and honours a STOP file between arms, and validate the first job before the rest.
- At the end: short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
