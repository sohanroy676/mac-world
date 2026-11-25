Table: cell c3b (mentor 3B), stations per AP 20,20,20. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 27.3 ± 0.3 | – | 8.8 / 9.5 / 9.0 | 0.997 | 0.43 | 20% | 0.75 | 5 |
| BEB + RTS/CTS | 19.3 ± 0.1 | -29.3 ± 1.0 | 6.2 / 6.9 / 6.2 | 0.997 | 0.31 | 0% | 0.85 | 5 |
| DAC | 39.1 ± 0.5 | +43.4 ± 1.7 | 12.8 / 13.7 / 12.6 | 0.997 | 0.61 | 100% | 0.57 | 5 |
| BLADE | 36.7 ± 0.5 | +34.6 ± 1.5 | 12.1 / 12.2 / 12.5 | 0.997 | 0.57 | 100% | 0.54 | 5 |
| IdleSense | 38.4 ± 0.4 | +40.6 ± 1.6 | 12.6 / 12.8 / 13.0 | 0.998 | 0.60 | 100% | 0.56 | 5 |
| KW (online) | 27.1 ± 5.8 | -0.8 ± 19.9 | 8.7 / 9.0 / 9.4 | 0.992 | 0.41 | 20% | 0.75 | 5 |
| Static, model (Patras) | 32.6 ± 0.3 | +19.4 ± 1.5 | 10.7 / 11.2 / 10.7 | 1.000 | 0.53 | 100% | 0.68 | 5 |
| Static, proportional | 39.7 ± 0.0 | +45.3 ± 1.9 | 13.2 / 13.3 / 13.2 | 1.000 | 0.66 | 100% | 0.56 | 5 |
| Static, common best (alpha 0) | 39.7 ± 0.0 | +45.3 ± 1.9 | 13.2 / 13.3 / 13.2 | 1.000 | 0.66 | 100% | 0.56 | 5 |
| Static, common best (alpha 1) | 39.7 ± 0.0 | +45.3 ± 1.9 | 13.2 / 13.3 / 13.2 | 1.000 | 0.66 | 100% | 0.56 | 5 |
| Central online search (alpha 0) | 38.6 ± 0.3 | +41.4 ± 2.0 | 12.3 / 12.2 / 14.1 | 0.963 | 0.55 | 100% | 0.64 | 5 |
| Central online search (alpha 1) | 39.0 ± 0.4 | +42.8 ± 2.4 | 13.2 / 12.1 / 13.6 | 0.985 | 0.57 | 100% | 0.61 | 5 |
| Global-CW OSCAR (central actor) | 37.2 ± 0.5 | +36.3 ± 4.9 | 12.5 / 12.1 / 12.7 | 0.998 | 0.59 | 100% | 0.54 | 5 |
| Independent per-AP OSCAR | 5.4 ± 0.3 | -80.4 ± 3.4 | 1.7 / 2.1 / 1.5 | 0.976 | 0.07 | 0% | 0.97 | 5 |
| Independent PF learner | 38.6 ± 0.5 | +41.2 ± 4.4 | 12.6 / 13.1 / 12.9 | 0.998 | 0.62 | 100% | 0.55 | 5 |
