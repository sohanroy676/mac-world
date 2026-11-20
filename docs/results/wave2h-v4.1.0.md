# Wave 2h: S4 alpha 0 recheck on validation seeds 200-209 (2026-11-20)

30 runs planned, 29 collected (0 hash mismatches), image sha256:7808da54 (commit b8e448d1), 60 s, utility at alpha 0 on thr_half2.
One run failed its check: `w2h-s4-kwdirect-a0-s206` (exit 1 after the full 585 s, `check: FAIL`); reproduced locally (see below).

| method | n | U (alpha 0) | sd | mean Mbps AP1/AP2/AP3 | feasible (floors 24.44, 1.31, 24.44, tol 0.05) |
|---|---|---|---|---|---|
| BEB | 10 | 73.305 | 0.85 | 36.0 / 1.31 / 36.0 | yes (matches the validated 73.31) |
| DAC (Tc 514 us) | 10 | 78.351 | 0.42 | 38.6 / 1.15 / 38.6 | NO (AP2 1.15 < 1.245) |
| kwdirect alpha 0 (tau 1.0, delta 0.2) | 9 | 77.679 | 0.40 | 38.0 / 1.80 / 37.9 | yes |

Findings:
- The validated static ceiling for S4 alpha 0 (77.28) is exceeded by a feasible online controller: kwdirect 77.68 (share 1.09 of the BEB-to-ceiling gap on these seeds). The static F1/F3 ceiling is therefore not an upper bound for online controllers, only the reference.
- The 0.94 worst-cell share in Wave 2e used seeds 0-3 (77.06). On seeds 200-209 the same setting scores 77.68, so that gap is mostly a seed-set effect, not a controller weakness.
- DAC reaches 78.35 but violates the AP2 floor (1.15 Mbps), so it does not count as feasible. This also means the Wave 2g DAC S4 alpha 0 share of 1.25 is not a valid win.
- The worst-cell figure must be recomputed on the tournament seeds (300-309), not on tuning seeds 0-3.
