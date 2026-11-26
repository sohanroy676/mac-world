Table: cell a1b (mentor 1B), stations per AP 15,15. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 32.0 ± 0.1 | – | 15.9 / 16.1 | 1.000 | 1.05 | 100% | 0.69 | 10 |
| BEB + RTS/CTS | 22.4 ± 0.0 | -30.0 ± 0.2 | 11.3 / 11.1 | 0.999 | 0.73 | 0% | 0.83 | 10 |
| DAC | 39.6 ± 0.1 | +23.6 ± 0.4 | 19.5 / 20.1 | 0.999 | 1.28 | 100% | 0.55 | 10 |
| BLADE | 36.8 ± 0.0 | +14.9 ± 0.3 | 18.2 / 18.6 | 1.000 | 1.21 | 100% | 0.53 | 10 |
| IdleSense | 38.0 ± 0.0 | +18.6 ± 0.4 | 18.8 / 19.2 | 1.000 | 1.25 | 100% | 0.54 | 10 |
| KW (online) | 38.9 ± 0.9 | +21.4 ± 2.9 | 19.6 / 19.2 | 0.998 | 1.26 | 100% | 0.57 | 10 |
| Static, Patras model | 36.5 ± 0.3 | +13.9 ± 1.1 | 18.2 / 18.3 | 1.000 | 1.21 | 100% | 0.63 | 10 |
| Static, proportional | 39.8 ± 0.0 | +24.2 ± 0.4 | 19.9 / 19.9 | 1.000 | 1.32 | 100% | 0.55 | 10 |
| Static, common (a=0) | 39.8 ± 0.0 | +24.2 ± 0.4 | 19.9 / 19.9 | 1.000 | 1.32 | 100% | 0.55 | 10 |
| Static, common (a=1) | 39.8 ± 0.0 | +24.2 ± 0.4 | 19.9 / 19.9 | 1.000 | 1.32 | 100% | 0.55 | 10 |
| Central search (a=0) | 38.3 ± 1.9 | +19.6 ± 5.9 | 18.8 / 19.5 | 0.998 | 1.23 | 100% | 0.61 | 10 |
| Central search (a=1) | 37.1 ± 1.9 | +15.8 ± 6.0 | 18.0 / 19.1 | 0.997 | 1.18 | 100% | 0.63 | 10 |
| Global-CW OSCAR | 39.7 ± 0.0 | +23.9 ± 0.3 | 19.6 / 20.0 | 1.000 | 1.31 | 100% | 0.56 | 10 |
| Independent OSCAR | 20.8 ± 0.1 | -35.0 ± 0.3 | 10.9 / 9.9 | 0.997 | 0.66 | 0% | 0.82 | 10 |
| PF learner | 39.4 ± 0.0 | +23.1 ± 0.4 | 17.2 / 22.2 | 0.984 | 1.15 | 100% | 0.56 | 10 |
