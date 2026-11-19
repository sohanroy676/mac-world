# Wave 2b: floor-guarded controllers (2026-11-19)

105 runs (BEB references and floor-guarded controllers on S2, S4, S5a), all PASS, no hash mismatch, own Actions account, image acf9d0ac. 60 s runs, seeds 0-3, scored on seconds 30-60, alpha 1. Script `rank_w2b_v4_1_0.py`. Floors are the BEB means of the validation seeds (ceilings-v4.1.0.md), feasibility at tolerance 0.05. Ceilings (F1, F3) are the validated values on seeds 200-209; the controllers run on seeds 0-3, so shares are indicative.

| cell | BEB (seeds 0-3) | best static F1 | schedule F3 | best controller (settings) | feasible | share of BEB-to-ceiling gap |
|---|---|---|---|---|---|---|
| S2 | -46.66 | -24.83 | - | kwdirect -26.77 (delta 0.35) | yes | 0.91 |
| S4 | 6.05 | 20.05 | 21.39 | coord +floor guard 20.50 (delta 0.35, beta 1.5) | yes | 0.94 |
| S5a | 9.65 | 13.28 | - | kwdirect 13.25 (delta 0.35) | yes | 0.99 |

- The floor guard fixes the failure of grid 1: coord on S4 was 20.0 but infeasible (outer APs 21 vs floor 24.4); with the guard it is 20.5 and feasible (outer 25.0-25.9, middle 10-12 Mbps). It beats the best static F1 (20.05) and is within 0.9 of the schedule ceiling F3 (21.39).
- cascade (L1+L2) still starves the middle AP on S4 (3-9 Mbps) and has a large seed spread; `kwdirect` is the best online controller without L3 (S2 -26.8, S4 19.7 with SD 0.4, S5a 13.25 with SD 0.08).
- Small delta (0.35) is better for coord and kwdirect; beta 0.5 vs 1.5 makes no clear difference (within seed SD).
- Remaining shortfall: S4 coord vs F3 (about 0.9 of 21.39 minus BEB), S2 kwdirect vs F1 (about 2 utility points). S7a, S7b, S8p3 only have BEB references so far.
- Next: S7 (delay objective), S8 (load schedule), alpha 0 and 4, a finer kwdirect/coord grid around delta 0.35, and larger graphs for qcsma vs coord.
