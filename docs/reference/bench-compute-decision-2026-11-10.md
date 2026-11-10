# Compute decision: GitHub Actions vs Hugging Face Space (2026-11-10, DRAFT, soak pending)

Goal: least wall-clock to finish the remaining v4 job list. Labels: **M** = measured today, **E** = estimate from measured numbers, **U** = unverified.
Cell = 20,40 APs, beb, seed 0, 1500 steps (`tools/bench/run_bench.sh`). "Lab-hour" = one hour of the plan's serial lab time (lab cell 16-21 min, about 1037 s).

## Measured (M)
| Platform | CPU | 1 cell | Many at once | Cells/h |
|---|---|---|---|---|
| Actions runner (4 vCPU = 2 cores x 2) | AMD EPYC 7763 (2026-11-03) | 1037 s | - | 3.5 |
| Actions runner | Intel Xeon 8370C | 957 s | 4 at once: 1593 s each | 9.0 per runner (2.4x of 1 cell) |
| Actions runner | AMD EPYC 9V45 | 310 s | 2 at once: 323 s each | 22.3 per runner |
| HF Space (16 CPU cgroup quota, host Xeon 8559C, load about 58) | Xeon 8559C | 553 s | 4: 550 s, 8: 556 s, 16: 567 s | 25.8 / 51.5 / 100.6 |

- Actions runner CPU is not selectable and varies 3.3x (310 to 1037 s per cell). Build, python and apt timings vary with it too.
- HF scaling is linear to 16. CPU steal 0.002 %. The Space has a hard 16 CPU limit (cgroup `1600000 100000`); at 16 cells it is throttled in 84 % of periods but only 2.5 % slower, so 16 is the useful maximum.
- Actions concurrency: M2c run 42774734240 ran 20 jobs at once (queue 1-2 s for the first 20, later jobs waited 1.5-3 h for a slot), 30 jobs, 49.6 job-hours, 5 h 57 min wall; packing efficiency only 42 % because jobs were 40 min to 3 h long. A job failed on an apt 404 (needs rerun).
- ns-3 build cache (actions/cache, 257 MB archive, 1045 MB build dir): save 44 s; hit restore 8 s, configure + dry run 108 s versus 439 s clean build on another runner (CPU differed, so the saving of about 5 min is indicative only).

## Estimates (E)
Remaining list per plan rev 10: M2b 52 + M4 109 = 161 lab-hours (M4 must be re-planned; M5 adds 91 = 252). Throughput in lab-hours per wall-hour:
- HF at 16 cells: 16 x 1037/567 = 29 lab-h/h. 161 h: 5.5 h ideal, about 7 h at 80 % packing; 252 h: about 11 h.
- Actions, 20 runners x 4 cells each, Intel-class: 20 x 4 x 1037/1593 = 52 lab-h/h. 161 h: 3.1 h ideal, about 4 h at 80 %. AMD 9V45-class runners are 2.5x faster again (U for 4 at once).
- Both in parallel: about 81 lab-h/h; 161 h in about 2.5-3 h; 252 h in about 4 h.
- Learner cells are heavier than beb (independent 1531 s vs beb 1037 s on one runner) and 4-at-once scaling with torch is untested (U); set `OMP_NUM_THREADS=1`.

## Terms and risks
- Actions (verified wording, research/github-actions-feasibility-2026-11-03.md section 6): "disproportionate burden" and "unrelated to ... the software project" clauses; research sweeps are a grey area. Use here so far: about 50 runner-hours (M2c) + about 3 today. Remaining list would be about 60-110 runner-hours at 4 per runner (E). No schedule, keep `--check` in every job.
- HF (U until soak): free Space may sleep after inactivity, disk is ephemeral, restarts possible, ZeroGPU hardware used for CPU-only work may be restricted. Results leave via `GH_TOKEN` push to `bench/hf-results` (tested, works).

## Provisional recommendation (to confirm after the 6 h HF soak)
1. Primary: Actions, 20 jobs, 4 cells per job (needs a small change to `run_job.py` / matrix), ns-3 build cached.
2. In parallel: HF Space at 16 cells for roughly a third of the jobs, if the soak passes. Fallback if Actions is throttled or terms are questioned: HF alone (about 7 h for the 161-lab-hour list), then the lab PC.

Branches: bench/actions-scale (workflow `bench-actions.yml`), bench/hf-scale (harness), bench/hf-results (HF events).
