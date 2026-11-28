# Wave U1 summary (seeds 0-2, 30 s, throughput over the second half, Mbps)

Waves U1 + U1c (`run-packs` runs 45832945993 and 45859492307, commits 21d54d0 and be4c6ee, branch claude/project-thread-qtjqjo): 1098 runs, all `--check PASS`, no failures (486 in U1, 612 in U1c = grid extension below CW 32 plus the 18 DAC runs, which U1 skipped because `jobsplit.py` sends non-listed modes to the HF queue). Analysis: `.github/scripts/apdir_w1_analyse.py`. Seeds 0-2, n=3, selection seeds only: no claims, no confidence intervals. Static grid: (edge, middle, ..., edge) with symmetric edges, CW from 16 (the clamp default) to 512; AP-asymmetric optima are not covered.

## Reading (fact from the tables; inference marked)
- BEB starves the middle AP of the 3-AP chain in every direction (0.35-5.2 Mbps; worst in `b`, `m` mixes). The 4-AP chain is milder.
- IdleSense (published rule, target 3.3) is no better than BEB and often worse for the middle AP (0.1-0.2 Mbps in the 3-AP cells).
- DAC (Tc 514 us) is about level with BEB on the middle AP (0.5->2.0 b3, 0.4->2.4 m3) and keeps total throughput; it does not lift the middle AP anywhere near the static oracle (9-15 Mbps).
- Best static PF point lifts the middle AP to 8-15 Mbps at a cost of 4-20 Mbps of sum throughput except in d4, where the best point is all-16 = BEB-like (BEB is already the PF optimum there, sum 81.5).
- Edge-of-grid caveat: d4 (all CW 16) and m3 (middle 16) sit on the CW 16 clamp, d3 (middle 16) too. The true optimum may be below 16 (needs `--cwLo` below 16, as in the v4.1.0 max-CW work). Not quoted as an oracle.
- Inference: the optimum direction depends on the mix: uplink wants the edges' CW well above the middle's (128/64/128); downlink wants a small CW everywhere (AP is a single contender per BSS), so one static point cannot serve all directions.

## Cell b3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 37.8 / 0.5 / 37.5 | 75.8 | 0.52 | 6.60 | 3 |
| dac514 | 38.0 / 2.0 / 37.9 | 77.9 | 2.00 | 7.96 | 3 |
| idlesense | 36.7 / 0.2 / 36.7 | 73.6 | 0.19 | 5.52 | 3 |
| static-128-32-128 (best PF) | 25.7 / 11.4 / 25.4 | 62.5 | 11.41 | 8.91 | 3 |
| static-128-16-128 (best min-AP) | 18.0 / 15.9 / 17.8 | 51.7 | 15.94 | 8.53 | 3 |

## Cell b4

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 29.6 / 7.7 / 9.9 / 26.6 | 73.8 | 7.67 | 11.00 | 3 |
| dac514 | 32.8 / 7.2 / 10.2 / 29.8 | 80.0 | 7.21 | 11.18 | 3 |
| idlesense | 31.1 / 6.2 / 10.3 / 27.1 | 74.7 | 6.16 | 10.89 | 3 |
| static-128-64-64-128 (best PF) | 23.7 / 15.2 / 15.6 / 23.3 | 77.8 | 15.23 | 11.78 | 3 |
| static-256-64-64-256 (best min-AP) | 18.0 / 17.7 / 18.4 / 16.7 | 70.9 | 16.69 | 11.50 | 3 |

## Cell d3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 34.0 / 5.2 / 33.9 | 73.1 | 5.21 | 8.70 | 3 |
| dac514 | 33.6 / 5.7 / 33.6 | 72.9 | 5.72 | 8.77 | 3 |
| idlesense | 36.3 / 0.2 / 36.3 | 72.8 | 0.21 | 5.64 | 3 |
| static-24-16-24 (best PF) | 26.6 / 10.4 / 26.6 | 63.7 | 10.43 | 8.91 | 3 |
| static-48-24-48 (best min-AP) | 17.6 / 15.8 / 17.5 | 51.0 | 15.83 | 8.49 | 3 |

## Cell d4

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 26.7 / 13.7 / 13.7 / 26.7 | 80.8 | 13.69 | 11.80 | 3 |
| dac514 | 26.8 / 14.0 / 13.9 / 26.8 | 81.5 | 13.95 | 11.85 | 3 |
| idlesense | 27.6 / 8.4 / 8.1 / 27.9 | 72.1 | 8.14 | 10.87 | 3 |
| static-16-16-16-16 (best PF) | 26.8 / 14.0 / 13.9 / 26.7 | 81.5 | 13.95 | 11.85 | 3 |
| static-32-16-16-32 (best min-AP) | 20.1 / 16.9 / 16.9 / 20.1 | 74.1 | 16.88 | 11.66 | 3 |

## Cell m3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 37.9 / 0.4 / 37.8 | 76.0 | 0.35 | 6.22 | 3 |
| dac514 | 37.6 / 2.4 / 37.8 | 77.7 | 2.36 | 8.12 | 3 |
| idlesense | 36.9 / 0.1 / 36.7 | 73.8 | 0.14 | 5.24 | 3 |
| static-256-16-256 (best PF) | 23.0 / 14.7 / 18.5 | 56.2 | 14.74 | 8.74 | 3 |

## Cell u3

| method | per-AP | sum | min-AP | PF | n |
|---|---|---|---|---|---|
| beb | 35.6 / 1.5 / 35.6 | 72.6 | 1.46 | 7.52 | 3 |
| dac514 | 38.2 / 1.6 / 38.2 | 78.0 | 1.60 | 7.76 | 3 |
| idlesense | 35.9 / 1.2 / 35.9 | 73.0 | 1.21 | 7.35 | 3 |
| static-128-64-128 (best PF) | 30.0 / 8.3 / 30.0 | 68.4 | 8.33 | 8.92 | 3 |
| static-256-64-256 (best min-AP) | 17.3 / 19.2 / 17.3 | 53.8 | 17.29 | 8.66 | 3 |
