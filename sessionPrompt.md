Continue the mac-world project (Multi-AP OSCAR, ns-3.29), v4 plan revision 10. M0-M3 are done; next is M2c and M2b (v3.8.0), then M4. Follow CLAUDE.md, except where this prompt changes the git rules.

## Start of session
1. `git fetch origin && git checkout feature/v4 && git pull`. Read `memory-bank/activeContext.md` and `progress.md`, then `docs/results/m3-step3-results-v4.0.0.md` and `m2c-preregistration-v4.0.0.md`. In `docs/planning/mac-world-v4-plan.html` read M2b/M2c, M4, Claims and scoring, Statistics, Risks (extract text with a small python script). ADRs 0005-0007 before touching the shared actor or the pool.
2. Toolchain per CLAUDE.md "Stack". Rebuild only if `cw.cc` changes; regressions are listed in the earlier prompt in git history (`git show v3.7.0:sessionPrompt.md`). After a trainer change run only the `2,3` reference and `cmp` its trace.
3. Compute: the Actions runner and job format are in `.github/` (`workflows/run-jobs.yml`, `scripts/make_matrix.py`, `run_job.py`, `fetch_bundles.py`, job lists in `jobs/`). `run_job.py` is plain Python, so the same job JSON can run on any other machine or provider; keep the platform fixed within one comparison. Notes: `docs/results/actions-comparability-2026-11-08.md`, `m3-step0-checks-v4.0.0.md`.

## Git rules (override CLAUDE.md where they differ)
- `main` is frozen. `dev` is NOT touched for v4 work until the user says so. Integration branch is `feature/v4`. Branch each piece from it, validate, `git merge --no-ff` into it, push both. Standing approval.
- Ask first before: force-push, rebase of pushed history, reset --hard, deleting branches or tags, tags (unless the user says "tag"), anything on `main` or `dev`.
- Run dirs may be committed (`config.json` + `trace.csv` per run, actors, result.txt) under `docs/figures/`; check `du -sh .git` first (567 MB at this handoff). Never commit secrets, `wandb/`, `CW_data*`, `cw.csv`, pcaps, build outputs.
- CHANGELOG: commit first, then `git-cliff -o CHANGELOG.md` (needs a non-shallow clone: `git fetch --unshallow --tags`; in a fresh container `pip install --target ~/.gc git-cliff`).
- Commit trailers: use the ones in the session reminder. No model names in commits or PRs.

## State at handoff (2026-11-10, facts)
- Tags: `v4.0.0` (M3), `v3.7.0`, `v3.6.0`, `v3.5.0` on `feature/v4`.
- M3 outcome (selection seeds 0-2, alpha 1, GC): per-scenario RAFA (lambda 1, 6 episodes, shared actor with alpha input) S2 0.730, S4 0.968, S5a 0.775. Pooled RAFA (24 configs round-robin) S2 0.522, S4 0.553, S5a 0.610. **Gate G3 failed, so RAFA = per-scenario.** G1 failed (edge/middle CW ratio about 1.0-1.7; shared actor kept as a stated deviation), G2 passed, Gumbel noise not adopted. S2 per-scenario pins the CW at 1024 in all 3 seeds (RAFA's weak cell). At alpha 0, S4 is weak (6-episode GC 0.01 / -1.59 / 0.87).
- Open M3 items: alpha-4 (max-min) oracle not determined; lab sha256 of `results/multi-ap-20261028-083001/trace.csv` not compared (Actions `2,3` ref sha256 is `044cf770...1958`); a lab GPU vs Actions CPU run of the same seed not done; the decision card on G1 was never answered.
- Determinism: learner runs are bit-identical only within one CPU vendor (AMD EPYC vs Intel Xeon differ by 1 ulp in torch). Non-learned runs are byte-identical across platforms.
- **M2c run 42774734240 (30 jobs, 138 commands) was still running at handoff.** It retrains Global, PF learner and CCOD (12 episodes x 3 seeds each, S2/S4/S5a) plus BEB/IdleSense/static refs at seeds 100-102 on Actions CPU. Job `m2c-s5a-ccod-t1` failed at apt install (a 404 on perl packages, infrastructure, not the code): rerun it with `rerun_failed_jobs` once the run completes. Results are in the job logs (kept about 90 days): `python3 .github/scripts/fetch_bundles.py 42774734240 <out>`, symlink the eval dirs into one results dir, then `gc_analysis.py --tagPrefix m2c- --seeds 100-102 --alphas 0,1,4`. Selection rule for the strongest seed per method, cell and alpha is in `m2c-preregistration-v4.0.0.md`.

## Next
1. Finish M2c: wait for the run, rerun the failed job, fetch, score, commit run dirs, write `m2c-results`.
2. M2b (about 52 h): drlCW, Patras DAC, model-based static, contextual UCB; BLADE-style only after its appendices are read. Do not write code from memory of a paper.
3. M4: both RAFA ensembles are replaced by per-scenario RAFA, so re-plan M4 with the user (the plan assumed a pooled actor). Commit the analysis spec before any M4 run.
Ask the user for the compute platform before launching a batch. Use tracked background watchers (until loop, exit on completion or first failure) rather than polling.
