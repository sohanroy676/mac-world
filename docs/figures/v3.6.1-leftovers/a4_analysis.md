# M1 selection-seed analysis (python seeds 0-2)

## s8p3 (10,10,10, hidden 1-3, loads , load 10.0)

alpha 0: oracle `static:32,64,32`, U gap over BEB 1.090 (BEB U SD 0.278), degenerate: False, floors ['25.49', '2.13', '25.49']

| method | n | agg | min AP | feasible | U | GC |
|---|---|---|---|---|---|---|
| beb | 3 | 76.46 | 2.13 | True | 76.46 | 0.00 ± 0.00 |
| static:32,128,32 | 3 | 80.20 | 1.15 | False | 80.20 | 3.43 ± 0.55 |
| static:32,64,32 | 3 | 77.55 | 2.73 | True | 77.55 | 1.00 ± 0.47 |
| static:16,128,16 | 3 | 75.73 | 0.50 | False | 75.73 | -0.67 ± 1.70 |
| static:64,256,64 | 3 | 75.52 | 2.82 | True | 75.52 | -0.86 ± 0.76 |
| static:32,32,32 | 3 | 73.80 | 4.02 | True | 73.80 | -2.43 ± 0.80 |
| static:64,128,64 | 3 | 73.33 | 5.03 | True | 73.33 | -2.87 ± 0.58 |

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
| static:32,64,32 | 37.36, 2.73, 37.45 | 3.34 (0.01), 1.02 (0.02), 3.32 (0.01) | 0.225, 0.363, 0.222 |
| static:64,32,64 | 24.71, 11.61, 24.77 | 4.53 (0.02), 2.00 (0.03), 4.52 (0.04) | 0.182, 0.500, 0.180 |
| static:64,64,64 | 30.40, 8.10, 30.46 | 5.05 (0.02), 1.80 (0.00), 5.04 (0.02) | 0.145, 0.368, 0.142 |

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

## S7 delay (p99 ms, worst AP; s7-s4b 1.93,1.0,1.93 per STA)

| s7-s4b method | worst-AP p99 ms (mean over seeds) | delivered >= 99 % | seeds |
|---|---|---|---|
| 128-64-128 | 9.3 | yes | 3 |
| 64-64-64 | 9.3 | yes | 3 |
| 32-32-32 | 9.6 | yes | 3 |
| 256-64-256 | 9.7 | yes | 3 |
| 128-128-128 | 10.5 | yes | 3 |
| 256-128-256 | 10.6 | yes | 3 |
| beb | 10.7 | yes | 3 |
| 256-256-256 | 17.6 | yes | 3 |
| 16-16-16 | 529.3 | NO | 3 |

Oracle (lowest p99, delivered >= 99 %): **128-64-128** p99 9.3 ms vs BEB 10.7 ms (ln gap 0.141)
