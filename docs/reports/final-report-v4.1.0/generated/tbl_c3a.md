Table: cell c3a (mentor 3A), stations per AP 10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 32.5 ± 0.1 | – | 10.4 / 11.6 / 10.4 | 0.996 | 1.02 | 80% | 0.68 | 10 |
| BEB + RTS/CTS | 22.7 ± 0.0 | -30.1 ± 0.3 | 7.1 / 8.4 / 7.2 | 0.994 | 0.70 | 0% | 0.83 | 10 |
| DAC | 39.9 ± 0.0 | +23.1 ± 0.5 | 12.6 / 14.7 / 12.6 | 0.992 | 1.23 | 100% | 0.55 | 9 |
| BLADE | 36.8 ± 0.0 | +13.4 ± 0.5 | 12.2 / 12.2 / 12.4 | 0.999 | 1.19 | 100% | 0.53 | 10 |
| IdleSense | 38.0 ± 0.0 | +17.2 ± 0.5 | 12.6 / 12.6 / 12.8 | 0.999 | 1.23 | 100% | 0.54 | 10 |
| KW (online) | 38.6 ± 1.1 | +18.9 ± 3.4 | 12.9 / 12.8 / 12.9 | 0.999 | 1.24 | 100% | 0.58 | 10 |
| Static, Patras model | 33.8 ± 0.1 | +4.0 ± 0.6 | 11.1 / 11.7 / 11.0 | 0.999 | 1.10 | 100% | 0.67 | 10 |
| Static, proportional | 40.0 ± 0.0 | +23.3 ± 0.5 | 13.3 / 13.5 / 13.3 | 1.000 | 1.32 | 100% | 0.55 | 10 |
| Static, common (a=0) | 40.0 ± 0.0 | +23.3 ± 0.5 | 13.3 / 13.5 / 13.3 | 1.000 | 1.32 | 100% | 0.55 | 10 |
| Static, common (a=1) | 40.0 ± 0.0 | +23.3 ± 0.5 | 13.3 / 13.5 / 13.3 | 1.000 | 1.32 | 100% | 0.55 | 10 |
| Central search (a=0) | 39.3 ± 0.6 | +21.0 ± 1.8 | 12.7 / 12.9 / 13.7 | 0.988 | 1.17 | 100% | 0.59 | 10 |
| Central search (a=1) | 37.1 ± 1.9 | +14.3 ± 5.5 | 12.0 / 12.9 / 12.2 | 0.991 | 1.13 | 100% | 0.62 | 10 |
| Global-CW OSCAR | 38.8 ± 0.0 | +19.5 ± 0.6 | 12.9 / 12.9 / 13.0 | 0.999 | 1.25 | 100% | 0.55 | 10 |
| Independent OSCAR | 14.7 ± 0.3 | -54.8 ± 0.7 | 3.1 / 5.5 / 6.0 | 0.938 | 0.31 | 0% | 0.89 | 10 |
| PF learner | 40.1 ± 0.0 | +23.6 ± 0.5 | 11.1 / 16.6 / 12.5 | 0.969 | 1.11 | 100% | 0.56 | 10 |
