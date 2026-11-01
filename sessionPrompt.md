Continue the mac-world project (Multi-AP OSCAR, ns-3.29). Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout dev && git pull`. Read `memory-bank/activeContext.md` and `memory-bank/progress.md`, then `docs/results/sensing-heuristics-v3.3.0.md` (§1 what was added, §3b corrected results, §3c `20,40`) and `docs/results/per-ap-scenario-v3.4.0.md` (§4 to §4i, §5). Read `docs/reports/technical-report-v2.3.0.md` §20.5-20.6 for the narrative, `docs/adr/0005-coarse-loss-matrix.md` for the scenario, and `docs/results/fair-protocol-v3.2.0.md` §2-3 only if you touch the runner.
2. Toolchain per CLAUDE.md "Stack" (Python 3.7.16 venv `ns-3.29/venv`; no scipy, Wilcoxon is in `aggregate_bench.py`). If the venv is missing, ask; do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, then confirm the binary mtime changed (an unchanged mtime after a no-op build is fine). Regressions to re-check after any `cw.cc` change: `--nWifi=5` dry seed 1 simTime 2 = 10533 packets, `--apStaCounts=5,15` = 9000, `baseline_v0_1_0.py --smoke` cumulative reward 10.59458. Do not edit `cw.cc` or the trainer while a batch runs (each job calls `waf --run`).
4. Branch each piece of work from `dev`.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen: never commit to, merge into or push it.
- Branch from `dev`, commit with Conventional Commits and specific files, validate, `git merge --no-ff` into `dev`, push the feature branch and `dev`. Standing approval.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating or moving tags (unless the user says "tag"), anything on `main`, and **any `rm -rf` or `git stash drop`** (the auto-mode classifier blocks them until the user approves in the chat; never glob-delete under `results/`). Committing run dirs (`trace.csv` + `config.json` per referenced run, plus logs, manifests and actors, force-added with `git add -f`) needs approval each time.
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps or secrets.
- CHANGELOG: commit first, then `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`, never hand-written. No CI is configured (no `.github/`), so "tag after CI" means tag after the push.
- If `git push` fails with HTTP 408 / "unexpected disconnect", retry with `git -c http.version=HTTP/1.1 push ...` (worked every time here; do not change git config).
- Commit trailer: use the one in the session reminder.

## State at handoff (facts; details in the results docs, report and memory-bank)
- Tags: `v3.0.0`, `v3.1.0`, `v3.2.0`, `v3.4.0`, `v3.4.1`, **`v3.3.1`** (annotated, ddc1913 on `dev`; the handoff commit after it only changes docs and one `trace.csv`), `main-at-v3.4.1` on `origin/main` (7df8322; local `main` is behind and untouched).
- v3.3.1 code (all opt-in, defaults byte-identical): `cw.cc --idleSense` (published Idle Sense rule, Heusse et al. SIGCOMM 2005 Fig. 6: every `--idleMaxTrans` 5 observed attempts, CW x`--idleUp` 1.2 when mean idle slots < `--idleTarget`, else CW <- 2CW/(2+`--idleEps` CW), eps 0.001), `--residual` (action = Delta log2 CW in [-2, 2] around the IdleSense CW), `--obsIdle` (observation = idle slots/20). Idle slots come from the AP's own PHY `State` trace. Trainer: `--mode idlesense`, `--residual`, `--obsIdle`, `--idleTarget/--idleEps/--idleUp`. Runner: `fair_protocol_v3_2_0.py --idleOnly` (IdleSense eval jobs only, tag `idlesense<variant>`). Earlier scenario flags: `--apHidden a-b --hiddenLoss dB --apLoads l1,l2,..`, `--reward pf`, `--algo td3`, `--cwMinOnly`, `--trainSeed`.
- Target for this PHY (HE 20 MHz HeMcs11): 3.3, derived with the paper's formula from an ESTIMATED T_c/T_slot of about 24 (range 15-24 gives 2.6-3.3); T_c was not measured in the simulator. Fixed before the batch, not tuned.
- Main results (n=8 paired, eval seeds 100-107, 95 % CIs in the docs):
  - Hidden chain `10,10,10 --apHidden 1-3`: IdleSense has the highest aggregate (78.12 Mbps) and the worst fairness (PF 6.68 vs BEB 7.48; middle AP 0.53 Mbps; its CW sits near 1024). Residual RL on it is unstable over trainSeeds 0-2 (PF 7.93 / 8.19 / 6.57). PF reward + idle observation: PF 8.87 / 8.70 / 8.92, level with the static 256,128,256 oracle but not shown better than the loss observation.
  - Single domain `20,40`: IdleSense (no learning, same target) matches Global-CW: 38.77 ± 0.21 vs 38.65 ± 0.40 Mbps, paired +0.11 ± 0.25 (p = 0.31), +40 % vs BEB 27.66.
  - PF-reward independent learners (DDPG, TD3, cwMinOnly, 3 policy seeds each): beat BEB in all runs; TD3 trainSeed 2 ties Global on PF (-0.01 ± 0.03, p = 0.38). Rankings between algorithms and independent-vs-shared are NOT supported.
- Reference numbers (hidden chain): BEB aggregate 71.63, PF 7.48, min-AP 1.44; Global-CW 76.46 / 8.16 / 2.58; static 256,128,256 59.58 / 8.87 / 13.25.
- Job times: one 15 s job at `10,10,10` about 450-520 s (training episode about 480 s), at `20,40` about 830-860 s. Run ONE ns-3 job at a time (the runner refuses otherwise).
- All run dirs for arms A-U, the `20,40` runs and the calibration runs are committed. Not committed on purpose: the old variant's killed partial run (deleted). Local-only leftovers to ignore: `.python-version`, `netanim-3.108/*`, `ns-3.29/*.pcap`, `ns-3.29/scratch/linear-mesh/results_gate_*.out`, `stash@{0}` (WIP on main, not mine).
- PDF reading: no `pdftoppm`/`pdftotext` on this machine. The previous session used PyMuPDF installed by the user into its scratchpad (`pylib`), which does not persist; if you need it again ask the user to run `! python3 -m pip install --target <scratchpad>/pylib PyMuPDF==1.22.5` with the pyenv Python 3.7. Do not install it into the project venv.
- Unknown: why 3 parallel sweep lanes failed earlier (run lanes=1); the true T_c of this PHY; IdleSense sensitivity to eps and maxtrans (only the target was varied, one seed).

## Open tasks (ask me which to do first, and the time budget before any batch)
1. Measure T_c in the simulator (frame airtime + ACK timeout at HeMcs11) and rerun IdleSense on `20,40` and the hidden chain with the measured target (about 2 h for `20,40` n=8, 1 h for the chain); check eps / maxtrans sensitivity on one seed.
2. IdleSense with the PF-style fairness fix, or IdleSense as the residual base only for the single-domain case: only if you want to push "heuristic + RL" further; the residual arm on the hidden chain did not help.
3. Bianchi baseline: blocked on a readable source for Bianchi 2000 (the SMU copy returned 403; the 2005 Bianchi-Tinnirello letter extracts without its equations). Drop unless a source is provided.
4. v3.5.0 optional (mean-field neighbours #11, MAPPO/QMIX #10, extra MAC knobs #13): only on request; #11 needs an ADR.
5. Policy-seed test or more policy seeds if a ranking between DDPG, TD3 and `--cwMinOnly` is wanted (about 1.4 h per arm).

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Verify an algorithm against its source before naming a result after it (the first "IdleSense" here was a variant and had to be redone).
- Paired comparisons against BEB (and Global, oracle) on the same seed; ns-3 seed = python seed + 1.
- Kill processes by PID. For batch progress use the Monitor tool (`tail -n 0 -F batch.log | grep -E --line-buffered " -> (PASS|FAIL)|FAIL|^ABORT|^STOP|^DONE|^START"`), re-arm at its 30 min expiry and check the log for missed lines; for long batches a single `until grep -qE "^DONE|^ABORT|FAIL" log` in a background Bash saves turns.
- Long batches: ask for the time budget (IST wall-clock deadline; the system clock is IST), write a driver in the scratchpad that runs serially and honours a STOP file between arms, and validate the first job before the rest.
- At the end: short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
