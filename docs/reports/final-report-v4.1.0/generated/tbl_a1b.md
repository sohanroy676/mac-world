Table: cell a1b (mentor 1B), stations per AP 15,15. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 32.0 ± 0.1 | – | 15.9 / 16.1 | 1.000 | 1.06 | 100% | 0.69 | 5 |
| BEB + RTS/CTS | 22.4 ± 0.0 | -30.0 ± 0.3 | 11.3 / 11.1 | 0.999 | 0.73 | 0% | 0.83 | 5 |
| DAC | 39.6 ± 0.1 | +23.8 ± 0.5 | 19.3 / 20.3 | 0.998 | 1.27 | 100% | 0.55 | 5 |
| BLADE | 36.8 ± 0.0 | +15.0 ± 0.5 | 18.3 / 18.5 | 1.000 | 1.22 | 100% | 0.53 | 5 |
| IdleSense | 38.0 ± 0.1 | +18.8 ± 0.4 | 18.8 / 19.1 | 1.000 | 1.26 | 100% | 0.54 | 5 |
| KW (online) | 39.3 ± 0.7 | +23.0 ± 2.5 | 20.3 / 19.1 | 0.997 | 1.27 | 100% | 0.56 | 5 |
| Static, model (Patras) | 36.7 ± 0.5 | +14.6 ± 1.2 | 18.4 / 18.3 | 1.000 | 1.22 | 100% | 0.63 | 5 |
| Static, proportional | 39.8 ± 0.1 | +24.4 ± 0.6 | 19.9 / 19.9 | 1.000 | 1.33 | 100% | 0.55 | 5 |
| Static, common best (alpha 0) | 39.8 ± 0.1 | +24.4 ± 0.6 | 19.9 / 19.9 | 1.000 | 1.33 | 100% | 0.55 | 5 |
| Static, common best (alpha 1) | 39.8 ± 0.1 | +24.4 ± 0.6 | 19.9 / 19.9 | 1.000 | 1.33 | 100% | 0.55 | 5 |
| Central online search (alpha 0) | 39.5 ± 0.5 | +23.5 ± 1.3 | 19.2 / 20.3 | 0.998 | 1.26 | 100% | 0.60 | 5 |
| Central online search (alpha 1) | 38.2 ± 1.8 | +19.4 ± 5.6 | 18.3 / 19.9 | 0.995 | 1.19 | 100% | 0.61 | 5 |
| Global-CW OSCAR (central actor) | 39.7 ± 0.0 | +24.1 ± 0.8 | 19.7 / 20.0 | 1.000 | 1.31 | 100% | 0.56 | 5 |
| Independent per-AP OSCAR | 20.8 ± 0.2 | -35.2 ± 0.4 | 11.0 / 9.8 | 0.997 | 0.65 | 0% | 0.82 | 5 |
| Independent PF learner | 39.4 ± 0.0 | +23.5 ± 0.6 | 17.3 / 22.2 | 0.985 | 1.15 | 100% | 0.56 | 5 |
