# Session prompt: start the next research milestone after v3.1.0 Ceiling (closed)

Paste everything below the line into Claude Code, started in the repo root (`~/mac-world` on the laptop used for v3.1.0; `ns-allinone-3.29` elsewhere).

---

Continue the mac-world project (Multi-AP OSCAR, ns-3.29). Milestone **v3.1.0 Ceiling is closed** (merged into `dev`, pushed, tagged `v3.1.0`).
Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then
   `docs/results/ceiling-v3.1.0.md` (final report) and `docs/research-beat-oscar.md` (sections 4-6).
2. Check the toolchain matches CLAUDE.md "Stack" (Python 3.7.16 venv at `ns-3.29/venv`). If the venv is missing, ask me; do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, then confirm the binary mtime changed. A stale binary is not validation.
4. Branch each piece of work from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it.
- Long-lived integration branch is `dev`. Branch each piece of work from `dev`, commit with Conventional Commits and specific files,
  validate, then `git merge --no-ff` into `dev` and push the feature branch and `dev`. Standing approval; do not wait to be asked.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating tags (unless I say "tag"), anything on `main`.
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets. `results/` is gitignored; run dirs are force-added
  (`trace.csv` + `config.json` only) only with my approval. v3.1.0 run dirs are already committed.
- No CI is configured (checked: no `.github`, `gh run list` empty). `git-cliff` lives in `~/.venvs/changelog` (outside the repo, pip-installed); regenerate with `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`, never hand-write.

## State at handoff (facts from v3.1.0; details in `docs/results/ceiling-v3.1.0.md`)
- 50 static-CW jobs PASS at 20,40 (diagonal + D1 pair at seeds 0-2, off-diagonal grid at seed 0) and 6x10 diagonal (seed 0). One job ~800-1150 s on a 2-core laptop.
- 20,40, n=3: best static common CW 512,512 = 39.62 +- 0.21 Mbps; +12.32 +- 0.84 vs BEB; +3.45 +- 6.77 vs Global (CI spans 0). Decision rule NOT met: no measurable headroom over Global.
- No per-AP split beat 512,512 (off-diagonal grid n=1, best 39.52; D1 pair n=3 below it and very unfair). 6x10 diagonal plateaus at 512-768 (about 39.7, n=1, no paired references: none with this exact split in the clone).
- Code in place: `cw.cc` honours `--apCws` (ignores agent actions); `OSCAR_multi_ap_train.py --mode static --apCws c1,c2`; `ceiling_sweep_v3_1_0.py` (`run`, `table`).
- Unknown: why 3 parallel sweep lanes failed in the earlier session (cause not investigated). Run ONE ns-3 job at a time unless you find and fix the cause first.
- A stash `old local --staticCws static mode` may exist on the laptop that did v3.1.0; it is obsolete (superseded by `--apCws`), do not apply it.

## Task
1. Ask me which order to run the remaining milestones. The ceiling shows no aggregate headroom over Global at 20,40, and `docs/research-beat-oscar.md` says that case should move toward
   the per-AP scenario (#7) and fairness reward (#14). Options: (a) as planned v3.2.0 -> v3.3.0 -> v3.4.0, or (b) v3.4.0 first. v3.4.0 changes the scenario
   (`cw.cc` `set_phy` / `scenario.h`, a coarse loss matrix) so ask before starting it.
2. Plan (do not start without my go-ahead) the chosen milestone with acceptance criteria and a time estimate for any batch (ask before a batch longer than about 2 h):
   - v3.2.0 Fair protocol: multi-episode training, `--saveActor/--loadActor`, frozen noise-free eval, n >= 8 paired seeds, `--alpha 0` independent, CWmin-only flag, TD3 option.
   - v3.3.0 Sensing + heuristics: sensing observations, IdleSense/Bianchi baselines, residual RL.
   - v3.4.0 Per-AP scenario: partial overlap / uneven load, cooperative fairness reward.
   - v3.5.0 optional: mean-field neighbours, MAPPO/QMIX, extra MAC knobs.
3. Optional if I ask: a paired 6x10 BEB/Global reference at seed 0 (same split `10,10,10,10,10,10`, same simTime) to turn the n=1 6x10 ceiling into a paired comparison.

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons against BEB and Global on the same seed. Use ns-3 seed = python seed + 1 (trainer does this).
- Do not kill processes with `pkill -f` patterns that appear in your own command line (it kills your shell); kill by PID.
- Use a Monitor for long batches (30 min max per arm, re-arm with `tail -n +N` from the line count so already-seen lines are not replayed).
- At the end, give a short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
