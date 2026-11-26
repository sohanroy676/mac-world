Table: cell f6s (mentor 6 saturated), stations per AP 10,10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 30.7 ± 0.1 | – | 7.3 / 8.3 / 8.2 / 6.9 | 0.993 | 0.69 | 100% | 0.70 | 10 |
| BEB + RTS/CTS | 21.6 ± 0.0 | -29.4 ± 0.3 | 4.8 / 6.0 / 6.0 / 4.8 | 0.988 | 0.48 | 0% | 0.83 | 10 |
| DAC | 39.8 ± 0.3 | +29.8 ± 1.0 | 9.4 / 10.7 / 10.7 / 8.9 | 0.990 | 0.89 | 100% | 0.56 | 10 |
| BLADE | 36.8 ± 0.0 | +20.1 ± 0.6 | 9.4 / 9.2 / 9.2 / 9.1 | 0.999 | 0.89 | 100% | 0.53 | 10 |
| IdleSense | 38.4 ± 0.0 | +25.1 ± 0.6 | 9.7 / 9.6 / 9.6 / 9.4 | 0.998 | 0.92 | 100% | 0.54 | 10 |
| KW (online) | 33.0 ± 1.9 | +7.6 ± 6.1 | 8.3 / 8.1 / 8.4 / 8.3 | 0.989 | 0.73 | 60% | 0.66 | 10 |
| Static, Patras model | 30.0 ± 0.3 | -2.1 ± 1.2 | 7.2 / 7.8 / 7.9 / 7.1 | 0.995 | 0.68 | 60% | 0.71 | 10 |
| Static, proportional | 40.0 ± 0.1 | +30.6 ± 0.6 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Static, common (a=0) | 40.0 ± 0.1 | +30.6 ± 0.6 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Static, common (a=1) | 40.0 ± 0.1 | +30.6 ± 0.6 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Central search (a=0) | 38.5 ± 1.3 | +25.6 ± 4.4 | 10.0 / 9.7 / 10.2 / 8.6 | 0.982 | 0.83 | 100% | 0.62 | 10 |
| Central search (a=1) | 38.8 ± 0.9 | +26.4 ± 3.1 | 9.8 / 9.3 / 10.1 / 9.6 | 0.975 | 0.83 | 100% | 0.60 | 10 |
| Global-CW OSCAR | 38.3 ± 0.1 | +25.0 ± 0.8 | 9.7 / 9.6 / 9.6 / 9.4 | 0.998 | 0.92 | 100% | 0.54 | 10 |
| Independent OSCAR | 10.0 ± 0.3 | -67.3 ± 0.9 | 2.6 / 2.3 / 2.3 / 2.8 | 0.991 | 0.22 | 0% | 0.94 | 10 |
| PF learner | 38.9 ± 0.1 | +26.8 ± 0.7 | 10.8 / 7.3 / 11.7 / 9.1 | 0.970 | 0.73 | 70% | 0.55 | 10 |
