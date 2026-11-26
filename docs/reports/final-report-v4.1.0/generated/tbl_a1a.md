Table: cell a1a (mentor 1A), stations per AP 10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 34.8 ± 0.2 | – | 17.4 / 17.4 | 0.999 | 1.70 | 80% | 0.66 | 10 |
| BEB + RTS/CTS | 24.2 ± 0.0 | -30.5 ± 0.4 | 12.1 / 12.0 | 1.000 | 1.19 | 0% | 0.81 | 10 |
| DAC | 39.9 ± 0.0 | +14.8 ± 0.7 | 20.5 / 19.4 | 0.997 | 1.90 | 100% | 0.55 | 10 |
| BLADE | 36.6 ± 0.0 | +5.3 ± 0.6 | 18.3 / 18.3 | 0.999 | 1.81 | 100% | 0.53 | 10 |
| IdleSense | 37.9 ± 0.0 | +8.9 ± 0.6 | 19.0 / 18.9 | 0.999 | 1.87 | 100% | 0.53 | 10 |
| KW (online) | 40.0 ± 0.0 | +15.1 ± 0.6 | 20.0 / 20.0 | 1.000 | 1.97 | 100% | 0.56 | 10 |
| Static, Patras model | 37.6 ± 0.4 | +8.0 ± 0.8 | 18.7 / 18.9 | 1.000 | 1.86 | 100% | 0.62 | 10 |
| Static, proportional | 40.1 ± 0.0 | +15.4 ± 0.6 | 20.0 / 20.1 | 1.000 | 2.00 | 100% | 0.57 | 10 |
| Static, common (a=0) | 40.1 ± 0.0 | +15.4 ± 0.6 | 20.0 / 20.1 | 1.000 | 2.00 | 100% | 0.57 | 10 |
| Static, common (a=1) | 40.1 ± 0.0 | +15.4 ± 0.6 | 20.0 / 20.1 | 1.000 | 2.00 | 100% | 0.57 | 10 |
| Central search (a=0) | 39.0 ± 0.9 | +12.2 ± 3.0 | 19.2 / 19.9 | 0.996 | 1.87 | 90% | 0.60 | 10 |
| Central search (a=1) | 38.9 ± 0.9 | +11.9 ± 2.7 | 19.4 / 19.5 | 0.999 | 1.88 | 100% | 0.60 | 9 |
| Global-CW OSCAR | 40.1 ± 0.0 | +15.3 ± 0.6 | 20.1 / 20.0 | 0.999 | 1.98 | 100% | 0.56 | 10 |
| Independent OSCAR | 23.1 ± 0.2 | -33.6 ± 0.6 | 10.0 / 13.1 | 0.983 | 1.00 | 0% | 0.80 | 10 |
| PF learner | 40.1 ± 0.0 | +15.3 ± 0.7 | 20.1 / 20.0 | 0.999 | 1.98 | 100% | 0.56 | 10 |
