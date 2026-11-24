# Wave 2 tuning, first grid (2026-11-18)

108 runs (cascade S2 and S4, coord S4; L2 step eta in 0.1/0.25/0.5 x probe delta 0.2/0.35/0.7; seeds 0-3; 60 s, scored on seconds 30-60), all PASS, own Actions account, image 0b8c89b1. Script `rank_w2_tuning_v4_1_0.py`. Reference BEB and F1 are the validated numbers on seeds 200-209 (different seeds, same window), so gaps are indicative; alpha 1.

| cell | BEB | best F1 | best F3 | cascade best | coord best |
|---|---|---|---|---|---|
| S2 | -46.49 | -24.83 (512/512) | - | -30.23 (eta 0.25, delta 0.7; 75% of the BEB-to-F1 gap) | - |
| S4 | 4.65 | 20.05 (128/64/128) | 21.39 | 10.06 (eta 0.25, delta 0.7; 35%) | 20.00 +-0.10 (eta 0.1, delta 0.35) |

- Coord on S4 reaches 93-100% of the F1 ceiling in every cell of the grid, but is NOT floor-feasible: outer APs get about 21 Mbps against a floor of 24.4. It does not reach the F3 schedule (21.39).
- Cascade on S4 starves the middle AP (1-9 Mbps), the same weak spot as BEB; larger delta (0.7) helps; spread across seeds is large (SD 2-8).
- Cascade on S2 is insensitive to eta and delta (all within about 0.5 of each other, SD 3-8): the grid does not separate them.
- Next: floor guard in L2/L3 (hold outer APs above the floor), then a finer grid and the F3-style duty cycle for coord.
