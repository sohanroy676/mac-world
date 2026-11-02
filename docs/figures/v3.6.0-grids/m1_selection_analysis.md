# M1 selection-seed analysis (python seeds 0-2)

## s4 (10,10,10, hidden 1-3, loads , load 10.0)

alpha 0: oracle `static:64,64,64`, U gap over BEB 3.824 (BEB U SD 0.310), degenerate: False, floors ['24.07', '1.43', '24.07']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 72.21 | 1.43 | True | 72.21 | 0.00 ± 0.00 |
| static:64,256,64 | 3 | 79.67 | 0.51 | False | 79.67 | 1.95 ± 0.20 |
| static:64,128,64 | 3 | 78.62 | 1.26 | False | 78.62 | 1.68 ± 0.24 |
| static:64,64,64 | 3 | 76.03 | 2.78 | True | 76.03 | 1.00 ± 0.18 |
| static:128,256,128 | 3 | 75.11 | 2.86 | True | 75.11 | 0.76 ± 0.20 |
| static:32,256,32 | 3 | 73.08 | 0.20 | False | 73.08 | 0.23 ± 0.32 |
| idlesense | 3 | 72.94 | 1.20 | False | 72.94 | 0.19 ± 0.27 |

alpha 1: oracle `static:128,64,128`, U gap over BEB 14.344 (BEB U SD 1.194), degenerate: False, floors ['24.07', '1.43', '24.07']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 72.21 | 1.43 | True | 5.75 | 0.00 ± 0.00 |
| static:128,64,128 | 3 | 68.25 | 8.30 | True | 20.09 | 1.00 ± 0.20 |
| static:256,128,256 | 3 | 59.48 | 13.29 | True | 19.58 | 0.96 ± 0.21 |
| static:128,32,128 | 3 | 60.24 | 11.91 | True | 19.40 | 0.95 ± 0.20 |
| static:256,256,256 | 3 | 62.77 | 8.09 | True | 18.00 | 0.85 ± 0.21 |
| static:256,64,256 | 3 | 53.93 | 17.36 | False | 17.56 | 0.82 ± 0.21 |
| static:128,128,128 | 3 | 72.72 | 5.05 | True | 17.55 | 0.82 ± 0.21 |

alpha 2: oracle `static:256,128,256`, U gap over BEB 60.375 (BEB U SD 9.389), degenerate: False, floors ['24.07', '1.43', '24.07']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 72.21 | 1.43 | True | -76.56 | 0.00 ± 0.00 |
| static:256,128,256 | 3 | 59.48 | 13.29 | True | -16.19 | 1.00 ± 0.39 |
| static:128,32,128 | 3 | 60.24 | 11.91 | True | -16.67 | 0.99 ± 0.39 |
| static:256,64,256 | 3 | 53.93 | 17.36 | False | -16.73 | 0.99 ± 0.39 |
| static:512,256,512 | 3 | 49.46 | 15.93 | False | -18.21 | 0.97 ± 0.39 |
| static:128,64,128 | 3 | 68.25 | 8.30 | True | -18.72 | 0.96 ± 0.39 |
| static:256,256,256 | 3 | 62.77 | 8.09 | True | -19.67 | 0.94 ± 0.39 |

| run | per-AP Mbps | idle slots per AP (SD over seeds) | retry rate per AP |
|---|---|---|---|
| beb | 35.18, 1.43, 35.60 | 2.62 (0.02), 0.78 (0.03), 2.62 (0.01) | 0.383, 0.343, 0.382 |
| static:128,64,128 | 29.96, 8.30, 29.98 | 5.01 (0.00), 1.83 (0.01), 5.02 (0.00) | 0.159, 0.366, 0.159 |
| static:256,128,256 | 23.10, 13.29, 23.09 | 7.81 (0.05), 3.10 (0.02), 7.81 (0.02) | 0.096, 0.209, 0.096 |
| static:64,64,64 | 36.60, 2.78, 36.64 | 3.37 (0.01), 1.06 (0.02), 3.35 (0.00) | 0.251, 0.376, 0.250 |

## s5a (10,10,10, hidden 1-3, loads 150,150,1, load 150.0)

