# Wave U3 summary: kwdirect retune on downlink cells (seeds 0-2, 60 s, second-half throughput, Mbps)

Run: `run-packs` 45912736278 (branch claude/project-thread-qtjqjo, 324 jobs, 323 pass; one job, `u3-d4-kw-e0.1-d0.1-t0.3-a0-s0`, crashed in wandb's offline reader after finishing and is rerun separately, so that setting has n=2 in the table). Grid: eta in {0.1, 0.25, 0.5}, delta in {0.1, 0.2, 0.4}, tau in {0.3, 0.6, 1.0}, cells d3 and d4, alpha 0 and 1, seeds 0-2, 60 s. Top 8 per cell and alpha by U_alpha; no confidence intervals, no claims.

## Reading
- **Retuning does not help.** The best of 27 settings is within 0.02 of U of the default in every cell and alpha: d3 alpha 0 stays at BEB level (share -0.04), d3 alpha 1 reaches 0.43, d4 stays at 0.13-0.14 of the static gap.
- Mean CW in the U2 default runs on d4 is 17-18 (static optimum 4-12) and in d3 alpha 0 is 16-17: the controller settles near the 16 where BEB starts, so (inference) its throughput-only SPSA signal is too flat between CW 16 and the optimum to climb out in 60 s, not a gain/step-size problem.
- Decision: no further kwdirect tuning here. Confirmation (wave C1) uses the U2 default kwdirect and reports it as it is.

## Cell d3 alpha 0  (U_BEB 73.12, U_static 77.05 at f1-12-8-12, U_kwdirect default 72.94)

| eta | delta | tau | n | per-AP | U | share | feasible |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.2 | 0.6 | 3 | 33.7 / 5.7 / 33.6 | 72.98 | -0.04 | yes |
| 0.25 | 0.1 | 0.6 | 3 | 33.6 / 5.7 / 33.6 | 72.97 | -0.04 | yes |
| 0.5 | 0.1 | 0.6 | 3 | 33.6 / 5.7 / 33.6 | 72.96 | -0.04 | yes |
| 0.1 | 0.4 | 0.6 | 3 | 33.6 / 5.7 / 33.6 | 72.96 | -0.04 | yes |
| 0.25 | 0.2 | 0.3 | 3 | 33.6 / 5.7 / 33.6 | 72.96 | -0.04 | yes |
| 0.25 | 0.2 | 1 | 3 | 33.6 / 5.7 / 33.6 | 72.96 | -0.04 | yes |
| 0.1 | 0.2 | 1 | 3 | 33.6 / 5.8 / 33.6 | 72.95 | -0.04 | yes |
| 0.5 | 0.4 | 1 | 3 | 33.6 / 5.8 / 33.6 | 72.94 | -0.05 | yes |

Settings with fewer than 3 seeds (missing or failed jobs): 0

## Cell d3 alpha 1  (U_BEB 17.92, U_static 22.28 at f1-16-4-16, U_kwdirect default 19.80)

| eta | delta | tau | n | per-AP | U | share | feasible |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.1 | 0.3 | 3 | 29.0 / 8.6 / 29.0 | 19.81 | 0.43 | yes |
| 0.25 | 0.2 | 0.6 | 3 | 29.5 / 8.6 / 28.4 | 19.80 | 0.43 | yes |
| 0.5 | 0.1 | 0.3 | 3 | 29.6 / 8.1 / 30.0 | 19.76 | 0.42 | yes |
| 0.25 | 0.1 | 0.6 | 3 | 30.2 / 8.1 / 29.4 | 19.75 | 0.42 | yes |
| 0.5 | 0.2 | 0.6 | 3 | 30.0 / 8.1 / 29.4 | 19.73 | 0.41 | yes |
| 0.25 | 0.2 | 1 | 3 | 29.0 / 8.1 / 30.7 | 19.69 | 0.40 | yes |
| 0.5 | 0.1 | 0.6 | 3 | 30.2 / 7.9 / 30.1 | 19.67 | 0.40 | yes |
| 0.25 | 0.1 | 1 | 3 | 30.1 / 7.9 / 29.9 | 19.66 | 0.40 | yes |

Settings with fewer than 3 seeds (missing or failed jobs): 0

## Cell d4 alpha 0  (U_BEB 80.80, U_static 86.06 at f1-8-8-8-8, U_kwdirect default 81.49)

| eta | delta | tau | n | per-AP | U | share | feasible |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.2 | 0.6 | 3 | 26.8 / 13.9 / 14.0 / 26.7 | 81.50 | 0.13 | yes |
| 0.25 | 0.1 | 0.3 | 3 | 26.8 / 14.0 / 14.0 / 26.7 | 81.50 | 0.13 | yes |
| 0.25 | 0.4 | 1 | 3 | 26.8 / 14.0 / 14.0 / 26.8 | 81.50 | 0.13 | yes |
| 0.25 | 0.1 | 0.6 | 3 | 26.8 / 14.0 / 14.0 / 26.7 | 81.49 | 0.13 | yes |
| 0.1 | 0.4 | 0.6 | 3 | 26.8 / 14.0 / 14.0 / 26.8 | 81.49 | 0.13 | yes |
| 0.1 | 0.2 | 1 | 3 | 26.7 / 14.0 / 14.0 / 26.8 | 81.49 | 0.13 | yes |
| 0.25 | 0.2 | 0.6 | 3 | 26.8 / 14.0 / 14.0 / 26.7 | 81.49 | 0.13 | yes |
| 0.5 | 0.2 | 1 | 3 | 26.7 / 14.0 / 14.0 / 26.8 | 81.49 | 0.13 | yes |

Settings with fewer than 3 seeds (missing or failed jobs): 1

## Cell d4 alpha 1  (U_BEB 25.94, U_static 29.07 at f1-12-4-4-12, U_kwdirect default 26.39)

| eta | delta | tau | n | per-AP | U | share | feasible |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.2 | 0.6 | 3 | 26.8 / 14.0 / 14.0 / 26.8 | 26.39 | 0.14 | yes |
| 0.5 | 0.1 | 0.6 | 3 | 26.7 / 14.0 / 14.0 / 26.7 | 26.39 | 0.14 | yes |
| 0.5 | 0.2 | 0.3 | 3 | 26.5 / 14.1 / 14.1 / 26.5 | 26.38 | 0.14 | yes |
| 0.5 | 0.4 | 0.6 | 3 | 26.4 / 14.2 / 13.9 / 26.8 | 26.38 | 0.14 | yes |
| 0.5 | 0.1 | 0.3 | 3 | 26.8 / 13.9 / 14.2 / 26.5 | 26.38 | 0.14 | yes |
| 0.25 | 0.4 | 0.6 | 3 | 26.5 / 14.1 / 14.0 / 26.5 | 26.35 | 0.13 | yes |
| 0.5 | 0.4 | 0.3 | 3 | 26.9 / 13.8 / 14.4 / 26.0 | 26.34 | 0.13 | yes |
| 0.1 | 0.2 | 0.6 | 3 | 26.8 / 13.9 / 14.0 / 26.7 | 26.33 | 0.12 | yes |

Settings with fewer than 3 seeds (missing or failed jobs): 0
