Table: cell c3d (mentor 3D), stations per AP 20,20,20,20. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 25.6 ± 0.3 | – | 6.1 / 6.9 / 6.7 / 5.9 | 0.984 | 0.26 | 20% | 0.76 | 10 |
| BEB + RTS/CTS | 18.0 ± 0.0 | -29.6 ± 0.9 | 4.1 / 4.9 / 4.9 / 4.1 | 0.993 | 0.20 | 0% | 0.86 | 10 |
| DAC | 39.3 ± 0.5 | +53.3 ± 1.9 | 9.4 / 10.6 / 9.9 / 9.4 | 0.984 | 0.40 | 90% | 0.66 | 10 |
| BLADE | 37.8 ± 0.3 | +47.5 ± 2.8 | 9.3 / 9.7 / 9.6 / 9.2 | 0.992 | 0.42 | 100% | 0.54 | 10 |
| IdleSense | 38.8 ± 0.2 | +51.6 ± 2.4 | 9.6 / 9.9 / 10.0 / 9.4 | 0.994 | 0.44 | 100% | 0.56 | 10 |
| KW (online) | 19.1 ± 1.6 | -25.4 ± 5.7 | 4.8 / 4.9 / 4.8 / 4.6 | 0.990 | 0.21 | 0% | 0.86 | 10 |
| Static, Patras model | 28.8 ± 0.2 | +12.4 ± 2.1 | 6.9 / 7.4 / 7.4 / 7.0 | 0.997 | 0.34 | 100% | 0.73 | 10 |
| Static, proportional | 39.6 ± 0.0 | +54.4 ± 2.0 | 9.8 / 10.0 / 10.0 / 9.8 | 1.000 | 0.49 | 100% | 0.57 | 10 |
| Static, common (a=0) | 39.6 ± 0.0 | +54.4 ± 2.0 | 9.8 / 10.0 / 10.0 / 9.8 | 1.000 | 0.49 | 100% | 0.57 | 10 |
| Static, common (a=1) | 39.6 ± 0.0 | +54.4 ± 2.0 | 9.8 / 10.0 / 10.0 / 9.8 | 1.000 | 0.49 | 100% | 0.57 | 10 |
| Central search (a=0) | 39.2 ± 0.3 | +53.2 ± 2.2 | 9.5 / 10.0 / 10.3 / 9.4 | 0.962 | 0.39 | 100% | 0.62 | 10 |
| Central search (a=1) | 39.2 ± 0.4 | +52.9 ± 2.3 | 9.2 / 10.4 / 9.6 / 10.0 | 0.990 | 0.44 | 100% | 0.59 | 10 |
| Global-CW OSCAR | 38.9 ± 0.3 | +51.9 ± 2.4 | 9.5 / 9.9 / 10.0 / 9.4 | 0.993 | 0.43 | 100% | 0.55 | 10 |
| Independent OSCAR | 6.7 ± 0.7 | -73.9 ± 2.6 | 1.4 / 0.2 / 3.1 / 2.0 | 0.705 | 0.01 | 0% | 0.96 | 10 |
| PF learner | 38.1 ± 0.3 | +48.6 ± 2.7 | 8.6 / 8.9 / 9.0 / 11.5 | 0.979 | 0.41 | 100% | 0.54 | 10 |
