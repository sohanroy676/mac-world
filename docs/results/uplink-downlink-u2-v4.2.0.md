# Wave U2 summary (seeds 0-2, exact static 30 s, kwdirect 60 s, second-half throughput, Mbps)

Runs: `run-packs` 45887657599 (cells u3, d3, b3) and 45887661143 (cells m3, d4, b4), branch claude/project-thread-qtjqjo, commit e414291; 1188 of 1188 runs `--check PASS`. Pilot: run 45882374476 (9/9 PASS). Analysis: `.github/scripts/apdir_u2_analyse.py` against the U1 BEB runs. Seeds 0-2 only (n=3), no confidence intervals, no claims. The 'static' rows are the best exact static grid point (CW 4..256, `--cwHold`) that meets the fair floors with 5 % slack, chosen on the same seeds it is scored on, so it is an optimistic oracle.

## Reading (fact from the tables; inference marked)
- Exact low-CW static beats the old rounded grid and BEB everywhere: the best points include CW 4-12 for the middle AP (d3 12-8-12 at alpha 0, d4 8-8-8-8, m3 128-4-128). The U1 oracles clamped at CW 16 were not final; these are.
- kwdirect (v4.1.0 settings, 60 s, not retuned for these cells) reaches 0.78-1.0 of the static gap on uplink, both and mixed 3-AP cells at alpha 0 and 1, but only -0.05 to 0.43 on the downlink cells d3 (alpha 0 and 1) and 0.03-0.14 on d4. Inference: its per-AP CW writes assume the STAs' contention; with downlink the AP itself is the contender, so the controller's update direction and gain need retuning for `d`.
- Alpha 4 share is not meaningful: BEB's starved middle AP (0.4-0.5 Mbps) makes U_BEB hugely negative (-24210, -77360), so share rounds to 1.00 whatever kwdirect does. Compare U_kwdirect with U_static directly: kwdirect is below static in every alpha-4 cell (e.g. m3 -11.86 vs -2.86), and b3 alpha 4 violates the floors.
- Shares above 1.0 (u3 alpha 0: 1.46, b4 alpha 0: 1.30) mean kwdirect beat the grid's best point on throughput at alpha 0; the grid is coarse.

## Cell b3  (BEB 37.8 / 0.5 / 37.5, floors 25.3 / 0.5 / 25.3)

| alpha | method | per-AP | U | share | feasible |
|---|---|---|---|---|---|
| 0 | beb | 37.8 / 0.5 / 37.5 | 75.85 | - | yes |
| 0 | f1-64-64-64 | 39.4 / 0.8 / 39.3 | 79.47 | 1.00 | yes |
| 0 | kwdirect | 39.2 / 0.7 / 39.1 | 79.05 | 0.88 | yes |
| 1 | beb | 37.8 / 0.5 / 37.5 | -3.11 | - | yes |
| 1 | f1-128-32-128 | 25.8 / 11.4 / 25.5 | 20.15 | 1.00 | yes |
| 1 | kwdirect | 31.8 / 6.0 / 29.2 | 17.10 | 0.87 | yes |
| 4 | beb | 37.8 / 0.5 / 37.5 | -24210.31 | - | yes |
| 4 | f1-128-32-128 | 25.8 / 11.4 / 25.5 | -2.65 | 1.00 | yes |
| 4 | kwdirect | 25.3 / 8.1 / 20.8 | -6.89 | 1.00 | NO |

## Cell b4  (BEB 29.6 / 7.7 / 9.9 / 26.6, floors 18.4 / 7.7 / 9.9 / 18.4)

| alpha | method | per-AP | U | share | feasible |
|---|---|---|---|---|---|
| 0 | beb | 29.6 / 7.7 / 9.9 / 26.6 | 73.80 | - | yes |
| 0 | f1-64-64-64-64 | 29.5 / 10.1 / 12.8 / 26.3 | 78.65 | 1.00 | yes |
| 0 | kwdirect | 30.6 / 9.4 / 12.2 / 27.9 | 80.11 | 1.30 | yes |
| 1 | beb | 29.6 / 7.7 / 9.9 / 26.6 | 17.90 | - | yes |
| 1 | f1-128-64-64-128 | 23.8 / 15.2 / 15.6 / 23.3 | 25.79 | 1.00 | yes |
| 1 | kwdirect | 27.1 / 12.5 / 13.6 / 25.8 | 24.79 | 0.87 | yes |
| 4 | beb | 29.6 / 7.7 / 9.9 / 26.6 | -11.11 | - | yes |
| 4 | f1-128-32-32-128 | 22.7 / 15.1 / 16.8 / 21.0 | -2.32 | 1.00 | yes |
| 4 | kwdirect | 27.4 / 12.2 / 13.3 / 26.4 | -3.61 | 0.85 | yes |

## Cell d3  (BEB 34.0 / 5.2 / 33.9, floors 24.4 / 5.2 / 24.4)

