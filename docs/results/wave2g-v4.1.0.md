# Wave 2g: rival sanity and detector retune (2026-11-20)

92 runs (seeds 0-3, 60 s, image sha256:7808da54, commit b8e448d1), 0 missing, 0 hash mismatches, all PASS.
BLADE was merged from feature/v3.8.0-m2b (4f6572b) first; `--lyDetectLam` / `--lyDetectDelta` added.

## Rivals (default or earlier-tuned settings, not retuned per alpha; thr_half2; share of the validated BEB-to-ceiling gap)

| cell | rival | alpha 0 | alpha 1 | alpha 4 | feasible |
|---|---|---|---|---|---|
| S2 | DAC (Tc 514 us) | 0.97 | 0.97 | 0.97 | yes |
| S2 | IdleSense | 0.90 | 0.92 | 0.95 | yes |
| S2 | BLADE | 0.77 | 0.80 | 0.88 | yes |
| S2 | KW (original) | 0.41 | 0.45 | 0.55 | yes |
| S2 | contextual UCB | -0.28 | -0.41 | -1.15 | no |
| S4 | KW | -3.74 | 0.84 | 1.00 | no |
| S4 | contextual UCB | -3.98 | 0.63 | 1.00 | yes |
| S4 | DAC | 1.25 | 0.10 | 0.82 | yes |
| S4 | BLADE | -0.62 | 0.05 | 0.85 | yes |
| S4 | IdleSense | -0.08 | -0.02 | 0.76 | no |
| S5a | KW | 0.76 | 0.98 | 0.98 | yes |
| S5a | DAC | 0.98 | 0.10 | -1.30 | no |
| S5a | others | below 0.5 or infeasible | | | |

Reading:
- All five rivals run and pass the checks; BLADE is functional.
- DAC with Tc 514 us ties our best online controller on S2 (0.97 at all alphas): a strong rival there, so S2 is where our margin is thinnest.
- DAC at alpha 0 on S4 (1.25) beats the S4 alpha 0 ceiling share used so far (0.94); the alpha 0 ceiling for S4 may be understated. To check with fresh seeds before the tournament.
- Rivals are not tuned per alpha, so this is a sanity result, not the tournament.

## S8 detector retune (alpha 1, whole run utility)

| setting | U |
|---|---|
| coord, no detector (Wave 2f) | 20.08 |
| coord, lam 30, delta 0.2 | 20.28 |
| coord, lam 30, delta 0.05 | 20.13 |
| coord, lam 10 | 17.7 / 17.9 |
| coord, detector lam 3 (Wave 2f) | 11.59 |
| kwdirect, no detector (Wave 2f) | 18.88 |
| kwdirect, lam 30, delta 0.2 | 18.20 |
| kwdirect, lam 10 | 17.0 / 17.8 |

- A larger threshold removes the damage: lam 30 is level with no detector (coord 20.28 vs 20.08, kwdirect 18.20 vs 18.88).
- The detector gives no measurable gain on this shift; the 5-STA load shift at 30 s is tracked by L2 without a restart. A stronger shift (full cell change) is needed to show a benefit, else Gate L-style evidence for the detector is absent and it stays off by default.
