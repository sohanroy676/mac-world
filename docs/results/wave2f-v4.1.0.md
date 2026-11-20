# Wave 2f: S8 with the change detector (2026-11-20)

S8 = S4 with a load shift at 30 s: AP1's first 5 STAs are on 0-30 s only, AP3's first 5 STAs on 30-60 s only (`--staSchedule 0:0-4:0:30/2:0-4:30:60`, cell `s8` in cells.json).
32 runs (seeds 0-3, 60 s, whole-run `thr_all`), 0 missing, 0 hash mismatches. Floors are the S4 floors (24.44, 1.31, 24.44), not validated for S8. No S8 ceiling yet, so only absolute utility is compared.

| setting | U at its alpha (alpha 0) | U (alpha 1) | mean Mbps AP1/AP2/AP3 |
|---|---|---|---|
| BEB | 73.57 | 7.40 | 35.6 / 1.6 / 36.4 |
| static 64,64,64 | 71.56 | 16.56 | 33.1 / 4.7 / 33.8 |
| kwdirect alpha 1, no detector | | 18.88 | 26.0 / 8.9 / 28.7 |
| kwdirect alpha 1, detector | | 15.37 | 33.8 / 4.0 / 34.7 |
| coord alpha 1, no detector | | 20.08 | 25.8 / 11.5 / 25.2 |
| coord alpha 1, detector | | 11.59 | 36.5 / 2.4 / 37.0 |
| kwdirect alpha 0, no detector | 72.87 | | 35.1 / 2.3 / 35.5 |
| kwdirect alpha 0, detector | 72.39 | | 33.8 / 4.1 / 34.5 |
| coord (alpha 1 setting) scored at alpha 0, detector | 75.92 | | 36.5 / 2.4 / 37.0 |

Findings:
- Alpha 1: coord without the detector is best (20.08), above static 64 (16.56) and BEB (7.40). All online settings beat BEB.
- The detector hurts at alpha 1 (coord 20.08 to 11.59, kwdirect 18.88 to 15.37): it restarts L2 and loses the learned level. Page-Hinkley settings (delta 0.05, lambda 3) are probably too sensitive, or the restart is too costly.
- Alpha 0: nothing clearly beats BEB (73.57); coord with detector reaches 75.92 but it was tuned for alpha 1.
- Not done: an S8 ceiling (per-phase best static plus schedule) to turn these into shares; detector retune (larger lambda, softer restart instead of full restart).
