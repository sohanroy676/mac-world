Table: cell a1c (mentor 1C), stations per AP 20,20. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 30.1 ± 0.2 | – | 14.9 / 15.1 | 0.999 | 0.74 | 90% | 0.71 | 10 |
| BEB + RTS/CTS | 21.1 ± 0.0 | -29.8 ± 0.5 | 10.5 / 10.6 | 1.000 | 0.52 | 0% | 0.84 | 10 |
| DAC | 39.4 ± 0.2 | +31.2 ± 0.7 | 19.6 / 19.8 | 0.999 | 0.96 | 100% | 0.56 | 10 |
| BLADE | 36.8 ± 0.2 | +22.5 ± 0.7 | 18.4 / 18.4 | 0.999 | 0.90 | 100% | 0.53 | 10 |
| IdleSense | 38.1 ± 0.2 | +26.9 ± 0.8 | 19.0 / 19.1 | 0.999 | 0.93 | 100% | 0.55 | 10 |
| KW (online) | 37.2 ± 1.1 | +23.7 ± 3.8 | 18.6 / 18.5 | 0.999 | 0.91 | 100% | 0.60 | 10 |
| Static, Patras model | 35.7 ± 0.3 | +18.8 ± 1.4 | 17.8 / 17.9 | 1.000 | 0.88 | 100% | 0.63 | 10 |
| Static, proportional | 39.6 ± 0.0 | +31.9 ± 1.1 | 19.8 / 19.8 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Static, common (a=0) | 39.6 ± 0.0 | +31.9 ± 1.1 | 19.8 / 19.8 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Static, common (a=1) | 39.6 ± 0.0 | +31.9 ± 1.1 | 19.8 / 19.8 | 1.000 | 0.99 | 100% | 0.57 | 10 |
| Central search (a=0) | 39.2 ± 0.6 | +30.5 ± 2.6 | 19.1 / 20.2 | 0.995 | 0.93 | 100% | 0.60 | 10 |
| Central search (a=1) | 39.0 ± 0.9 | +29.7 ± 3.5 | 19.5 / 19.5 | 0.997 | 0.93 | 100% | 0.60 | 10 |
| Global-CW OSCAR | 38.2 ± 0.2 | +27.0 ± 0.8 | 19.0 / 19.2 | 0.999 | 0.94 | 100% | 0.56 | 10 |
| Independent OSCAR | 16.2 ± 0.4 | -46.1 ± 1.1 | 11.2 / 5.0 | 0.870 | 0.25 | 0% | 0.88 | 10 |
| PF learner | 39.5 ± 0.2 | +31.4 ± 0.7 | 19.3 / 20.2 | 0.999 | 0.96 | 100% | 0.56 | 10 |
