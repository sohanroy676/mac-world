Table: cell a1d (mentor 1D), stations per AP 25,25. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 28.6 ± 0.3 | – | 14.3 / 14.3 | 1.000 | 0.56 | 100% | 0.73 | 5 |
| BEB + RTS/CTS | 20.0 ± 0.1 | -30.2 ± 0.7 | 10.0 / 10.0 | 1.000 | 0.40 | 0% | 0.85 | 5 |
| DAC | 39.5 ± 0.0 | +38.0 ± 1.2 | 19.7 / 19.7 | 0.999 | 0.77 | 100% | 0.56 | 5 |
| BLADE | 37.1 ± 0.0 | +29.5 ± 1.3 | 18.5 / 18.6 | 1.000 | 0.73 | 100% | 0.53 | 5 |
| IdleSense | 38.5 ± 0.1 | +34.7 ± 1.4 | 19.2 / 19.4 | 1.000 | 0.76 | 100% | 0.55 | 5 |
| KW (online) | 34.9 ± 1.5 | +22.1 ± 4.9 | 17.6 / 17.4 | 1.000 | 0.69 | 100% | 0.64 | 5 |
| Static, model (Patras) | 36.6 ± 0.1 | +27.8 ± 1.4 | 18.3 / 18.3 | 1.000 | 0.73 | 100% | 0.63 | 5 |
| Static, proportional | 39.3 ± 0.1 | +37.3 ± 1.4 | 19.7 / 19.6 | 1.000 | 0.78 | 100% | 0.55 | 5 |
| Static, common best (alpha 0) | 39.3 ± 0.1 | +37.3 ± 1.4 | 19.7 / 19.6 | 1.000 | 0.78 | 100% | 0.55 | 5 |
| Static, common best (alpha 1) | 39.3 ± 0.1 | +37.3 ± 1.4 | 19.7 / 19.6 | 1.000 | 0.78 | 100% | 0.55 | 5 |
| Central online search (alpha 0) | 39.3 ± 0.4 | +37.4 ± 1.9 | 19.3 / 20.0 | 0.994 | 0.74 | 100% | 0.62 | 5 |
| Central online search (alpha 1) | 38.7 ± 2.1 | +35.1 ± 7.2 | 19.1 / 19.5 | 0.998 | 0.74 | 100% | 0.61 | 5 |
| Global-CW OSCAR (central actor) | 38.7 ± 0.1 | +35.9 ± 2.2 | 19.7 / 19.0 | 0.998 | 0.75 | 100% | 0.56 | 5 |
| Independent per-AP OSCAR | 23.9 ± 0.4 | -16.8 ± 0.5 | 9.0 / 14.9 | 0.942 | 0.36 | 0% | 0.79 | 5 |
| Independent PF learner | 39.6 ± 0.0 | +39.1 ± 2.0 | 19.3 / 20.3 | 0.998 | 0.76 | 100% | 0.56 | 5 |