alpha 0: oracle `static:128,128,128`, U gap over BEB 4.439 (BEB U SD 0.247), degenerate: False, floors ['15.13', '10.85', '10.00']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 45.38 | 10.00 | True | 45.38 | 0.00 ± 0.00 |
| static:128,128,128 | 3 | 49.82 | 10.00 | True | 49.82 | 1.00 ± 0.12 |
| static:128,256,128 | 3 | 49.78 | 10.00 | False | 49.78 | 0.99 ± 0.13 |
| static:64,256,128 | 3 | 49.77 | 6.20 | False | 49.77 | 0.99 ± 0.14 |
| static:64,128,128 | 3 | 49.21 | 10.00 | False | 49.21 | 0.86 ± 0.11 |
| static:128,64,128 | 3 | 48.74 | 10.00 | True | 48.74 | 0.76 ± 0.15 |
| static:256,128,128 | 3 | 48.37 | 10.00 | True | 48.37 | 0.67 ± 0.12 |

alpha 1: oracle `static:128,128,128`, U gap over BEB 3.485 (BEB U SD 0.147), degenerate: False, floors ['15.13', '10.85', '10.00']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 45.38 | 10.00 | True | 9.78 | 0.00 ± 0.00 |
| static:128,128,128 | 3 | 49.82 | 10.00 | True | 13.26 | 1.00 ± 0.12 |
| static:128,64,128 | 3 | 48.74 | 10.00 | True | 13.21 | 0.98 ± 0.11 |
| static:256,128,128 | 3 | 48.37 | 10.00 | True | 12.97 | 0.92 ± 0.12 |
| static:256,256,128 | 3 | 47.45 | 10.00 | True | 12.15 | 0.68 ± 0.09 |
| static:64,64,128 | 3 | 47.76 | 10.00 | True | 12.07 | 0.66 ± 0.13 |
| static:256,64,128 | 3 | 47.85 | 10.00 | False | 11.91 | 0.61 ± 0.13 |

alpha 2: oracle `static:128,64,128`, U gap over BEB 2.970 (BEB U SD 0.278), degenerate: False, floors ['15.13', '10.85', '10.00']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 45.38 | 10.00 | True | -23.31 | 0.00 ± 0.00 |
| static:128,64,128 | 3 | 48.74 | 10.00 | True | -20.34 | 1.00 ± 0.23 |
| static:256,128,128 | 3 | 48.37 | 10.00 | True | -20.49 | 0.95 ± 0.24 |
| static:128,128,128 | 3 | 49.82 | 10.00 | True | -20.57 | 0.92 ± 0.25 |
| static:256,256,128 | 3 | 47.45 | 10.00 | True | -21.12 | 0.74 ± 0.23 |
| static:64,64,128 | 3 | 47.76 | 10.00 | True | -21.29 | 0.68 ± 0.26 |
| static:256,64,128 | 3 | 47.85 | 10.00 | False | -21.51 | 0.61 ± 0.24 |

| run | per-AP Mbps | idle slots per AP (SD over seeds) | retry rate per AP |
|---|---|---|---|
| beb | 24.53, 10.85, 10.00 | 2.62 (0.02), 2.29 (0.01), 18.51 (1.33) | 0.428, 0.509, 0.725 |
| static:128,128,128 | 24.33, 15.49, 10.00 | 4.09 (0.00), 3.17 (0.02), 18.70 (0.07) | 0.197, 0.241, 0.552 |
| static:128,64,128 | 18.77, 19.97, 10.00 | 3.51 (0.01), 2.57 (0.02), 10.68 (0.05) | 0.248, 0.331, 0.403 |

## s8p3 (10,10,10, hidden 1-3, loads , load 10.0)

alpha 0: oracle `static:64,256,64`, U gap over BEB -0.939 (BEB U SD 0.278), degenerate: True, floors ['25.49', '2.13', '25.49']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 76.46 | 2.13 | True | 76.46 | n/a |
| static:64,256,64 | 3 | 75.52 | 2.82 | True | 75.52 | n/a |
| static:64,128,64 | 3 | 73.33 | 5.03 | True | 73.33 | n/a |
| static:64,64,64 | 3 | 68.97 | 8.10 | True | 68.97 | n/a |
| static:128,256,128 | 3 | 63.08 | 8.06 | True | 63.08 | n/a |
| static:64,32,64 | 3 | 61.10 | 11.61 | True | 61.10 | n/a |
| static:128,128,128 | 3 | 59.63 | 13.25 | False | 59.63 | n/a |

