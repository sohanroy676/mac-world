# Wave U1 summary (seeds 0-2, 30 s, throughput over the second half, Mbps)

Run: Actions `run-packs` 45832945993 (branch claude/project-thread-qtjqjo, commit 21d54d0), 486 of 504 runs, all `--check PASS`, no failures. The 18 DAC (Tc 514 us) runs were NOT run: `jobsplit.py` sends non-listed modes to the HF queue, so they were skipped by design; they are rerun together with the grid extension in `apdir-w1c-ext.json` (jobs now `on: actions`). Analysis: `.github/scripts/apdir_w1_analyse.py`. Seeds 0-2, n=3, selection seeds only, so no claim.

**Caveat (fact):** in several cells the best static point sits on the lower edge of the grid (middle AP CW 32, d3 and d4 at 32 for every AP). The grid needs extending down to CW 16 before any oracle or ceiling is quoted. The grid is also symmetric (edge, middle, ..., edge), which hides asymmetric optima in the mixed cell m3.

## Cell b3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 37.8 / 0.5 / 37.5 | 75.8 | 0.52 | 6.60 | 3 |
| idlesense | 36.7 / 0.2 / 36.7 | 73.6 | 0.19 | 5.52 | 3 |
| static-128-32-128 (best PF) | 25.7 / 11.4 / 25.4 | 62.5 | 11.41 | 8.91 | 3 |
| static-256-128-256 (best min-AP) | 14.6 / 20.6 / 15.4 | 50.6 | 14.60 | 8.44 | 3 |

## Cell b4

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 29.6 / 7.7 / 9.9 / 26.6 | 73.8 | 7.67 | 11.00 | 3 |
| idlesense | 31.1 / 6.2 / 10.3 / 27.1 | 74.7 | 6.16 | 10.89 | 3 |
| static-128-64-64-128 (best PF) | 23.7 / 15.2 / 15.6 / 23.3 | 77.8 | 15.23 | 11.78 | 3 |
| static-256-64-64-256 (best min-AP) | 18.0 / 17.7 / 18.4 / 16.7 | 70.9 | 16.69 | 11.50 | 3 |

## Cell d3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 34.0 / 5.2 / 33.9 | 73.1 | 5.21 | 8.70 | 3 |
| idlesense | 36.3 / 0.2 / 36.3 | 72.8 | 0.21 | 5.64 | 3 |
| static-32-32-32 (best PF) | 25.3 / 8.9 / 25.2 | 59.5 | 8.93 | 8.65 | 3 |
| static-64-32-64 (best min-AP) | 15.2 / 16.1 / 15.1 | 46.4 | 15.15 | 8.22 | 3 |

## Cell d4

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 26.7 / 13.7 / 13.7 / 26.7 | 80.8 | 13.69 | 11.80 | 3 |
| idlesense | 27.6 / 8.4 / 8.1 / 27.9 | 72.1 | 8.14 | 10.87 | 3 |
| static-32-32-32-32 (best PF) | 22.5 / 13.4 / 13.4 / 22.5 | 71.8 | 13.42 | 11.42 | 3 |
| static-64-32-32-64 (best min-AP) | 15.4 / 15.7 / 15.8 / 15.3 | 62.2 | 15.31 | 10.97 | 3 |

## Cell m3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 37.9 / 0.4 / 37.8 | 76.0 | 0.35 | 6.22 | 3 |
| idlesense | 36.9 / 0.1 / 36.7 | 73.8 | 0.14 | 5.24 | 3 |
| static-256-32-256 (best PF) | 26.7 / 9.5 / 20.4 | 56.7 | 9.55 | 8.56 | 3 |
| static-512-64-512 (best min-AP) | 19.7 / 10.9 / 11.1 | 41.8 | 10.92 | 7.78 | 3 |

## Cell u3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 35.6 / 1.5 / 35.6 | 72.6 | 1.46 | 7.52 | 3 |
| idlesense | 35.9 / 1.2 / 35.9 | 73.0 | 1.21 | 7.35 | 3 |
| static-128-64-128 (best PF) | 30.0 / 8.3 / 30.0 | 68.4 | 8.33 | 8.92 | 3 |
| static-256-64-256 (best min-AP) | 17.3 / 19.2 / 17.3 | 53.8 | 17.29 | 8.66 | 3 |
