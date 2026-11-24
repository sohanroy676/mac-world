# Wave 2i / 2i2 (v4.1.0): S7 delay cells

- Date: 2026-11-20. Image sha256:4149e56b..., 60 s runs, seeds 0-3, 48 runs (2i: 32, 2i2: 16 BEB/static reruns with `--extraTraces --delayWindow 0.3`), about 19 lab-h.
- Cells: s7a (20,40 STAs, load 0.37), s7b (10,10,10, hidden 1-3, loads 1.93/1.0/1.93).
- Controller: kwdirect, delay objective -ln(worst-AP mean p95), floor 0.99 x offered load, wide CW range, tau 0.6 or 1.0.
- Note: 2i BEB/static had no delay traces (fact), so they were rerun in 2i2 with the same seeds.

## Results (mean over 4 seeds; p99 delay in ms per AP; worst = max over APs)

| cell | method | p99 per AP | worst p99 | mean delay | throughput (Mbps) |
|---|---|---|---|---|---|
| s7a | BEB | 27.2, 27.2 | 27.2 | 15.0, 15.1 | 7.40, 14.80 |
| s7a | static CW 256 | 19.4, 19.5 | **19.5** | 9.2, 9.3 | 7.40, 14.80 |
| s7a | kwdelay tau 0.6 | 22.5, 21.9 | 22.5 | 10.3, 10.1 | 7.40, 14.79 |
| s7a | kwdelay tau 1.0 | 23.5, 23.1 | 23.5 | 10.3, 10.6 | 7.39, 14.78 |
| s7b | BEB | 8.2, 10.6, 8.3 | 10.6 | 2.1, 3.6, 2.1 | 19.3, 10.0, 19.3 |
| s7b | static 128,64,128 | 6.2, 9.4, 6.2 | 9.4 | 2.3, 3.2, 2.3 | 19.3, 10.0, 19.3 |
| s7b | kwdelay tau 0.6 | 5.0, 9.3, 5.0 | **9.3** | 1.9, 3.4, 1.9 | 19.3, 10.0, 19.3 |
| s7b | kwdelay tau 1.0 | 4.8, 9.4, 4.8 | 9.4 | 1.9, 3.4, 1.9 | 19.3, 10.0, 19.3 |

## Reading
- Delivered load is >= 99 % of offered for every method (fact), so the delay comparison is valid.
- s7a: kwdelay cuts worst p99 by 17 % vs BEB (tau 0.6) but stays 15 % above the static anchor (22.5 vs 19.5). It does not reach the static anchor.
- s7b: kwdelay 9.3 vs static 9.4 vs BEB 10.6 (-12 %); ties the static anchor on the worst AP and beats it on APs 1 and 3 (5.0 vs 6.2).
- The earlier worry that s7a had too few delay samples was a 5 s local run; real runs have 38k-76k samples per AP (fact).
- Tau 0.6 is at least as good as 1.0 in both cells (inference from 4 seeds, no test run).
- Share of BEB-to-anchor gap closed (worst p99): s7a (27.2-22.5)/(27.2-19.5) = 0.61; s7b (10.6-9.3)/(10.6-9.4) = 1.08.

## Open
- s7a gap to static: next try a slower tau or a larger eta (not run). The delay objective at p95 may hide the tail; p99 objective not tried.
- No paired test yet (analysis code pending).
