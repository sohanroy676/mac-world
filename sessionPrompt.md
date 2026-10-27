# Session prompt: continue v3.1.0 (static CW ceiling sweep) on another laptop

Paste everything below the line into Claude Code, started in the repo root (`ns-allinone-3.29`).

---

Continue the mac-world project (Multi-AP OSCAR, ns-3.29) from a handoff. The previous session ran on another laptop and stopped
part-way through milestone **v3.1.0 Ceiling**. Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then
   `docs/research-beat-oscar.md` (the research plan, section 6 milestones) and `docs/results/ceiling-v3.1.0.md` (partial report).
2. Check the toolchain matches CLAUDE.md "Stack" (Python 3.7 venv at `ns-3.29/venv`, ns-3.29 builds). If the venv is missing, ask me;
   do not upgrade or downgrade anything.
3. Rebuild: `cd ns-3.29 && ./waf build --target=linear-mesh` (several minutes) and confirm the binary mtime changed. A stale binary is not validation.
4. Branch: work on `feature/v3.1.0-ceiling` (already on origin, merged into `dev` as a partial). Continue on it, or branch `fix/...` from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it.
- Long-lived integration branch is `dev`. Branch each piece of work from `dev`, commit with Conventional Commits and specific files,
  validate, then `git merge --no-ff` into `dev` and push the feature branch and `dev`. Standing approval; do not wait to be asked.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating tags, anything on `main`.
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets. `results/` is gitignored; the few runs
  committed for this handoff were force-added with the user's approval. Do not add more without asking.

## State at handoff (facts, from the previous session)
- Code done and validated: `cw.cc` ignores agent actions when `--apCws` is set (static CWs stay); `OSCAR_multi_ap_train.py --mode static --apCws c1,c2`;
  `ceiling_sweep_v3_1_0.py` (`run` and `table`). Validation: BEB and Global short-run traces byte-identical to the old binary;
  static short run held CW 32/512 on every step; `--check` PASS.
- Pilot, 20,40, seed 0, static diagonal, policy window steps >= 300 (aggregate Mbps): CW 32: 12.80, 64: 19.66, 128: 30.25, **256: 37.75**.
  Paired references (n=3 seeds 0-2): BEB 27.30 +- 0.63, Global 36.17 +- 6.95. Seed 0 only so far: 256,256 is +10.50 over BEB and +2.68 over Global (n=1, no CI).
- Per job ~20-25 min (ns-3 dominated, no agent). NOT yet run: CW 384, 512, 768, 1023 diagonal and the D1 pair (64,512),(512,64) at seed 0;
  then seeds 1-2; then the off-diagonal grid; then 6x10 diagonal. Tables: `docs/figures/v3.1.0/tables.md`.
- Unknown: why running 3 sweep lanes in parallel failed (2 of 3 trainers exited rc 0 after ~4 s with no `APs:` line, cause not investigated).
  Run ONE job at a time unless you find and fix the cause first.

## Task
1. Resume the pilot: `cd ns-3.29/scratch/linear-mesh && ../../venv/bin/python ceiling_sweep_v3_1_0.py run --grid pilot --seeds 0 --lanes 1 --benchDir results/ceiling-v3.1.0`
   (resumes from `results/ceiling-v3.1.0/manifest.csv`; only PASS rows are skipped; remove the FAIL rows' effect is automatic). Remaining pilot ~6 jobs, about 2.5 h:
   ask me before starting a batch longer than about 2 h.
2. Build the table: `ceiling_sweep_v3_1_0.py table --benchDir results/ceiling-v3.1.0 --out ../../../docs/figures/v3.1.0 --refs results/screen2-beb/manifest.csv results/screen2-global/manifest.csv`.
   The BEB/Global reference run dirs are committed (trace.csv + config.json only) so this works on a fresh clone.
3. Report the pilot to me with the D1 payoff (64,512)/(512,64) and ask for approval of the rest (3 seeds at 20,40 diag + off-diagonal grid
   {32,128,512,1023}^2, then `--grid diag6` at 6x10). Record the decision rule outcome: is the headroom of the best static CW over Global larger than the CI width?
   Note: a static common CW of 256 may already match or beat Global; check with n=3 before claiming anything.
4. Close v3.1.0: finish `docs/results/ceiling-v3.1.0.md` (style of `docs/results/improvement-v3.0.0.md`, facts/inferences labelled), update ROADMAP.md,
   memory-bank, run `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md` if available (never hand-write it), merge into `dev`, push.
5. Then plan (do not start without my go-ahead) v3.2.0 Fair protocol, v3.3.0 Sensing + heuristics, v3.4.0 Per-AP scenario (ask me first),
   v3.5.0 optional, as in `docs/research-beat-oscar.md` section 6.

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons against BEB and Global on the same seed. Use ns-3 seed = python seed + 1 (trainer does this).
- Do not kill processes with `pkill -f` patterns that appear in your own command line (it kills your shell); kill by PID.
- At the end, give a short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
