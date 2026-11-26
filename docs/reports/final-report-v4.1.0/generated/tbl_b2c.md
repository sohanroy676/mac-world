Table: cell b2c (mentor 2C), stations per AP 15,15,15. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 69.4 ± 0.5 | – | 34.1 / 1.1 / 34.2 | 0.687 | 0.07 | 22% | 0.65 | 9 |
| BEB + RTS/CTS | 48.8 ± 0.1 | -29.6 ± 0.4 | 24.2 / 0.4 / 24.2 | 0.679 | 0.03 | 0% | 0.81 | 10 |
| DAC | 77.5 ± 0.2 | +11.7 ± 0.8 | 38.0 / 1.4 / 38.0 | 0.692 | 0.10 | 70% | 0.55 | 10 |
| BLADE | 70.7 ± 0.3 | +1.9 ± 0.7 | 34.4 / 2.0 / 34.4 | 0.704 | 0.13 | 90% | 0.53 | 10 |
| IdleSense | 73.8 ± 0.2 | +6.4 ± 0.6 | 36.3 / 1.2 / 36.3 | 0.689 | 0.08 | 20% | 0.53 | 10 |
| KW (online) | 56.0 ± 1.1 | -19.3 ± 1.8 | 23.9 / 8.5 / 23.6 | 0.870 | 0.57 | 100% | 0.60 | 10 |
| Static, Patras model | 77.3 ± 0.4 | +11.3 ± 0.8 | 37.7 / 1.9 / 37.7 | 0.700 | 0.13 | 100% | 0.57 | 10 |
| Static, proportional | 68.9 ± 0.1 | -0.7 ± 0.8 | 31.3 / 6.3 / 31.3 | 0.793 | 0.42 | 100% | 0.53 | 10 |
| Static, common (a=0) | 76.2 ± 0.4 | +9.7 ± 0.8 | 36.7 / 2.9 / 36.7 | 0.718 | 0.19 | 100% | 0.56 | 10 |
| Static, common (a=1) | 68.9 ± 0.1 | -0.7 ± 0.8 | 31.3 / 6.3 / 31.3 | 0.793 | 0.42 | 100% | 0.53 | 10 |
| Central search (a=0) | 76.5 ± 0.7 | +10.2 ± 1.2 | 37.4 / 1.9 / 37.2 | 0.701 | 0.13 | 100% | 0.57 | 10 |
| Central search (a=1) | 66.0 ± 2.6 | -4.7 ± 4.4 | 28.7 / 8.3 / 29.0 | 0.837 | 0.55 | 100% | 0.56 | 10 |
| Global-CW OSCAR | 75.9 ± 0.7 | +9.4 ± 0.8 | 36.6 / 2.6 / 36.6 | 0.714 | 0.18 | 100% | 0.57 | 10 |
| Independent OSCAR | 64.6 ± 2.2 | -6.6 ± 3.1 | 30.4 / 4.0 / 30.2 | 0.752 | 0.27 | 100% | 0.63 | 10 |
| PF learner | 65.3 ± 0.7 | -5.9 ± 1.1 | 29.3 / 6.7 / 29.3 | 0.806 | 0.44 | 100% | 0.53 | 10 |