| alpha | method | per-AP | U | share | feasible |
|---|---|---|---|---|---|
| 0 | beb | 34.0 / 5.2 / 33.9 | 73.12 | - | yes |
| 0 | f1-12-8-12 | 35.9 / 5.3 / 35.9 | 77.05 | 1.00 | yes |
| 0 | kwdirect | 33.6 / 5.7 / 33.6 | 72.94 | -0.05 | yes |
| 1 | beb | 34.0 / 5.2 / 33.9 | 17.92 | - | yes |
| 1 | f1-16-4-16 | 26.6 / 13.1 / 26.6 | 22.28 | 1.00 | yes |
| 1 | kwdirect | 29.5 / 8.6 / 28.4 | 19.80 | 0.43 | yes |
| 4 | beb | 34.0 / 5.2 / 33.9 | -23.79 | - | yes |
| 4 | f1-16-4-16 | 26.6 / 13.1 / 26.6 | -1.84 | 1.00 | yes |
| 4 | kwdirect | 24.8 / 9.8 / 27.9 | -3.88 | 0.91 | yes |

## Cell d4  (BEB 26.7 / 13.7 / 13.7 / 26.7, floors 20.2 / 13.7 / 13.7 / 20.2)

| alpha | method | per-AP | U | share | feasible |
|---|---|---|---|---|---|
| 0 | beb | 26.7 / 13.7 / 13.7 / 26.7 | 80.80 | - | yes |
| 0 | f1-8-8-8-8 | 29.5 / 13.6 / 13.6 / 29.4 | 86.06 | 1.00 | yes |
| 0 | kwdirect | 26.8 / 14.0 / 14.0 / 26.7 | 81.49 | 0.13 | yes |
| 1 | beb | 26.7 / 13.7 / 13.7 / 26.7 | 25.94 | - | yes |
| 1 | f1-12-4-4-12 | 24.4 / 17.5 / 17.6 / 24.3 | 29.07 | 1.00 | yes |
| 1 | kwdirect | 26.8 / 14.0 / 14.0 / 26.8 | 26.39 | 0.14 | yes |
| 4 | beb | 26.7 / 13.7 / 13.7 / 26.7 | -2.94 | - | yes |
| 4 | f1-16-4-4-16 | 22.3 / 18.7 / 18.7 / 22.2 | -1.62 | 1.00 | yes |
| 4 | kwdirect | 21.9 / 14.9 / 13.9 / 21.5 | -2.90 | 0.03 | yes |

## Cell m3  (BEB 37.9 / 0.4 / 37.8, floors 25.3 / 0.4 / 25.3)

| alpha | method | per-AP | U | share | feasible |
|---|---|---|---|---|---|
| 0 | beb | 37.9 / 0.4 / 37.8 | 76.03 | - | yes |
| 0 | f1-64-64-64 | 39.7 / 0.4 / 39.7 | 79.85 | 1.00 | yes |
| 0 | kwdirect | 39.5 / 0.6 / 39.5 | 79.52 | 0.91 | yes |
| 1 | beb | 37.9 / 0.4 / 37.8 | -6.89 | - | yes |
| 1 | f1-128-4-128 | 28.8 / 10.9 / 28.2 | 21.80 | 1.00 | yes |
| 1 | kwdirect | 32.8 / 4.3 / 33.6 | 15.52 | 0.78 | yes |
| 4 | beb | 37.9 / 0.4 / 37.8 | -77360.81 | - | yes |
| 4 | f1-128-4-128 | 28.8 / 10.9 / 28.2 | -2.86 | 1.00 | yes |
| 4 | kwdirect | 26.2 / 6.6 / 27.3 | -11.86 | 1.00 | yes |

## Cell u3  (BEB 35.6 / 1.5 / 35.6, floors 24.2 / 1.5 / 24.2)

| alpha | method | per-AP | U | share | feasible |
|---|---|---|---|---|---|
| 0 | beb | 35.6 / 1.5 / 35.6 | 72.63 | - | yes |
| 0 | f1-64-64-64 | 36.8 / 2.7 / 36.8 | 76.26 | 1.00 | yes |
| 0 | kwdirect | 38.0 / 1.8 / 38.1 | 77.91 | 1.46 | yes |
| 1 | beb | 35.6 / 1.5 / 35.6 | 6.12 | - | yes |
| 1 | f1-128-64-128 | 30.0 / 8.3 / 30.0 | 20.07 | 1.00 | yes |
| 1 | kwdirect | 29.3 / 8.5 / 29.3 | 19.84 | 0.98 | yes |
| 4 | beb | 35.6 / 1.5 / 35.6 | -1080.81 | - | yes |
| 4 | f1-128-32-128 | 24.4 / 11.8 / 24.4 | -2.51 | 1.00 | yes |
| 4 | kwdirect | 26.9 / 9.9 / 26.7 | -3.77 | 1.00 | yes |
