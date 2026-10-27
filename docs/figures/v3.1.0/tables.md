# v3.1.0 static CW sweep tables

Policy window = steps >= 300 (3 s of 15 s); mean ± 95% CI (Student t) over seeds; Mbps. Paired = same ns-3 seed.

## 20,40

- beb reference (n=3): 27.30 ± 0.63
- global reference (n=3): 36.17 ± 6.95

| CW per AP | n | aggregate | per-AP | Jain | phy loss | vs BEB (paired) | vs Global (paired) |
|---|---|---|---|---|---|---|---|
| 32,32 | 1 | 12.80 (n=1) | 3.99 / 8.81 | 0.88 | 0.912 | -14.44 (n=1) | -22.27 (n=1) |
| 64,64 | 1 | 19.66 (n=1) | 7.03 / 12.63 | 0.92 | 0.839 | -7.59 (n=1) | -15.41 (n=1) |
| 128,128 | 1 | 30.25 (n=1) | 10.01 / 20.24 | 0.90 | 0.710 | 3.00 (n=1) | -4.82 (n=1) |
| 256,256 | 1 | 37.75 (n=1) | 12.56 / 25.18 | 0.90 | 0.610 | 10.50 (n=1) | 2.68 (n=1) |

Best by mean aggregate: cw=256,256 (37.75 (n=1)).
