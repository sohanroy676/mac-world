Continue the mac-world project (Multi-AP OSCAR, ns-3.29), v4 plan, next: resolve M1 leftovers, then M2 (v3.7.0). Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout feature/v4 && git pull`. Read `memory-bank/activeContext.md` and `progress.md`, then `docs/results/m1-oracle-grids-v3.6.0.md` (M1 state), and in `docs/planning/mac-world-v4-plan.html` the sections M2, Baselines, Scoring, Statistics (extract text with a small python script; large HTML). ADRs 0005-0007 only if you touch the scenario, on/off traffic or the shared actor.
2. Toolchain per CLAUDE.md "Stack" (Python 3.7.16 venv `ns-3.29/venv`; no scipy). Do not upgrade or downgrade anything.
3. Rebuild only if you change `cw.cc`: `cd ns-3.29 && ./waf build --target=linear-mesh`, confirm the binary mtime changed. Regressions after any `cw.cc` change: `--nWifi=5` dry seed 1 simTime 2 = 10533 packets, `--apStaCounts=5,15` = 9000, `baseline_v0_1_0.py --smoke` reward 10.59458, default `2,3` trace byte-identical (reference run `results/multi-ap-20261028-083001`, args `--apStaCounts 2,3 --simTime 3 --stepTime 0.1 --historyLength 20 --obsWindow 20 --start_timesteps 10 --batch_size 8 --seed 100 --mode beb --check --cwReadbackEvery 0`). Do not edit `cw.cc` or the trainer while a batch runs.

## Git rules (override CLAUDE.md and .clinerules where they differ)
- `main` is frozen. **`dev` is NOT touched for v4 work until the user says so.** Integration branch **`feature/v4`** (long-lived, pushed). Branch each piece from it (`feature/v3.7.0-<piece>`, `fix/...`, `docs/...`), validate, `git merge --no-ff` into `feature/v4`, push both. Standing approval.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, creating or moving tags (unless the user says "tag"), anything on `main` or `dev`, any `rm -rf` or `git stash drop`, and committing run dirs (`git add -f` of `config.json` + `trace.csv` per referenced run, plus logs and manifests).
- Never commit build outputs, venvs, `wandb/`, `CW_data*`, `cw.csv`, pcaps, `.wandb` files or secrets. CHANGELOG: commit first, then `~/.venvs/changelog/bin/git-cliff -o CHANGELOG.md`. No CI exists: "tag after CI" means tag after the push. On HTTP 408 retry with `git -c http.version=HTTP/1.1 push ...`. Commit trailer: use the one in the session reminder.

## State at handoff (facts)
- Tags: **`v3.6.0`** (M1) and `v3.5.0` (M0) on `feature/v4`. `dev` is at v3.3.1 docs and has NOT received v4 work.
- M1 done (details `docs/results/m1-oracle-grids-v3.6.0.md`): 258 jobs PASS; selection-seed oracles (S4 64,64,64 / 128,64,128 / 256,128,256 for alpha 0/1/2; S5a 128,128,128 / 128,128,128 / 128,64,128; S8 phase 3 64,64,64 at alpha 1 and 64,32,64 at alpha 2, alpha 0 degenerate; S2 512,512); G0a PASS, G0b PASS on idle slots, FAIL on retry rate; IdleSense does not settle in 3 s (13-15 s), so IdleSense cells run 30 s per the plan rule; first GC tables for S2/S4/S5a at eval seeds 100-102 (`docs/figures/v3.6.0-grids/gc_table_*.md`). Headline (n=3, 1 Global/OSCAR training seed): IdleSense infeasible in S4 and S5a, OSCAR per AP infeasible everywhere, Global near the ceiling in S2 and S5a but only 0.3-0.4 GC in S4 at alpha 1-2, PF learner near the oracle in S4/S5a (seed-dependent).
- Code added: `--extraTraces` now also writes an `idle` column and prints per-AP `DELAY` lines in gym runs (scheduled before `Simulator::Run`; the trainer's stop request exits ns-3 before the end-of-main summary). `m1_jobs_v3_6_0.py` (a1/a2/a3 job lists), `m1_analysis_v3_6_0.py`, batch driver `batch_driver_v3_5_0.py` (resumes from its manifest; a `STOP` file in the batch dir stops it).
- Load rule: equal-load cells use `--offeredLoad 10 --rewardNorm 150`; S5a keeps `150,150,1`. Only powers of two matter for CW (STAs read 2^k-1).
- Machine: WSL has 3 cores = 2 lanes. A2-A3 job times at 2 lanes: grids about 4-8 min each, S5a about 8-10 min, learner training about 13 min. A stray `2,3` ns-3 process (PID 1687, since 2026-11-01 12:53) may still be running; check with `pgrep -af linear-mesh` and ask before killing.

## Open items (ask the user which first)
1. **S7-S4 delay load is broken**: uniform 80 % of BEB aggregate (1.93 Mbps/STA) asks 19 Mbps of the middle AP, which no static delivers, so every setting has middle-AP p99 about 500 ms and the plan's oracle rule (lowest p99 at >= 99 % delivered) has no answer. Proposal: per-AP loads via `--apLoads` with the middle AP at about 1 Mbps/STA, then re-run the S7-S4 grid. S7-S2 works (oracle 256,256, p99 19.5 ms vs BEB 27.3).
2. S8 phase 3 oracles sit at the edge-CW lower bound of the grid (64): run edge CW 16/32.
3. GC table is eval seeds 100-102 only; Stage 2 needs 103-109 (plan). Global/OSCAR have one training seed.
4. User sign-off on my definitions: G0a (idle slots within 10 %, SD below 10 %), G0b (|edge - middle| > 3 pooled seed SD), IdleSense "settled" criterion (CW within a factor 2 of the last-third median).
5. Then M2 (new baselines coded while M3 runs; only from texts that were read) and M3 (RAFA, shared actor with gate G0b), per the plan page. S8 phase 2 (S5a loads mid-run) needs new code: ADR-0006 has no load schedule.
Ask the user for the time budget (IST deadline) and WSL core count before any batch.

## Working rules
- Never assume; label fact / inference / unknown. Never claim a result without a run. Smallest validation first, short answers.
- Paired comparisons on the same seed (ns-3 seed = python seed + 1). Selection seeds 0-2, evaluation seeds 100-109, training ns-3 seeds 2001+; keep them separate.
- Kill processes by PID. For batch progress use one background `until grep` on the batch log, not repeated polling.
- At the end: short summary (what changed, results with CIs, branches pushed, what is next) and suggest a fresh session.
