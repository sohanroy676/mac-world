# Wave 2c: finer grid and alpha 0 / 4 (2026-11-19)

220 runs, all PASS, no hash mismatch, own Actions account (19 packs parallel, about 1 h 50 min), image acf9d0ac. S2, S4, S5a; seeds 0-3; 60 s, seconds 30-60. Script `rank_w2c_v4_1_0.py` (also reads the Wave 2b file). Share = (U - BEB) / (ceiling - BEB) with the validated BEB and ceilings of ceilings-v4.1.0.md (seeds 200-209; the controllers run seeds 0-3, so shares are indicative; a share above 1 means above the lower-bound ceiling). Only floor-feasible settings count (tolerance 0.05, floors from the validation BEB).

Best feasible share per cell and alpha (mode, eta / delta / beta):

| cell | alpha 0 | alpha 1 | alpha 4 |
|---|---|---|---|
| S2 | 0.92 kwdirect (0.25 / 0.35) | 0.93 kwdirect (0.15 / 0.35) | 0.93 kwdirect (0.25 / 0.35) |
| S4 | 0.76 kwdirect (0.25 / 0.35); coord is below BEB | 0.96 coord (0.15 / 0.5 / 1.5); kwdirect 0.92 | 1.00 coord and kwdirect |
| S5a | 0.88 kwdirect (0.25 / 0.35); coord 0.46 | 1.04 kwdirect (0.4 / 0.2); coord 0.69 | 0.95 kwdirect; coord 0.68 |

- Worst cell is S4 at alpha 0 (0.76, kwdirect): at alpha 0 the objective is plain throughput and the whole BEB-to-ceiling gap is only about 4 Mbps; coord's muting costs throughput there, so L3 should be switched off (or its weights set to alpha) at alpha 0. Next worst: S5a alpha 0 (0.88) and S2 alpha 0 (0.92).
- kwdirect is the best online controller without L3 in every cell (0.88-1.04 except S4 alpha 0), and needs no neighbour or hearing-graph information beyond the network goodput that L2 already uses.
- coord only wins where the schedule helps (S4 alpha 1 and 4) and loses elsewhere; coord with beta 1.5 and small delta (0.2-0.5) is within seed noise of beta 0.5.
- The primary target (worst-cell share 0.95) is not reached yet: S4 alpha 0 (0.76), S5a alpha 0 (0.88), S2 (0.92-0.93).
- Next: alpha-aware L3 (mute only when the alpha-fair utility gains), a longer probe window for alpha 0, S7 delay cells, S8 schedule with the change detector, then the rivals and learners.
