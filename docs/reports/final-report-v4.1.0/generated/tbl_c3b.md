Table: cell c3b (mentor 3B), stations per AP 20,20,20. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 27.4 ± 0.2 | – | 8.9 / 9.5 / 9.0 | 0.997 | 0.43 | 50% | 0.74 | 10 |
| BEB + RTS/CTS | 19.3 ± 0.0 | -29.5 ± 0.5 | 6.1 / 6.9 / 6.2 | 0.997 | 0.31 | 0% | 0.85 | 10 |
| DAC | 39.4 ± 0.3 | +43.9 ± 0.9 | 13.2 / 13.7 / 12.5 | 0.995 | 0.61 | 100% | 0.57 | 10 |
| BLADE | 37.0 ± 0.3 | +35.0 ± 0.8 | 12.3 / 12.3 / 12.3 | 0.997 | 0.58 | 100% | 0.53 | 10 |
| IdleSense | 38.6 ± 0.2 | +40.9 ± 0.8 | 12.7 / 12.8 / 13.0 | 0.999 | 0.62 | 100% | 0.55 | 10 |
| KW (online) | 28.8 ± 2.7 | +5.2 ± 9.5 | 9.6 / 9.4 / 9.9 | 0.994 | 0.44 | 50% | 0.73 | 10 |
| Static, Patras model | 32.5 ± 0.1 | +18.9 ± 0.8 | 10.7 / 11.1 / 10.7 | 1.000 | 0.53 | 100% | 0.68 | 10 |
| Static, proportional | 39.7 ± 0.0 | +44.9 ± 0.9 | 13.2 / 13.3 / 13.2 | 1.000 | 0.66 | 100% | 0.56 | 10 |
| Static, common (a=0) | 39.7 ± 0.0 | +44.9 ± 0.9 | 13.2 / 13.3 / 13.2 | 1.000 | 0.66 | 100% | 0.56 | 10 |
| Static, common (a=1) | 39.7 ± 0.0 | +44.9 ± 0.9 | 13.2 / 13.3 / 13.2 | 1.000 | 0.66 | 100% | 0.56 | 10 |
| Central search (a=0) | 39.1 ± 0.4 | +42.7 ± 1.4 | 13.0 / 13.1 / 13.0 | 0.973 | 0.57 | 100% | 0.62 | 10 |
| Central search (a=1) | 39.2 ± 0.3 | +43.4 ± 1.1 | 13.1 / 12.7 / 13.4 | 0.990 | 0.59 | 100% | 0.60 | 10 |
| Global-CW OSCAR | 37.3 ± 0.3 | +36.4 ± 1.0 | 12.4 / 12.5 / 12.5 | 0.998 | 0.59 | 100% | 0.54 | 10 |
| Independent OSCAR | 5.3 ± 0.3 | -80.7 ± 1.0 | 1.7 / 2.2 / 1.4 | 0.970 | 0.07 | 0% | 0.97 | 10 |
| PF learner | 38.7 ± 0.3 | +41.5 ± 0.9 | 12.4 / 13.5 / 12.8 | 0.997 | 0.61 | 100% | 0.55 | 10 |
