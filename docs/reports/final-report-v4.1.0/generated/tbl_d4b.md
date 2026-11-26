Table: cell d4b (mentor 4B), stations per AP 10,20,30,40. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 24.6 ± 0.5 | – | 3.0 / 5.9 / 7.3 / 8.4 | 0.958 | 0.19 | 30% | 0.78 | 10 |
| BEB + RTS/CTS | 16.7 ± 0.0 | -32.2 ± 1.3 | 1.8 / 3.6 / 5.3 / 6.0 | 0.995 | 0.15 | 0% | 0.88 | 10 |
| DAC | 30.3 ± 13.2 | +22.5 ± 53.4 | 3.7 / 6.9 / 9.1 / 10.7 | 0.888 | 0.22 | 78% | 0.79 | 9 |
| BLADE | 38.4 ± 0.2 | +56.4 ± 3.7 | 4.2 / 8.7 / 11.3 / 14.3 | 0.972 | 0.30 | 100% | 0.54 | 10 |
| IdleSense | 39.2 ± 0.1 | +59.4 ± 3.0 | 4.3 / 8.9 / 11.5 / 14.6 | 0.972 | 0.31 | 100% | 0.56 | 10 |
| KW (online) | 13.2 ± 5.2 | -46.4 ± 20.9 | 2.9 / 3.0 / 3.6 / 3.7 | 0.801 | 0.09 | 0% | 0.92 | 10 |
| Static, Patras model | 32.7 ± 0.4 | +33.0 ± 2.9 | 10.7 / 10.8 / 7.0 / 4.2 | 0.633 | 0.11 | 0% | 0.68 | 10 |
| Static, proportional | 39.8 ± 0.0 | +61.8 ± 3.0 | 13.6 / 13.7 / 8.1 / 4.3 | 0.610 | 0.11 | 0% | 0.57 | 10 |
| Static, common (a=0) | 39.2 ± 0.1 | +59.7 ± 2.9 | 4.4 / 8.9 / 12.6 / 13.2 | 0.984 | 0.33 | 100% | 0.58 | 10 |
| Static, common (a=1) | 39.2 ± 0.1 | +59.7 ± 2.9 | 4.4 / 8.9 / 12.6 / 13.2 | 0.984 | 0.33 | 100% | 0.58 | 10 |
| Central search (a=0) | 38.9 ± 0.6 | +58.4 ± 3.1 | 5.4 / 9.0 / 11.8 / 12.7 | 0.911 | 0.30 | 100% | 0.63 | 10 |
| Central search (a=1) | 39.0 ± 0.5 | +58.9 ± 2.2 | 4.3 / 7.7 / 11.3 / 15.6 | 0.989 | 0.35 | 100% | 0.60 | 9 |
| Global-CW OSCAR | 38.6 ± 0.2 | +57.1 ± 3.8 | 4.2 / 8.7 / 11.3 / 14.4 | 0.973 | 0.30 | 100% | 0.54 | 10 |
| Independent OSCAR | 7.0 ± 1.2 | -71.3 ± 5.0 | 2.6 / 3.5 / 0.8 / 0.2 | 0.542 | 0.01 | 0% | 0.96 | 10 |
| PF learner | 38.2 ± 0.2 | +55.4 ± 2.7 | 9.5 / 8.6 / 10.8 / 9.4 | 0.765 | 0.23 | 70% | 0.58 | 10 |
