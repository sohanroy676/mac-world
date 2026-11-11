# Running v4 jobs on Actions (4 jobs per runner) and on a Hugging Face Space (2026-11-11)

Branch `bench/lanes` (from feature/v4 3f52442). Decision and numbers: docs/reference/bench-compute-decision-2026-11-10.md on bench/actions-scale.
Status of each claim is in the thread; anything not yet run is marked **untested**.

## One batch file for both platforms
`{"lanes": 4, "packs": 20, "jobs": [ {id, args|cmds, ref?, pin?, on?, w?} ]}` in `.github/jobs/packs-current.json`.
- `on`: "hf" or "actions". Default (`.github/scripts/jobsplit.py`): jobs whose `--mode` is a learner go to **hf** (one CPU type, so comparisons stay on one CPU); `beb`, `static`, `idlesense` jobs go to **actions** (byte-identical on every CPU).
- `w`: estimated minutes, used to balance packs (default: number of commands).

## Actions: `.github/workflows/run-packs.yml`
- Push to `bench/lanes*` or `feature/v4*` that changes `.github/jobs/packs-current.json`, or run it by hand.
- `make_matrix.py` puts the actions jobs into `packs` matrix entries (longest first, balanced); `run_pack.py` runs each pack's jobs `lanes` at a time (new job starts when a lane frees, starts 2.5 s apart); each job is still one `run_job.py` call, so its commands stay in order.
- `fetch_bundles.py` now reads several BUNDLE blocks per log (one per job).
- ns-3 build is cached (`actions/cache`).
- Code changes outside CI: `run_job.py` finds its run dir from the trainer's `out:` line (the old before/after glob breaks with parallel jobs); the trainer creates its run dir with an atomic `makedirs` (the old exists-then-create check could crash two same-second starts: probable cause of the 2 s failures seen in the HF soak).

## Hugging Face: `tools/hf/`
- `app.py` (Gradio, buttons: setup, run batch), `hfjobs.py` (runs the batch's `hf` jobs 16 at a time with the same `run_job.py`), `packages.txt`, `requirements.txt` from bench/hf.
- Every finished job is pushed to branch `bench/hf-results`: `hf-jobs/<batch>/<job>.tar.gz` + `.result.txt`; `status.json` every minute. After a restart the batch resumes (jobs whose result says PASS are skipped). Needs the `GH_TOKEN` secret.
- Space settings: README frontmatter `sdk: gradio`, `app_file: app.py`, `python_version: 3.7`; optional variable `AUTOSTART=batch:.github/jobs/packs-current.json`.
- Tested here with a stub runner (no token): queue, lanes, resume logic. **Untested on a real Space**: the setup against this branch, real pushes of tarballs, 16 learner jobs at once.

## Actions test result (run 42987319968, 16 jobs, 2 packs x 4 lanes, all PASS, measured)
| Pack | Runner CPU | 4 heavy cells at once (20,40 beb, 1500 steps) | Pack total |
|---|---|---|---|
| pack-00 | AMD EPYC 9V45 | 568-575 s each (single cell on a 9V45 earlier: 310 s) = 25 cells/h | 606 s (incl. 4 small learner jobs) |
| pack-01 | AMD EPYC 9V74 | 1458-1462 s each = 9.9 cells/h | 1514 s |
- Lane safety: 4 same-seed `independent` learner jobs at once gave one identical trace sha (`db439d30...`), equal to the earlier single-job Actions result in docs/results/m3-step0-checks-v4.0.0.md; 4 pinned jobs one identical sha (`313f0f68...`). So lanes do not change a small learner cell's result (heavy learner cells **untested**).
- `fetch_bundles`-style parsing decoded all 8 bundles of each pack log (48 files each).
- Runner CPU is still random (9V45 vs 9V74 = 2.5x apart); build on a cache miss took 3-4 min on these runners.
- Not yet verified: cache hit in run-packs (the key was new), 20 packs at once, heavy learner cells with 4 lanes, HF run on this branch (steps sent to the user).

## HF test result (Space, 2026-11-11, batch hf-test.json, measured)
- 22 jobs ran 16 at a time on the Xeon 8559C Space, all exit 0 and `--check` PASS. 16 heavy beb cells (20,40, 1500 steps) at once: 593-607 s each (about 96 cells/h).
- The 8 beb traces with seeds 0-7 are **byte-identical** to the Actions run (same sha256 for the same seed), so non-learned jobs can go to either platform.
- Learner (`independent`, 2,3): the 4 same-seed jobs on HF give one sha (`f4ddded7...`), different from the AMD Actions sha (`db439d30...`): learner results differ by CPU vendor, as already documented, so keep each comparison on one platform.
- Push: 21 of 22 result files reached `bench/hf-results`; GitHub answered HTTP 409 to concurrent commits and one `result.txt` exhausted its retries (hf-beb2040-4). Fixed by serialising pushes (not yet re-run on the Space); the resume logic will rerun only jobs without a result file.
