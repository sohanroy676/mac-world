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

## Not yet verified
Learner results with 4 lanes per runner (torch threads): compare sha256 of the same job run alone, in a pack, and with `pin`.
