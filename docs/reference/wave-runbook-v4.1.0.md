# Wave runbook (v4.1.0)

How one batch of an approved wave runs. Design: `docs/design/measurement-modes-v4.1.0.md`. Status on 2026-11-14:
the scripts are tested locally (section 4); `build-image` passed on GitHub (image digest in the design doc, section 7); `wave-run` and `wave-dispatch` have not run yet.

## 1. One-time setup by people

Repository owner (main account):
1. After the first `build-image` run, open the package `mac-world-run` (Profile, Packages) and set its visibility to
   public, so the forks can pull it without a token.
2. Add each fork token as an Actions secret `FORK_TOKEN_0` .. `FORK_TOKEN_6` (Settings, Secrets and variables, Actions).

Each fork owner (7 other accounts):
1. Fork `sohanroy676/mac-world` with all branches (untick "copy the main branch only").
2. Settings, General, Default branch: choose the branch that holds `.github/workflows/wave-run.yml`
   (`claude/project-thread-o7nshg` today; `feature/v4` after the merge). `workflow_dispatch` only works for
   workflows on the default branch.
3. Actions tab: enable workflows for the fork.
4. Create a fine-grained personal access token: repository access = only the fork, permission
   "Actions: Read and write", nothing else, expiry 30 days. Send it to the repository owner. The token can start
   workflows on that fork and nothing more.

## 2. One batch

1. Jobs: `cw_search_v4_1_0.py propose ...` (or another generator) writes `batch.json`.
2. Packs: `python3 .github/scripts/make_packs.py batch.json --shards 7 --lanes 4 --minutes 40 --out .github/waves/<wave>-<n>-packs.json`.
3. `.github/waves/dispatch.json`: wave name, packs path, image digest, `max_parallel` (5 in Wave 0, 20 later),
   `cap_lab_h` (the cap approved for the wave), `spent_lab_h` (sum of the wave's earlier batches), shard list.
4. Commit and push both files. `wave-dispatch` starts one `wave-run` per shard and refuses a batch over the cap.
5. Each shard runs its packs in the pinned image and publishes `summaries-<run>.jsonl` and one tarball per pack as
   assets of the release `wave-<wave>-s<k>` in its own repository.
6. Collect: `python3 .github/scripts/collect_wave.py .github/waves/dispatch.json --out docs/figures/<wave>/summaries.jsonl --retry retry.json`.
   Exit 0 = complete, 2 = jobs missing (retry batch written), 3 = two machines disagree on a trace hash.
7. A retry batch goes through steps 2-6 once more with the shard list rotated, so a job lands on a different fork.

## 3. Rules that protect the accounts

- No scheduled triggers. A batch starts only from a pushed `dispatch.json`.
- Wave 0 uses `max_parallel` 5; a fork goes to 20 only after its Wave 0 shard passed.
- At most about 6 hours of full load per fork per day.

## 4. What was tested (2026-11-14, local container, Ubuntu 22.04, GCC 11.4, Python 3.7.12)

- `make_packs.py`, `run_pack.py`, `run_job.py` summaries, `cw_search_v4_1_0.py` rounds 0 and 1, `top`, and
  `collect_wave.py --local`: one pass on the tiny cells `t222` (f1, f3) and `t23` (f2), 85 runs.
- `build-image.yml`: passed on GitHub Actions (run 43649676348).
- Not tested: `wave-run.yml`, `wave-dispatch.yml`, `dispatch_wave.py` against the GitHub API, the
  release download path of `collect_wave.py`. These need the forks.
- Hugging Face Spaces queue-at-boot: not started.
