# CLAUDE.md — Multi-AP OSCAR (CN Major Project)

Extend OSCAR (DDPG contention-window optimization for 802.11) from 1 AP / 1 agent / 1 CW
to N APs in ONE shared ns-3 simulation, each with an independent AP-level DDPG agent and its own CW.
Goal: finish the whole project fast **without compromising correctness, reproducibility, or evaluation quality**.

## Rule #1 — Never assume
- Do not guess about code behavior, versions, file locations, results, or user intent. Verify by reading code/running it, or ASK the user.
- Code is authoritative over papers/docs. Paper behavior ≠ this code's behavior.
- Label statements as fact / decision / inference / unknown when it matters.
- If docs and repo disagree, report the conflict. Do not pick one silently.

## Stack (verified, do NOT upgrade/downgrade without approval)
ns-3.29 (C++, GCC 11.4) · ns3-gym 1.0.0 / py 0.1.0 · Python 3.7.16 (venv: `ns-3.29/venv`) ·
PyTorch 1.13.1+cu117 (GTX 1650 Ti 4 GB) · Gym 0.26.2 · NumPy 1.21.6 · protobuf 3.20.3 · pyzmq 26.2.1 · W&B 0.18.7 · Ubuntu 22.04 WSL2

## Layout & commands
- Root: `~/college/major/ns-allinone-3.29` (git repo). Project code: `ns-3.29/scratch/linear-mesh/`
  (`cw.cc`, `scenario.h`, `OSCAR_train.py`, `agents/our_ddpg/`, `baseline_v0_1_0.py`). ns3-gym: `ns-3.29/contrib/opengym/`.
- Build: `cd ns-3.29 && ./waf build` (slow, can take minutes; prefer `--target=linear-mesh`).
- Run target name is `scratch/linear-mesh/linear-mesh`, NOT `.../cw`.
- Train: `cd ns-3.29/scratch/linear-mesh && ../../venv/bin/python OSCAR_train.py`
- Baseline smoke: `../../venv/bin/python baseline_v0_1_0.py --smoke` (full run: no flag).
- A stale binary is not validation. Confirm it was rebuilt.

## Architecture invariants (ADR-0002, docs/multi-ap-design-v0.2.0.md)
- One ns-3 process, N APs. Start with 2 (default STA split 20/40), scale to 10 only after 2-AP works.
- One DDPG Actor-Critic agent per AP. Actor + Critic = ONE agent, never "two agents".
- Strict per-AP isolation: observations, rewards, actions, statistics, CWs. No AP sees another AP's local obs.
- Reward: per-AP normalized goodput. Observation: one raw local loss scalar per AP (initially).
- Sequential joint stepping through ns3-gym. Local critics only in v1.
- Central critic = optional later phase (v1.7+). It must NEVER block core completion.
- Out of scope for v1: mobility, dynamic STAs, detailed interference modeling, per-station actors, PHY/MAC changes.
- Distinguish project changes from upstream ns-3/ns3-gym code. Touch upstream only when necessary, and say so.

## Roadmap (ROADMAP.md, details in docs/detailed_roadmap.md)
v0.1–v1.0 ✅ (baseline, design, two-AP topology, per-AP stats, per-AP CW, multi-AP ns3-gym, independent agents, W&B,
validation, core) · **v1.1 benchmarks (NEXT)** · v1.2–1.6 scale 4→10 APs + analysis · v1.7–1.9 central critic · v2.x robustness/results/report/demo/audit.
- Priority: Tier 1 (v0.1–v1.0) → Tier 2 (v1.1–v1.6) → central critic → rest.
- When v1.0 works: tag it, run baselines, collect 2-AP results, THEN scale, THEN central critic.
- Each version has completion criteria in docs/detailed_roadmap.md. Meet them before closing.

## Workflow per milestone
1. Plan first: read only the relevant code, restate acceptance criteria, list assumptions/unknowns, ask if unclear.
2. Work on a feature branch (`feature/…`, `fix/…`). Never commit to `main`.
3. Minimal, targeted edits. No unrelated refactors.
4. Validate (there is no test framework, so do not add one):
   - `./waf build` succeeds. Then a short run, e.g.
     `./waf --run "scratch/linear-mesh/linear-mesh --dryRun=true --disableGym=true --apStaCounts=20,40 --simTime=2"`
   - Check logs/metrics for the milestone's property (per-AP isolation, correct CW per AP, sane stats).
   - Validate ns-3 stats and per-AP CW before any long training run.
   - Never claim something works without a run that shows it. Report failures honestly.
5. Self-review the diff: secrets, dead code/debug prints, duplication, consistency, error handling.
6. Commit: Conventional Commits `type(scope): summary` (<50 chars, imperative) + 1–3 line "why" body.
   Stage specific files (no blind `git add .`). Never push, merge, force-push, rebase, reset --hard,
   or delete branches/tags without explicit approval.
7. CHANGELOG.md: regenerate via git-cliff/conventional-changelog only if installed. Never hand-write it.
8. Tag each closed milestone (`vX.Y.Z`) only when the user approves. Pre-existing tag references in older docs are obsolete.
9. Update `memory-bank/activeContext.md` + `progress.md` and ROADMAP.md status. Then suggest a fresh session.

## Security / hygiene
- Never hardcode or commit secrets (W&B key via env/local login). Scan diffs for key=/token=/password=.
- Never commit build outputs, venvs, caches, `wandb/`, `results/`, `CW_data*`, `cw.csv`, pcaps, `.local-git-backups/`.
- W&B runs offline by default in the runner (`--online` to sync).

## Token efficiency (Pro plan, limited budget)
- At session start, read `memory-bank/activeContext.md` + `progress.md` first. Read other docs only when needed.
- Use grep/targeted reads over whole-file reads, especially for large docs and ns-3 sources.
- Don't re-read unchanged files. Don't spawn subagents unless asked. Keep answers short.
- Avoid long builds/training runs without asking. Use the smallest run that proves the point.

## Reference files
- `docs/project_description.md` (full spec, terminology) · `docs/detailed_roadmap.md` (per-version criteria)
- `docs/multi-ap-design-v0.2.0.md` + `docs/adr/` (design contract) · `docs/baseline-v0.1.0.md` (baseline numbers, known quirks §7)
- `.clinerules/` (detailed rules/workflows) · `memory-bank/` (current state) · `AGENTS.md`
