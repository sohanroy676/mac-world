# Compute decision: GitHub Actions vs Hugging Face Space (2026-11-10, final)

Goal: least wall-clock to finish the remaining v4 job list. Labels: **M** = measured today, **E** = estimate from measured numbers, **U** = unverified.
Cell = 20,40 APs, beb, seed 0, 1500 steps (`tools/bench/run_bench.sh`). "Lab-hour" = one hour of the plan's serial lab time (lab cell 16-21 min, about 1037 s).

## Measured (M)
| Platform | CPU | 1 cell | Many at once | Cells/h |
|---|---|---|---|---|
| Actions runner (4 vCPU = 2 cores x 2) | AMD EPYC 7763 (2026-11-03) | 1037 s | - | 3.5 |
| Actions runner | Intel Xeon 8370C | 957 s | 4 at once: 1593 s each | 9.0 per runner (2.4x of 1 cell) |
| Actions runner | AMD EPYC 9V45 | 310 s | 2 at once: 323 s each | 22.3 per runner |
| Actions runners, rerun 2 (CPU model not read; slow class) | unknown | 1404 s and 1414 s | 2 at once: 1423 s each; 4 at once: 2224 s each | 2.5 (2 at once 5.1); 4 at once 6.5 per runner |
| HF Space (16 CPU cgroup quota, host Xeon 8559C, load about 58) | Xeon 8559C | 553 s | 4: 550 s, 8: 556 s, 16: 567 s | 25.8 / 51.5 / 100.6 |

- Actions runner CPU is not selectable and varies 4.5x (310 to 1414 s per cell). Across 5 runners: 310, 957, 1037, 1404, 1414 s. Running 2 at once costs nothing; 4 at once costs 1.7x per cell (Intel 8370C) and 1.6x (slow class), i.e. 4 per runner gives 2.4x and 2.5x of single-cell throughput. Build, python and apt timings vary with it too.
- HF scaling is linear to 16. CPU steal 0.002 %. The Space has a hard 16 CPU limit (cgroup `1600000 100000`); at 16 cells it is throttled in 84 % of periods but only 2.5 % slower, so 16 is the useful maximum.
- Actions concurrency: M2c run 42774734240 ran 20 jobs at once (queue 1-2 s for the first 20, later jobs waited 1.5-3 h for a slot), 30 jobs, 49.6 job-hours, 5 h 57 min wall; packing efficiency only 42 % because jobs were 40 min to 3 h long. A job failed on an apt 404 (needs rerun).
- ns-3 build cache (actions/cache, 257 MB archive, 1045 MB build dir): save 44 s; hit restore 8 s, configure + dry run 108 s versus 439 s clean build on another runner (CPU differed, so the saving of about 5 min is indicative only).

## HF 6 h soak (M, 17:20-23:22 UTC, 8 cells at once, run from the Space with the browser tab closed after start)
- One boot id for the whole run: no restart, no sleep, no throttling of the 8-cell load. 353 heartbeats, longest gap 64 s.
- 309 cells completed at 540-582 s (median 557 s; hourly medians 549-560 s, no drift): 51.2 cells/h sustained.
- 12 cells (3.7 %) exited after 2 s with rc 1. Probable cause (inference): run-directory name collision when two workers start in the same second. Harness fixed (serialised starts, branch bench/hf-scale commit 271c5b7), not yet re-run.
- Results left the Space every minute by GitHub push (`GH_TOKEN` secret), so a restart would lose at most the cells in flight.
- Not tested (U): runs longer than 6 h, 16 cells for hours (throttling begins at 16), idle sleep, a restart mid-run, a 54-72 min 10-AP cell (a cell is shorter than the soak, so it fits), learner cells (torch) at 16 at once, whether the host keeps this free hardware (Xeon 8559C, shared host, load about 58).

## Estimates (E)
Remaining list per plan rev 10: M2b 52 + M4 109 = 161 lab-hours (M4 must be re-planned; M5 adds 91 = 252). Throughput in lab-hours per wall-hour:
- HF at 16 cells: 16 x 1037/567 = 29 lab-h/h. 161 h: 5.5 h ideal, about 7 h at 80 % packing; 252 h: about 11 h.
- Actions, 20 runners x 4 cells each, Intel-class: 20 x 4 x 1037/1593 = 52 lab-h/h; slow-class runners (1404 s): 20 x 4 x 1037/2224 = 37 lab-h/h; a mix of 9V45-class runners raises it (U). 161 h: 3.1 h ideal, about 4 h at 80 %. AMD 9V45-class runners are 2.5x faster again (U for 4 at once).
- Both in parallel: about 81 lab-h/h; 161 h in about 2.5-3 h; 252 h in about 4 h.
- Learner cells are heavier than beb (independent 1531 s vs beb 1037 s on one runner) and 4-at-once scaling with torch is untested (U); set `OMP_NUM_THREADS=1`.

## Terms and risks
- Actions (verified wording, research/github-actions-feasibility-2026-11-03.md section 6): "disproportionate burden" and "unrelated to ... the software project" clauses; research sweeps are a grey area. Use here so far: about 50 runner-hours (M2c) + about 3 today. Remaining list would be about 60-110 runner-hours at 4 per runner (E). No schedule, keep `--check` in every job.
- HF (U until soak): free Space may sleep after inactivity, disk is ephemeral, restarts possible, ZeroGPU hardware used for CPU-only work may be restricted. Results leave via `GH_TOKEN` push to `bench/hf-results` (tested, works).

## Recommendation
Both together, split by reproducibility. Learner runs are bit-identical only within one CPU vendor (v4 sessionPrompt), and Actions hands out AMD and Intel runners at random, while the HF Space is always one Xeon 8559C.
1. **HF Space, 16 lanes: all learner cells** (RAFA, Global, PF, CCOD, DDPG-based rivals). Keeps each comparison on one CPU. About 29 lab-h/h.
2. **Actions, 20 jobs x 4 cells: non-learned cells** (BEB, static, IdleSense, UCB-type references), which are byte-identical across platforms, plus overflow. 37-52 lab-h/h, higher on 9V45 runners (U). Needs `run_job.py`/matrix change to run 4 commands per job and a build cache step.
3. Time (E): 161 lab-hours (M2b + M4) in about 3 h wall with both; HF alone about 7 h; Actions alone about 4-5.5 h; +91 lab-hours for M5 adds about 1.2 h (both), 3 h (HF alone).
4. **Fallback:** Space dies or is restricted -> move learner cells to Actions on one pinned runner type is not possible, so run them there and re-run any cross-vendor comparison arm on the same vendor; Actions throttled or terms questioned -> HF alone (about 7 h), then the lab PC.
Open risks: Actions terms are a grey area (about 50 runner-hours used so far in M2c, 4-per-job use would be 60-110 more, E); the learner share of the job list is not known here, so the 3 h figure assumes a balanced split.
