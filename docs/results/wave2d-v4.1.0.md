# Wave 2d: alpha-aware L3 and a longer probe window (2026-11-19/20)

56 runs, all PASS, no hash mismatch, own Actions account (7 packs, about 1 h 40 min), image 171d4f1a. Seeds 0-3, 60 s, seconds 30-60. Share = (U - BEB) / (ceiling - BEB) with the validated BEB and ceilings (seeds 200-209), floor-feasible only. Script `rank_w2c_v4_1_0.py`.

| cell, alpha | coord (weights (x/n)^-alpha) | kwdirect, probe window 0.6 s (eta 0.25, delta 0.2) | best before (Wave 2c) |
|---|---|---|---|
| S2, 0 | - | 0.97 | 0.92 |
| S4, 0 | -0.59 (beta 0.5), -1.57 (beta 1.5) | 0.94 | 0.76 |
| S5a, 0 | 0.60 | 0.95 | 0.88 |
| S4, 4 | 1.00 | - | 1.00 |
| S5a, 4 | 0.69 | - | 0.95 (kwdirect) |

- A 0.6 s probe window (instead of 0.3 s) fixes the alpha 0 cells: kwdirect now reaches 0.94-0.97 in all three. Delta 0.2 is better than 0.35 there.
- The alpha-aware weights do not rescue coord at alpha 0 (it stays below BEB on S4: muting costs throughput when the objective is throughput). Decision: L3 is off at alpha 0 and where kwdirect is better; coord stays only for S4 alpha 1 and 4.
- Alpha 1 and 4 are unchanged by the weights (alpha 1 weights are the same as before).
- Worst cell now: S2 at alpha 1 and 4 (0.93), S4 alpha 0 (0.94). Next: the longer window at alpha 1 and 4, window 1.0 s at alpha 0, coord with a longer window on S4 alpha 1.