alpha 1: oracle `static:64,64,64`, U gap over BEB 9.428 (BEB U SD 1.392), degenerate: False, floors ['25.49', '2.13', '25.49']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 76.46 | 2.13 | True | 10.72 | 0.00 ± 0.00 |
| static:64,64,64 | 3 | 68.97 | 8.10 | True | 20.15 | 1.00 ± 0.38 |
| static:128,128,128 | 3 | 59.63 | 13.25 | False | 19.64 | 0.95 ± 0.37 |
| static:64,32,64 | 3 | 61.10 | 11.61 | True | 19.61 | 0.94 ± 0.44 |
| static:128,256,128 | 3 | 63.08 | 8.06 | True | 18.08 | 0.78 ± 0.37 |
| static:64,128,64 | 3 | 73.33 | 5.03 | True | 17.69 | 0.74 ± 0.36 |
| static:128,64,128 | 3 | 53.92 | 17.34 | False | 17.55 | 0.72 ± 0.35 |

alpha 2: oracle `static:64,32,64`, U gap over BEB 36.267 (BEB U SD 6.934), degenerate: False, floors ['25.49', '2.13', '25.49']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 76.46 | 2.13 | True | -52.97 | 0.00 ± 0.00 |
| static:128,128,128 | 3 | 59.63 | 13.25 | False | -16.17 | 1.01 ± 0.48 |
| static:64,32,64 | 3 | 61.10 | 11.61 | True | -16.70 | 1.00 ± 0.47 |
| static:128,64,128 | 3 | 53.92 | 17.34 | False | -16.73 | 1.00 ± 0.47 |
| static:256,256,256 | 3 | 49.47 | 16.01 | False | -18.20 | 0.96 ± 0.48 |
| static:64,64,64 | 3 | 68.97 | 8.10 | True | -18.92 | 0.94 ± 0.48 |
| static:128,256,128 | 3 | 63.08 | 8.06 | True | -19.68 | 0.92 ± 0.48 |

| run | per-AP Mbps | idle slots per AP (SD over seeds) | retry rate per AP |
|---|---|---|---|
| beb | 37.13, 2.13, 37.20 | 2.90 (0.01), 0.92 (0.01), 2.91 (0.03) | 0.274, 0.391, 0.275 |
| static:64,256,64 | 36.30, 2.82, 36.40 | 5.91 (0.01), 1.91 (0.01), 5.89 (0.02) | 0.125, 0.185, 0.121 |
| static:64,32,64 | 24.71, 11.61, 24.77 | 4.53 (0.02), 2.00 (0.03), 4.52 (0.04) | 0.182, 0.500, 0.180 |
| static:64,64,64 | 30.40, 8.10, 30.46 | 5.05 (0.02), 1.80 (0.00), 5.04 (0.02) | 0.145, 0.368, 0.142 |

## s2 (20,40, hidden , loads , load 10.0)

alpha 0: oracle `static:512,512`, U gap over BEB 12.101 (BEB U SD 0.323), degenerate: False, floors ['9.19', '17.00']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 27.58 | 10.59 | True | 27.58 | 0.00 ± 0.00 |
| static:512,512 | 3 | 39.68 | 13.25 | True | 39.68 | 1.00 ± 0.06 |
| idlesense | 3 | 38.54 | 13.75 | True | 38.54 | 0.91 ± 0.15 |
| static:256,256 | 3 | 37.97 | 12.85 | True | 37.97 | 0.86 ± 0.05 |

alpha 1: oracle `static:512,512`, U gap over BEB 22.279 (BEB U SD 0.091), degenerate: False, floors ['9.19', '17.00']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 27.58 | 10.59 | True | -47.09 | 0.00 ± 0.00 |
| static:512,512 | 3 | 39.68 | 13.25 | True | -24.81 | 1.00 ± 0.01 |
| idlesense | 3 | 38.54 | 13.75 | True | -26.65 | 0.92 ± 0.09 |
| static:256,256 | 3 | 37.97 | 12.85 | True | -27.46 | 0.88 ± 0.03 |

