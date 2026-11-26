Table: cell d4d (mentor 4D), stations per AP 40,20,10,5. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 26.5 ± 0.4 | – | 11.8 / 8.4 / 4.4 / 1.9 | 0.972 | 0.29 | 80% | 0.75 | 10 |
| BEB + RTS/CTS | 18.2 ± 0.0 | -31.5 ± 0.9 | 8.7 / 5.4 / 2.7 / 1.4 | 0.992 | 0.22 | 0% | 0.86 | 9 |
| DAC | 39.1 ± 0.4 | +47.7 ± 2.5 | 17.5 / 12.2 / 6.4 / 3.0 | 0.977 | 0.44 | 100% | 0.57 | 10 |
| BLADE | 37.4 ± 0.2 | +40.9 ± 2.3 | 18.7 / 10.9 / 5.3 / 2.5 | 0.988 | 0.44 | 89% | 0.53 | 9 |
| IdleSense | 38.8 ± 0.2 | +46.6 ± 2.3 | 19.3 / 11.2 / 5.6 / 2.6 | 0.989 | 0.46 | 100% | 0.55 | 10 |
| KW (online) | 21.4 ± 1.8 | -19.2 ± 6.0 | 6.8 / 5.8 / 4.9 / 3.8 | 0.779 | 0.17 | 0% | 0.83 | 10 |
| Static, Patras model | 32.1 ± 0.4 | +21.4 ± 2.5 | 3.6 / 9.3 / 10.0 / 9.2 | 0.626 | 0.09 | 0% | 0.69 | 10 |
| Static, proportional | 39.9 ± 0.0 | +51.0 ± 2.2 | 4.3 / 11.9 / 12.0 / 11.7 | 0.618 | 0.11 | 0% | 0.55 | 10 |
| Static, common (a=0) | 39.6 ± 0.0 | +49.8 ± 2.3 | 19.5 / 11.6 / 5.7 / 2.9 | 0.994 | 0.49 | 100% | 0.56 | 10 |
| Static, common (a=1) | 39.6 ± 0.0 | +49.8 ± 2.3 | 19.5 / 11.6 / 5.7 / 2.9 | 0.994 | 0.49 | 100% | 0.56 | 10 |
| Central search (a=0) | 39.2 ± 0.4 | +48.2 ± 2.0 | 16.6 / 10.8 / 7.5 / 4.3 | 0.897 | 0.40 | 100% | 0.62 | 10 |
| Central search (a=1) | 39.0 ± 0.4 | +47.6 ± 1.5 | 19.8 / 10.9 / 5.4 / 3.0 | 0.971 | 0.45 | 100% | 0.60 | 10 |
| Global-CW OSCAR | 38.3 ± 0.2 | +44.8 ± 2.5 | 19.1 / 11.1 / 5.5 / 2.6 | 0.989 | 0.45 | 90% | 0.55 | 10 |
| Independent OSCAR | 9.7 ± 0.6 | -63.3 ± 2.1 | 1.0 / 1.2 / 4.1 / 3.3 | 0.545 | 0.03 | 0% | 0.91 | 10 |
| PF learner | 39.6 ± 0.1 | +49.5 ± 2.2 | 11.2 / 6.0 / 11.4 / 10.9 | 0.611 | 0.27 | 0% | 0.56 | 10 |
