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

## 5. Hugging Face Spaces (10 Spaces: 5 accounts, 2 Spaces each)

Decision (xyz, 2026-11-16): every Space pushes its results to the main repository. xyz holds all the HF accounts.
Status (2026-11-16): tested locally, two ways. (1) 12 tiny jobs in 3 packs, two packs at once, results to a stand-in folder:
all 12 PASS, a second pass skipped all 3 packs, the collector read them, and a batch over the cap was refused. (2) The GitHub
push path (create branch, create file, update file by sha, read back) against a mock GitHub API. **No real Space has run it
yet and the real GitHub API was not called** (Wave 0 does both). The first local test found a real bug: two packs started
within the same seconds made two `waf --run` calls rewrite `build/compile_commands.json` at once, one died, and its trainer waited
forever. Fixed with a start lock shared across packs (`run_pack.py`) and a per-job timeout (`run_job.py`, `JOB_TIMEOUT`).

One-time, per HF account (xyz or the owner):
1. Account at least 30 days old and in good standing (HF's documented rule for the free ZeroGPU Spaces; Wave 0 confirms).
2. Create 2 Spaces at huggingface.co/new-space under that account: SDK Gradio, hardware the same as xyz's existing two Spaces
   (Settings, Hardware). Names are free; send them to Claude as `owner/name`.
3. Upload to each Space root the four files: `tools/hf/space-README.md` as `README.md`, `tools/hf/app.py`,
   `tools/hf/packages.txt`, `tools/hf/requirements.txt` (Files tab, Add file, Upload files).
4. Settings, Variables and secrets:
   - Variables: `WAVE_WORKER` = `1`, `REF` = `claude/project-thread-o7nshg` (the branch that holds `.github/waves/dispatch.json`;
     `feature/v4` after the merge), `LANES` = `16`.
   - Secret: `GH_TOKEN` = a fine-grained GitHub token for `sohanroy676/mac-world` only, permission "Contents: Read and write",
     expiry 30 days. One token can be used in all 10 Spaces. It can write to every branch of the main repository, so keep expiry short.
5. Leave the Space running. It builds the code on first boot (about 10 to 15 minutes), then looks at `dispatch.json` every 5 minutes
   and does nothing until a batch lists it. A Space that sleeps or restarts resumes: packs whose summaries are already on GitHub are skipped.

What the worker does is in the docstring of `tools/hf/wave_worker.py`. Each Space writes to its own branch `wave-results-s<shard>`
(so ten Spaces never commit to one branch at once), under `<wave>/s<shard>/`: one `.summaries.jsonl` and one `.pack.txt` per pack.
Traces stay on the Space disk; only their SHA-256 goes to GitHub.

`dispatch.json` lists the Spaces: `"hf": [{"space": "owner/name", "repo": "sohanroy676/mac-world", "shard": k}, ...]`, with shard
numbers after the forks' (7 forks = shards 0-6, Spaces 7-16). A Space's own name comes from the `SPACE_ID` variable HF sets.

## 6. State after Wave 0 (2026-11-16)

- **Hugging Face Spaces are not used.** All 5 accounts were locked by Hugging Face during Wave 0 (terms of service).
  Section 5 is kept for the record only. Dispatch files carry no `"hf"` entries.
- **Forks:** 6 forks, `max_parallel` 5 (quarter load), about 6 hours of running per fork per day, no schedules
  (owner decision, 2026-11-16). Do not dispatch a new batch to a fork whose previous run is still going.
- **Collecting:** `date -u > .github/waves/collect.trigger`, commit, push. Workflow `wave-collect` runs
  `collect_wave.py` and commits `<wave>/summaries.jsonl` and `<wave>/status.txt` (with the state of each fork's last runs)
  to branch `wave-collected`.
- **Any push of `.github/waves/dispatch.json` starts the forks.** Change it only to start a batch.
