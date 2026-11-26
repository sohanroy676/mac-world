Table: cell a1d (mentor 1D), stations per AP 25,25. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 28.7 ± 0.3 | – | 14.7 / 14.0 | 0.993 | 0.55 | 70% | 0.73 | 10 |
| BEB + RTS/CTS | 20.0 ± 0.0 | -30.4 ± 0.7 | 10.0 / 10.0 | 1.000 | 0.40 | 0% | 0.85 | 10 |
| DAC | 39.4 ± 0.2 | +37.1 ± 1.3 | 20.3 / 19.1 | 0.994 | 0.75 | 100% | 0.56 | 10 |
| BLADE | 37.0 ± 0.2 | +28.7 ± 1.3 | 18.9 / 18.1 | 0.994 | 0.71 | 100% | 0.53 | 10 |
| IdleSense | 38.4 ± 0.2 | +33.7 ± 1.4 | 19.6 / 18.8 | 0.994 | 0.73 | 100% | 0.55 | 10 |
| KW (online) | 34.5 ± 1.3 | +20.1 ± 4.3 | 17.4 / 17.1 | 0.999 | 0.67 | 100% | 0.65 | 10 |
| Static, Patras model | 36.6 ± 0.0 | +27.2 ± 1.3 | 18.3 / 18.3 | 1.000 | 0.73 | 100% | 0.63 | 10 |
| Static, proportional | 39.3 ± 0.0 | +36.8 ± 1.4 | 19.7 / 19.6 | 1.000 | 0.79 | 100% | 0.55 | 10 |
| Static, common (a=0) | 39.3 ± 0.0 | +36.8 ± 1.4 | 19.7 / 19.6 | 1.000 | 0.79 | 100% | 0.55 | 10 |
| Static, common (a=1) | 39.3 ± 0.0 | +36.8 ± 1.4 | 19.7 / 19.6 | 1.000 | 0.79 | 100% | 0.55 | 10 |
| Central search (a=0) | 39.3 ± 0.2 | +36.7 ± 1.4 | 19.5 / 19.8 | 0.993 | 0.73 | 100% | 0.62 | 10 |
| Central search (a=1) | 38.9 ± 0.9 | +35.4 ± 3.0 | 19.0 / 19.9 | 0.997 | 0.75 | 100% | 0.60 | 10 |
| Global-CW OSCAR | 38.6 ± 0.2 | +34.3 ± 1.5 | 19.7 / 18.9 | 0.994 | 0.74 | 100% | 0.56 | 10 |
| Independent OSCAR | 24.1 ± 0.4 | -16.2 ± 0.7 | 9.3 / 14.8 | 0.942 | 0.37 | 0% | 0.78 | 10 |
| PF learner | 39.5 ± 0.2 | +37.6 ± 1.4 | 19.3 / 20.2 | 0.994 | 0.74 | 100% | 0.56 | 10 |
