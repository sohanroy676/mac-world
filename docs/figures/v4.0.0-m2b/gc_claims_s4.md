## GC table: 10,10,10 hidden 1-3, load 10, seeds 103-109

### alpha = 0

BEB per-AP Mbps [35.49, 1.31, 35.6]; floors [24.14, 1.31, 24.14]; oracle = static:64,64,64; U gap 3.791 (BEB SD 0.952)

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 7 | 72.41 | 1.31 | 72.408 | 0.000 ± 0.000 | ok |
| dac | 7 | 77.99 | 1.73 | 77.993 | 1.473 ± 0.165 | ok |
| drlv2t1 | 7 | 76.28 | 2.35 | 76.283 | 1.022 ± 0.048 | ok |
| idlesense | 7 | 73.09 | 1.11 | 73.090 | 0.180 ± 0.173 | **infeasible** |
| ms | 7 | 76.25 | 2.68 | 76.248 | 1.013 ± 0.270 | ok |
| static:128,64,128 | 7 | 68.30 | 8.29 | 68.305 | -1.082 ± 0.244 | ok |
| static:64,64,64 | 7 | 76.20 | 2.68 | 76.200 | 1.000 ± 0.207 | ok |
| ucbctx | 7 | 59.47 | 7.67 | 59.470 | -3.413 ± 0.298 | ok |

### alpha = 1

BEB per-AP Mbps [35.49, 1.31, 35.6]; floors [24.14, 1.31, 24.14]; oracle = static:128,64,128; U gap 16.106 (BEB SD 5.628); **degenerate cell, raw U only**

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 7 | 72.41 | 1.31 | 3.994 | n/a | ok |
| dac | 7 | 77.99 | 1.73 | 9.046 | n/a | ok |
| drlv2t1 | 7 | 76.28 | 2.35 | 10.801 | n/a | ok |
| idlesense | 7 | 73.09 | 1.11 | 2.601 | n/a | **infeasible** |
| ms | 7 | 76.25 | 2.68 | 12.852 | n/a | ok |
| static:128,64,128 | 7 | 68.30 | 8.29 | 20.100 | n/a | ok |
| static:64,64,64 | 7 | 76.20 | 2.68 | 12.860 | n/a | ok |
| ucbctx | 7 | 59.47 | 7.67 | 16.154 | n/a | ok |

### alpha = 4

BEB per-AP Mbps [35.49, 1.31, 35.6]; floors [24.14, 1.31, 24.14]; oracle = static:128,64,128; U gap 17616.924 (BEB SD 43842.249); **degenerate cell, raw U only**

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 7 | 72.41 | 1.31 | -17623.027 | n/a | ok |
| dac | 7 | 77.99 | 1.73 | -863.701 | n/a | ok |
| drlv2t1 | 7 | 76.28 | 2.35 | -1676.396 | n/a | ok |
| idlesense | 7 | 73.09 | 1.11 | -25555.762 | n/a | **infeasible** |
| ms | 7 | 76.25 | 2.68 | -177.942 | n/a | ok |
| static:128,64,128 | 7 | 68.30 | 8.29 | -6.103 | n/a | ok |
| static:64,64,64 | 7 | 76.20 | 2.68 | -174.935 | n/a | ok |
| ucbctx | 7 | 59.47 | 7.67 | -10.472 | n/a | ok |

