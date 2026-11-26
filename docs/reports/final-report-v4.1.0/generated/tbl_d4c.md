Table: cell d4c (mentor 4C), stations per AP 5,15,25,35. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 25.7 ± 0.6 | – | 2.0 / 5.5 / 8.4 / 9.9 | 0.979 | 0.28 | 40% | 0.76 | 10 |
| BEB + RTS/CTS | 17.8 ± 0.0 | -30.7 ± 1.9 | 1.2 / 3.5 / 5.9 / 7.1 | 0.994 | 0.20 | 0% | 0.87 | 10 |
| DAC | 37.3 ± 4.9 | +44.9 ± 19.2 | 3.0 / 7.5 / 12.3 / 14.5 | 0.976 | 0.41 | 90% | 0.64 | 10 |
| BLADE | 37.7 ± 0.2 | +46.6 ± 4.3 | 2.6 / 7.4 / 11.9 / 15.7 | 0.988 | 0.41 | 100% | 0.54 | 10 |
| IdleSense | 38.8 ± 0.2 | +51.1 ± 3.6 | 2.7 / 7.8 / 12.4 / 16.0 | 0.987 | 0.42 | 100% | 0.56 | 10 |
| KW (online) | 19.1 ± 1.4 | -25.8 ± 5.0 | 3.7 / 4.8 / 5.3 / 5.3 | 0.715 | 0.15 | 0% | 0.86 | 10 |
| Static, Patras model | 32.3 ± 0.6 | +25.6 ± 3.6 | 9.6 / 10.4 / 7.6 / 4.7 | 0.547 | 0.13 | 0% | 0.68 | 10 |
| Static, proportional | 39.9 ± 0.0 | +55.2 ± 3.9 | 11.9 / 12.3 / 10.1 / 5.5 | 0.542 | 0.16 | 0% | 0.56 | 10 |
| Static, common (a=0) | 39.5 ± 0.1 | +53.8 ± 3.7 | 2.6 / 7.8 / 13.0 / 16.1 | 0.996 | 0.46 | 100% | 0.57 | 10 |
| Static, common (a=1) | 39.5 ± 0.1 | +53.8 ± 3.7 | 2.6 / 7.8 / 13.0 / 16.1 | 0.996 | 0.46 | 100% | 0.57 | 10 |
| Central search (a=0) | 39.2 ± 0.6 | +52.4 ± 2.3 | 4.6 / 8.1 / 11.8 / 14.7 | 0.874 | 0.39 | 100% | 0.62 | 10 |
| Central search (a=1) | 39.2 ± 0.2 | +52.7 ± 3.6 | 3.0 / 7.4 / 12.2 / 16.6 | 0.982 | 0.46 | 100% | 0.59 | 10 |
| Global-CW OSCAR | 38.8 ± 0.2 | +50.9 ± 3.2 | 2.7 / 7.7 / 12.3 / 16.0 | 0.987 | 0.42 | 100% | 0.56 | 10 |
| Independent OSCAR | 12.2 ± 0.6 | -52.5 ± 1.9 | 3.3 / 1.5 / 5.3 / 2.2 | 0.543 | 0.06 | 0% | 0.91 | 10 |
| PF learner | 39.0 ± 0.1 | +51.9 ± 3.8 | 10.1 / 8.4 / 9.2 / 11.3 | 0.578 | 0.31 | 80% | 0.55 | 10 |
