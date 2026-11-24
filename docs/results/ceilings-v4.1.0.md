# Wave 1 ceilings (v4.1.0, Track A) — measured 2026-11-17/18

Labels: **fact** = computed from the runs named here; **decision** = our choice; **inference** = not checked.

## What was run
- **Search (fact):** 4,723 runs, all `--check` PASS, no trace-hash mismatch across machines: round 0 (Halton points plus anchors, 30 s, seeds 0-3) on the six forks,
  round 1 (Gaussian-process proposals) on five forks, round 2 parts 1 and 2 (1,011 of 1,508 runs) on this repository. Round 2 part 3 was skipped (decision).
  GitHub disabled Actions on the forks before round 2 could start there; see `docs/reference/wave-runbook-v4.1.0.md` section 6.
- **Validation (fact):** per cell and family the top 3 points per alpha on fresh seeds 200-209, 60 s runs scored on seconds 30-60, 480 runs, plus BEB on the same seeds.
- **Ceiling (definition):** best floor-feasible validated point over the families F1 exact static, F2 static CWmin, F3 schedule (S4 only); floors from the BEB means on the same
  seeds, tolerance 0.05; utility = station-weighted alpha-fair (`gc_analysis.utility`). Script: `ns-3.29/scratch/linear-mesh/ceilings_v4_1_0.py`.
- **Bound (fact for the model, inference for the real network):** `bounds_v4_1_0.py`, scheduled-access capacity 51.82 Mbps per BSS from the measured frame times,
  assumptions in the module docstring (no capture, no exchange shorter than the measured one).

## Results (utility, higher is better; point = CW per AP)
| cell | alpha | BEB | best F1 | best F2 | best F3 | ceiling | (ceiling - BEB) / (F1 - BEB) | bound | (ceiling - BEB) / (bound - BEB) |
|---|---|---|---|---|---|---|---|---|---|
| s2 | 0 | 27.90 | 39.72 (289/525) | 39.59 (255/511) | - | f1 39.72 | 1.00 | 51.82 | 0.49 |
| s2 | 1 | -46.49 | -24.83 (512/512) | -25.23 (255/255) | - | f1 -24.83 | 1.00 | -8.79 | 0.57 |
| s2 | 4 | -218.41 | -69.27 (512/512) | -70.69 (255/255) | - | f1 -69.27 | 1.00 | -31.04 | 0.80 |
| s4 | 0 | 73.31 | 76.77 (54/84/95) | 76.98 (63/63/63) | 77.28 (96/299/38) | f3 77.28 | 1.15 | 102.40 | 0.14 |
| s4 | 1 | 4.65 | 20.05 (128/64/128) | 19.59 (127/15/63) | 21.39 (33/35/49) | f3 21.39 | 1.09 | 30.26 | 0.65 |
| s4 | 4 | -8995.95 | -2.05 (254/104/200) | -2.76 (127/7/63) | -1.54 (33/35/49) | f3 -1.54 | 1.00 | -0.55 | 1.00 |
| s5a | 0 | 45.09 | 49.98 (110/161/94) | - | - | f1 49.98 | 1.00 | 61.82 | 0.29 |
| s5a | 1 | 9.86 | 13.28 (128/128/128) | - | - | f1 13.28 | 1.00 | 19.04 | 0.37 |
| s5a | 4 | -5.93 | -4.24 (227/133/279) | - | - | f1 -4.24 | 1.00 | -3.72 | 0.76 |
| s8p3 | 0 | 77.42 | 77.58 (32/64/32) | - | - | f1 77.58 | 1.00 | 101.84 | 0.01 |
| s8p3 | 1 | 9.04 | 20.56 (94/72/72) | - | - | f1 20.56 | 1.00 | 30.26 | 0.54 |
| s8p3 | 4 | -2897.84 | -2.77 (96/68/69) | - | - | f1 -2.77 | 1.00 | -0.55 | 1.00 |

Gate S (S4, schedule vs best static family, feasible points only): alpha | F3 - static | seed SD of static | 0.05 of BEB-to-F1 gap | pass
- alpha 0: +0.297 | 0.160 | 0.173 | no
- alpha 1: +1.340 | 0.073 | 0.770 | PASS
- alpha 4: +0.507 | 0.022 | 449.695 | no


## Reading the table
- Every cell has a large validated gap above BEB at alpha 1 and 4 (S2: -46.5 to -24.8 at alpha 1; S4: 4.7 to 21.4; S8 phase 3: 9.0 to 20.6). At alpha 0 (total throughput) the gain is small on S4 (+5 %) and almost nil on S8 phase 3 (77.4 to 77.6).
- **Gate S (S4):** the schedule beats the best static family at alpha 1 by +1.34 utility, 18 seed SDs and more than 0.05 of the BEB-to-F1 gap: **PASS** at alpha 1.
  At alpha 0 it does not (+0.30 against 3 SDs = 0.48). At alpha 4 the gap rule is not usable (BEB's utility is -8,996 because one AP is starved), so the SD rule alone gives +0.51 = 23 SDs; treat as not decided.
  Inference: a CW-only schedule helps the middle AP of the hidden chain at alpha 1; this is not yet shown to hold at 102.4 ms update granularity (Gate C).
- The ratio to the bound (last column) is 0.14 to 1.00. A low ratio at alpha 0 means the scheduled-access bound is loose there (it ignores collisions and backoff idle time), not that 86 % is available.
- S8 phase 3 has a time-varying load; the static ceiling is a reference for a fixed CW only (it is not the S8 ceiling an adaptive controller faces).

## Caveats
- The search used 4 seeds and 30 s runs; the top 3 per cell, family and alpha were re-run on fresh seeds, so a weak search can only make a ceiling too low. Round 2 was cut by a third and F2 is a grid, so the ceilings are lower bounds of the true optimum.
- Learned runs are not covered (a learner run hashed differently on Intel and AMD CPUs in Wave 0).
- Results are in branch `wave-collected` of the repository (`w1/summaries.jsonl`, `w1v/summaries.jsonl`).
