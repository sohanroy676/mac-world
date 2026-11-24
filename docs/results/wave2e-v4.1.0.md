# Wave 2e (2026-11-20)

68 runs (seeds 0-3, 60 s, wide CW range), 0 missing, 0 hash mismatches. Share = (U - BEB) / (ceiling - BEB), all feasible.

| cell | alpha | best online | share | setting |
|---|---|---|---|---|
| S2 | 0 | kwdirect | 0.97 | delta 0.2, tau 1.0 |
| S2 | 1 | kwdirect | 0.97 | delta 0.2, tau 0.6 |
| S2 | 4 | kwdirect | 0.97 | delta 0.2, tau 0.6 |
| S4 | 0 | kwdirect | 0.94 | delta 0.2, tau 1.0 (Wave 2d, tau 0.6: 0.94) |
| S4 | 1 | coord + floor guard | 0.97 | delta 0.5, beta 1.5, tau 0.6 |
| S4 | 4 | kwdirect | 1.00 | delta 0.2, tau 0.6 |
| S5a | 0 | kwdirect | 0.95 | tau 0.6 (Wave 2d; tau 1.0 here: 0.93) |
| S5a | 1 | kwdirect | 1.03 | delta 0.2, tau 0.6 |
| S5a | 4 | kwdirect | 0.97 | delta 0.2, tau 0.6 |

- Worst cell: S4 at alpha 0, 0.94 (target 0.95, not yet met; within seed noise on 4 seeds).
- Probe window 0.6 s with delta 0.2 fixes S2 at alpha 1 and 4 (0.93 to 0.97).
- Coord on S4 alpha 1 improves with delta 0.5 (0.97); kwdirect there stays at 0.90.
- Open: S7 delay objective, S8 with change detector, rivals/BLADE, class B learners.