alpha 2: oracle `static:512,512`, U gap over BEB 41.711 (BEB U SD 1.020), degenerate: False, floors ['9.19', '17.00']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 27.58 | 10.59 | True | -132.44 | 0.00 ± 0.00 |
| static:512,512 | 3 | 39.68 | 13.25 | True | -90.73 | 1.00 ± 0.07 |
| idlesense | 3 | 38.54 | 13.75 | True | -93.69 | 0.93 ± 0.02 |
| static:256,256 | 3 | 37.97 | 12.85 | True | -94.84 | 0.90 ± 0.08 |

| run | per-AP Mbps | idle slots per AP (SD over seeds) | retry rate per AP |
|---|---|---|---|
| beb | 10.59, 17.00 | 2.86 (0.01), 2.86 (0.01) | 0.637, 0.621 |
| static:512,512 | 13.25, 26.44 | 4.45 (0.04), 4.45 (0.04) | 0.200, 0.198 |

## Gates (proposed definitions; recorded as decisions)

G0a beb: idle ['2.86', '2.86'] SD ['0.01', '0.01'] -> PASS
G0a idlesense: idle ['5.49', '5.49'] SD ['0.04', '0.04'] -> PASS
G0a static:256,256: idle ['2.92', '2.92'] SD ['0.01', '0.01'] -> PASS
G0a static:512,512: idle ['4.45', '4.45'] SD ['0.04', '0.04'] -> PASS
G0b beb idle: edge 2.618 vs middle 0.778, |diff|/pooled SD = 86.0 -> PASS
G0b beb retry: edge 0.382 vs middle 0.343, |diff|/pooled SD = 1.6 -> FAIL
G0b idlesense idle: edge 8.078 vs middle 2.828, |diff|/pooled SD = 501.4 -> PASS
G0b idlesense retry: edge 0.109 vs middle 0.080, |diff|/pooled SD = 2.9 -> FAIL
G0b static:256,128,256 idle: edge 7.813 vs middle 3.097, |diff|/pooled SD = 186.4 -> PASS
G0b static:256,128,256 retry: edge 0.096 vs middle 0.209, |diff|/pooled SD = 46.2 -> PASS

## IdleSense convergence (published rule, selection seeds)

| cell | seed | AP | final median CW | first step within x2 and staying | settled by step 300 |
|---|---|---|---|---|---|
| s2 | 0 | 1 | 546 | 1491 | NO |
| s2 | 0 | 2 | 546 | 1491 | NO |
| s2 | 1 | 1 | 561 | 1498 | NO |
| s2 | 1 | 2 | 561 | 1498 | NO |
| s2 | 2 | 1 | 531 | 1480 | NO |
| s2 | 2 | 2 | 531 | 1480 | NO |
| s4 | 0 | 1 | 161 | 1346 | NO |
| s4 | 0 | 2 | 1024 | 1486 | NO |
| s4 | 0 | 3 | 163 | 1491 | NO |
| s4 | 1 | 1 | 162 | 1392 | NO |
| s4 | 1 | 2 | 1024 | 1461 | NO |
| s4 | 1 | 3 | 164 | 1398 | NO |
| s4 | 2 | 1 | 160 | 1493 | NO |
| s4 | 2 | 2 | 1024 | 1494 | NO |
| s4 | 2 | 3 | 162 | 1468 | NO |

## S7 delay (p99 ms, worst AP; load 1.0 Mbps per STA)

| s7-s4 method | worst-AP p99 ms (mean over seeds) | seeds |
|---|---|---|
| 128-128-128 | 517.8 | 3 |
| 128-64-128 | 519.7 | 3 |
| 16-16-16 | 557.9 | 3 |
| 256-128-256 | 520.3 | 3 |
| 256-256-256 | 524.9 | 3 |
| 256-64-256 | 516.5 | 3 |
| 32-32-32 | 527.0 | 3 |
| 64-64-64 | 507.3 | 3 |
| beb | 573.9 | 3 |

| s7-s2 method | worst-AP p99 ms (mean over seeds) | seeds |
|---|---|---|
| 128-128 | 20.4 | 3 |
| 16-16 | 17.2 | 3 |
| 256-256 | 19.5 | 3 |
| 32-32 | 638.8 | 3 |
| 512-512 | 21.9 | 3 |
| 64-64 | 25.7 | 3 |
| beb | 27.3 | 3 |
