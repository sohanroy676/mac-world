## GC table: 10,10,10 hidden 1-3 loads 150,150,1, load 150, seeds 100-102

### alpha = 0

BEB per-AP Mbps [24.0, 11.26, 10.0]; floors [15.09, 11.26, 10.0]; oracle = static:128,128,128; U gap 4.512 (BEB SD 0.050)

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 3 | 45.26 | 10.00 | 45.262 | 0.000 ± 0.000 | ok |
| drlv2t0 | 3 | 49.81 | 4.62 | 49.813 | 1.009 ± 0.007 | **infeasible** |
| drlv2t1 | 3 | 49.83 | 6.30 | 49.833 | 1.013 ± 0.037 | **infeasible** |
| drlv2t2 | 3 | 49.96 | 3.63 | 49.958 | 1.041 ± 0.014 | **infeasible** |
| idlesense | 3 | 47.37 | 9.45 | 47.371 | 0.467 ± 0.027 | **infeasible** |
| static:128,128,128 | 3 | 49.77 | 10.00 | 49.774 | 1.000 ± 0.013 | ok |

### alpha = 1

BEB per-AP Mbps [24.0, 11.26, 10.0]; floors [15.09, 11.26, 10.0]; oracle = static:128,128,128; U gap 3.304 (BEB SD 0.033)

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 3 | 45.26 | 10.00 | 9.942 | 0.000 ± 0.000 | ok |
| drlv2t0 | 3 | 49.81 | 4.62 | 4.864 | -1.537 ± 0.024 | **infeasible** |
| drlv2t1 | 3 | 49.83 | 6.30 | 7.484 | -0.744 ± 0.021 | **infeasible** |
| drlv2t2 | 3 | 49.96 | 3.63 | 2.758 | -2.175 ± 0.023 | **infeasible** |
| idlesense | 3 | 47.37 | 9.45 | 9.701 | -0.073 ± 0.034 | **infeasible** |
| static:128,128,128 | 3 | 49.77 | 10.00 | 13.246 | 1.000 ± 0.044 | ok |

### alpha = 4

BEB per-AP Mbps [24.0, 11.26, 10.0]; floors [15.09, 11.26, 10.0]; oracle = static:128,128,128; U gap 1.445 (BEB SD 0.066)

| Method | n | Aggregate | min-AP | U | GC (mean ± 95 % CI) | Floor |
|---|---|---|---|---|---|---|
| beb | 3 | 45.26 | 10.00 | -5.910 | 0.000 ± 0.000 | ok |
| drlv2t0 | 3 | 49.81 | 4.62 | -37.168 | -21.636 ± 0.572 | **infeasible** |
| drlv2t1 | 3 | 49.83 | 6.30 | -16.726 | -7.486 ± 0.262 | **infeasible** |
| drlv2t2 | 3 | 49.96 | 3.63 | -73.287 | -46.638 ± 1.075 | **infeasible** |
| idlesense | 3 | 47.37 | 9.45 | -7.438 | -1.057 ± 0.129 | **infeasible** |
| static:128,128,128 | 3 | 49.77 | 10.00 | -4.466 | 1.000 ± 0.118 | ok |

