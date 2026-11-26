Table: cell d4a (mentor 4A), stations per AP 10,10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 30.6 ± 0.2 | – | 7.2 / 8.2 / 8.0 / 7.2 | 0.993 | 0.69 | 60% | 0.70 | 10 |
| BEB + RTS/CTS | 21.6 ± 0.0 | -29.4 ± 0.5 | 4.9 / 5.9 / 6.0 / 4.8 | 0.989 | 0.48 | 0% | 0.83 | 10 |
| DAC | 40.0 ± 0.0 | +30.5 ± 1.0 | 9.5 / 10.8 / 10.5 / 9.1 | 0.992 | 0.89 | 100% | 0.56 | 10 |
| BLADE | 36.9 ± 0.0 | +20.2 ± 1.0 | 9.4 / 9.1 / 9.1 / 9.2 | 0.997 | 0.85 | 100% | 0.53 | 9 |
| IdleSense | 38.3 ± 0.1 | +25.2 ± 1.0 | 9.7 / 9.5 / 9.5 / 9.6 | 0.997 | 0.89 | 100% | 0.54 | 10 |
| KW (online) | 31.7 ± 2.2 | +3.5 ± 7.6 | 7.8 / 8.1 / 8.0 / 7.8 | 0.990 | 0.69 | 40% | 0.66 | 10 |
| Static, Patras model | 29.9 ± 0.3 | -2.4 ± 1.3 | 7.2 / 7.9 / 7.9 / 6.9 | 0.995 | 0.68 | 40% | 0.71 | 10 |
| Static, proportional | 40.0 ± 0.0 | +30.7 ± 0.9 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Static, common (a=0) | 40.0 ± 0.0 | +30.7 ± 0.9 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Static, common (a=1) | 40.0 ± 0.0 | +30.7 ± 0.9 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Central search (a=0) | 39.3 ± 1.2 | +28.4 ± 3.7 | 9.3 / 10.0 / 10.3 / 9.8 | 0.986 | 0.86 | 100% | 0.60 | 10 |
| Central search (a=1) | 39.3 ± 0.5 | +28.3 ± 2.2 | 10.0 / 9.5 / 10.5 / 9.4 | 0.982 | 0.85 | 100% | 0.59 | 10 |
| Global-CW OSCAR | 39.9 ± 0.1 | +30.2 ± 1.1 | 10.1 / 9.9 / 9.8 / 10.0 | 0.997 | 0.92 | 100% | 0.55 | 10 |
| Independent OSCAR | 11.3 ± 0.3 | -63.2 ± 0.8 | 3.4 / 2.5 / 1.9 / 3.4 | 0.947 | 0.19 | 0% | 0.93 | 10 |
| PF learner | 39.3 ± 0.1 | +28.4 ± 1.1 | 12.6 / 8.5 / 8.2 / 10.1 | 0.967 | 0.79 | 80% | 0.54 | 10 |
