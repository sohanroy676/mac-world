# Test: two Hugging Face Spaces on one account (2026-11-13)

Question: does a second Space get its own 16 CPUs, so two Spaces double the HF throughput? Branch `bench/two-spaces` (from feature/v4 bcdef6fc).

Method: `.github/jobs/two-spaces-test.json` = 32 identical-cost beb cells (20,40, 1500 steps). Space A runs shard `0/2`, Space B shard `1/2` (16 cells each, 16 lanes), started within a minute of each other. Both set variable `REF=bench/two-spaces`. Results and per-job start/end times land in `bench/hf-results` under `hf-jobs/two-spaces-test/` (`status-shard0of2.json`, `status-shard1of2.json`).

Reference (measured 2026-11-11): 16 such cells alone on one Space take 593-607 s each.

Decision rule (set before running): both shards' cells within 650 s each and overlapping in time -> separate CPU, two Spaces double throughput; about 1200 s each -> shared, no gain; in between -> partly shared, report the number.
## Result (measured, 2026-11-13)
- Both Spaces ran 16 cells at once, started 3 s apart (03:59:44 and 03:59:47 UTC), overlapped for 655 s, all 32 jobs PASS.
- Cell time: Space A median 640 s (588-688), Space B median 643 s (621-654), versus 593-607 s for 16 cells on one Space alone: about 6-7 % slower each.
- 32 cells finished in 688 s = about 167 cells/h, against about 100 cells/h for one Space: **1.7x**. The decision rule (each within 650 s median and overlapping) is met: a second Space on the same account gets its own CPUs, with a small slowdown (shared host).
- Not tested: three or more Spaces, hours-long runs with two Spaces, learner cells at 16 on each.

## Tools for more accounts (added on this branch, stub-tested only)
- `tools/hf/hfjobs.py` shard `k/n` (Shard box in the app): n Spaces split one batch, any accounts.
- `.github/scripts/split_batch.py <batch> <N> <prefix>`: N disjoint batch files for N forks (Actions jobs only).
- `.github/scripts/fetch_bundles.py <run> <out> <owner/repo>`: read a fork's run.
