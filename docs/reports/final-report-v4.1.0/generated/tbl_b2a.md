Table: cell b2a (mentor 2A), stations per AP 10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 72.5 ± 0.3 | – | 17.4 / 17.4 / 37.8 | 0.864 | 1.70 | 80% | 0.64 | 10 |
| BEB + RTS/CTS | 50.3 ± 0.0 | -30.6 ± 0.3 | 12.1 / 12.0 / 26.2 | 0.864 | 1.19 | 0% | 0.80 | 10 |
| DAC | 79.8 ± 0.0 | +10.0 ± 0.5 | 20.5 / 19.4 / 39.9 | 0.889 | 1.90 | 100% | 0.55 | 10 |
| BLADE | 72.9 ± 0.0 | +0.5 ± 0.4 | 18.3 / 18.3 / 36.3 | 0.892 | 1.81 | 100% | 0.53 | 10 |
| IdleSense | 75.1 ± 0.0 | +3.5 ± 0.4 | 19.0 / 18.9 / 37.2 | 0.894 | 1.87 | 100% | 0.53 | 10 |
| KW (online) | 80.0 ± 0.0 | +10.3 ± 0.4 | 20.0 / 20.0 / 40.0 | 0.889 | 1.99 | 100% | 0.56 | 10 |
| Static, Patras model | 77.8 ± 0.4 | +7.3 ± 0.5 | 18.7 / 18.9 / 40.3 | 0.868 | 1.86 | 100% | 0.59 | 10 |
| Static, proportional | 78.9 ± 0.1 | +8.7 ± 0.4 | 20.0 / 20.1 / 38.7 | 0.899 | 2.00 | 100% | 0.55 | 10 |
| Static, common (a=0) | 78.9 ± 0.1 | +8.7 ± 0.4 | 20.0 / 20.1 / 38.7 | 0.899 | 2.00 | 100% | 0.55 | 10 |
| Static, common (a=1) | 78.9 ± 0.1 | +8.7 ± 0.4 | 20.0 / 20.1 / 38.7 | 0.899 | 2.00 | 100% | 0.55 | 10 |
| Central search (a=0) | 78.6 ± 1.7 | +8.3 ± 2.2 | 19.1 / 19.6 / 39.9 | 0.878 | 1.88 | 90% | 0.58 | 10 |
| Central search (a=1) | 79.4 ± 0.5 | +9.5 ± 0.8 | 19.5 / 20.0 / 39.9 | 0.885 | 1.91 | 100% | 0.57 | 10 |
| Global-CW OSCAR | 78.2 ± 0.2 | +7.8 ± 0.3 | 19.2 / 19.2 / 39.8 | 0.878 | 1.90 | 100% | 0.58 | 10 |
| Independent OSCAR | 62.0 ± 0.3 | -14.6 ± 0.3 | 16.3 / 6.3 / 39.3 | 0.692 | 0.63 | 0% | 0.71 | 10 |
| PF learner | 80.2 ± 0.1 | +10.6 ± 0.4 | 17.7 / 22.3 / 40.2 | 0.883 | 1.77 | 100% | 0.56 | 10 |
