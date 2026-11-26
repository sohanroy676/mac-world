Table: cell b2b (mentor 2B), stations per AP 10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 72.7 ± 0.3 | – | 37.9 / 17.5 / 17.3 | 0.863 | 1.71 | 100% | 0.64 | 10 |
| BEB + RTS/CTS | 50.3 ± 0.0 | -30.8 ± 0.3 | 26.1 / 12.3 / 11.9 | 0.865 | 1.19 | 0% | 0.80 | 10 |
| DAC | 79.9 ± 0.1 | +9.8 ± 0.4 | 39.9 / 20.2 / 19.8 | 0.888 | 1.89 | 100% | 0.55 | 10 |
| BLADE | 72.9 ± 0.0 | +0.2 ± 0.4 | 36.3 / 18.4 / 18.2 | 0.892 | 1.82 | 100% | 0.53 | 10 |
| IdleSense | 75.1 ± 0.1 | +3.2 ± 0.4 | 37.2 / 19.0 / 18.9 | 0.894 | 1.88 | 100% | 0.53 | 10 |
| KW (online) | 80.0 ± 0.2 | +10.0 ± 0.4 | 40.0 / 20.0 / 20.1 | 0.889 | 1.98 | 100% | 0.56 | 10 |
| Static, Patras model | 78.2 ± 0.3 | +7.5 ± 0.6 | 40.2 / 19.0 / 18.9 | 0.871 | 1.86 | 100% | 0.59 | 10 |
| Static, proportional | 78.8 ± 0.0 | +8.4 ± 0.4 | 38.7 / 20.1 / 20.0 | 0.899 | 2.00 | 100% | 0.55 | 10 |
| Static, common (a=0) | 78.8 ± 0.0 | +8.4 ± 0.4 | 38.7 / 20.1 / 20.0 | 0.899 | 2.00 | 100% | 0.55 | 10 |
| Static, common (a=1) | 78.8 ± 0.0 | +8.4 ± 0.4 | 38.7 / 20.1 / 20.0 | 0.899 | 2.00 | 100% | 0.55 | 10 |
| Central search (a=0) | 79.1 ± 1.5 | +8.8 ± 1.8 | 40.0 / 20.0 / 19.2 | 0.882 | 1.91 | 100% | 0.57 | 10 |
| Central search (a=1) | 79.6 ± 0.3 | +9.4 ± 0.5 | 39.8 / 20.0 / 19.9 | 0.889 | 1.96 | 100% | 0.57 | 10 |
| Global-CW OSCAR | 72.1 ± 0.2 | -0.9 ± 0.5 | 34.7 / 18.8 / 18.6 | 0.910 | 1.86 | 100% | 0.55 | 10 |
| Independent OSCAR | 63.8 ± 0.1 | -12.4 ± 0.3 | 39.9 / 12.2 / 11.6 | 0.721 | 1.16 | 0% | 0.69 | 10 |
| PF learner | 79.2 ± 0.1 | +8.8 ± 0.5 | 39.7 / 19.7 / 19.7 | 0.886 | 1.95 | 100% | 0.56 | 10 |
