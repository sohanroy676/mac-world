# Test: two Hugging Face Spaces on one account (2026-11-13)

Question: does a second Space get its own 16 CPUs, so two Spaces double the HF throughput? Branch `bench/two-spaces` (from feature/v4 bcdef6fc).

Method: `.github/jobs/two-spaces-test.json` = 32 identical-cost beb cells (20,40, 1500 steps). Space A runs shard `0/2`, Space B shard `1/2` (16 cells each, 16 lanes), started within a minute of each other. Both set variable `REF=bench/two-spaces`. Results and per-job start/end times land in `bench/hf-results` under `hf-jobs/two-spaces-test/` (`status-shard0of2.json`, `status-shard1of2.json`).

Reference (measured 2026-11-11): 16 such cells alone on one Space take 593-607 s each.

Decision rule (set before running): both shards' cells within 650 s each and overlapping in time -> separate CPU, two Spaces double throughput; about 1200 s each -> shared, no gain; in between -> partly shared, report the number.
Result: pending.
