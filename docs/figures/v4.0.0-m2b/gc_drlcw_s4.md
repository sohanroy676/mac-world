## GC table: 10,10,10 hidden 1-3, load 10, seeds 100-102

### alpha = 0

BEB per-AP Mbps [35.76, 1.4, 35.57]; floors [24.24, 1.4, 24.24]; oracle = static:64,64,64; U gap 3.381 (BEB SD 0.370)

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 3 | 72.73 | 1.40 | 72.729 | 0.000 ± 0.000 | ok |
| drlv2t0 | 3 | 79.59 | 0.58 | 79.593 | 2.030 ± 0.351 | **infeasible** |
| drlv2t1 | 3 | 76.36 | 2.27 | 76.364 | 1.075 ± 0.472 | ok |
| drlv2t2 | 3 | 78.64 | 1.28 | 78.636 | 1.747 ± 0.231 | **infeasible** |
| idlesense | 3 | 73.06 | 1.19 | 73.061 | 0.098 ± 0.151 | **infeasible** |
| static:128,64,128 | 3 | 68.29 | 8.26 | 68.294 | -1.312 ± 0.292 | ok |
| static:64,64,64 | 3 | 76.11 | 2.73 | 76.110 | 1.000 ± 0.317 | ok |

### alpha = 1

BEB per-AP Mbps [35.76, 1.4, 35.57]; floors [24.24, 1.4, 24.24]; oracle = static:128,64,128; U gap 14.355 (BEB SD 1.191)

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 3 | 72.73 | 1.40 | 5.718 | 0.000 ± 0.000 | ok |
| drlv2t0 | 3 | 79.59 | 0.58 | -1.784 | -0.523 ± 0.704 | **infeasible** |
| drlv2t1 | 3 | 76.36 | 2.27 | 11.022 | 0.369 ± 0.276 | ok |
| drlv2t2 | 3 | 78.64 | 1.28 | 6.200 | 0.034 ± 0.314 | **infeasible** |
| idlesense | 3 | 73.06 | 1.19 | 4.167 | -0.108 ± 0.134 | **infeasible** |
| static:128,64,128 | 3 | 68.29 | 8.26 | 20.074 | 1.000 ± 0.211 | ok |
| static:64,64,64 | 3 | 76.11 | 2.73 | 13.007 | 0.508 ± 0.232 | ok |

### alpha = 4

BEB per-AP Mbps [35.76, 1.4, 35.57]; floors [24.24, 1.4, 24.24]; oracle = static:128,64,128; U gap 1299.052 (BEB SD 561.603); **degenerate cell, raw U only**

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 3 | 72.73 | 1.40 | -1305.209 | n/a | ok |
| drlv2t0 | 3 | 79.59 | 0.58 | -34500.185 | n/a | **infeasible** |
| drlv2t1 | 3 | 76.36 | 2.27 | -429.496 | n/a | ok |
| drlv2t2 | 3 | 78.64 | 1.28 | -2400.817 | n/a | **infeasible** |
| idlesense | 3 | 73.06 | 1.19 | -2356.117 | n/a | **infeasible** |
| static:128,64,128 | 3 | 68.29 | 8.26 | -6.157 | n/a | ok |
| static:64,64,64 | 3 | 76.11 | 2.73 | -164.630 | n/a | ok |

