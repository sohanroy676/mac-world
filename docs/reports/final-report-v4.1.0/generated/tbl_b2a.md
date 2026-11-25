Table: cell b2a (mentor 2A), stations per AP 10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 72.4 ± 0.4 | – | 17.5 / 17.1 / 37.7 | 0.862 | 1.69 | 80% | 0.64 | 5 |
| BEB + RTS/CTS | 50.4 ± 0.1 | -30.4 ± 0.4 | 12.0 / 12.1 / 26.2 | 0.865 | 1.20 | 0% | 0.80 | 5 |
| DAC | 79.8 ± 0.1 | +10.2 ± 0.8 | 20.9 / 19.1 / 39.8 | 0.888 | 1.87 | 100% | 0.55 | 5 |
| BLADE | 72.9 ± 0.0 | +0.7 ± 0.6 | 18.5 / 18.1 / 36.3 | 0.891 | 1.81 | 100% | 0.53 | 5 |
| IdleSense | 75.1 ± 0.1 | +3.7 ± 0.7 | 19.2 / 18.7 / 37.2 | 0.894 | 1.87 | 100% | 0.53 | 5 |
| KW (online) | 79.9 ± 0.0 | +10.4 ± 0.7 | 19.9 / 20.1 / 40.0 | 0.889 | 1.98 | 100% | 0.56 | 5 |
| Static, model (Patras) | 77.5 ± 0.5 | +7.1 ± 0.9 | 18.4 / 18.8 / 40.2 | 0.866 | 1.83 | 100% | 0.59 | 5 |
| Static, proportional | 78.9 ± 0.1 | +9.0 ± 0.5 | 20.1 / 20.1 / 38.7 | 0.899 | 2.01 | 100% | 0.55 | 5 |
| Static, common best (alpha 0) | 78.9 ± 0.1 | +9.0 ± 0.5 | 20.1 / 20.1 / 38.7 | 0.899 | 2.01 | 100% | 0.55 | 5 |
| Static, common best (alpha 1) | 78.9 ± 0.1 | +9.0 ± 0.5 | 20.1 / 20.1 / 38.7 | 0.899 | 2.01 | 100% | 0.55 | 5 |
| Central online search (alpha 0) | 77.6 ± 3.8 | +7.2 ± 5.2 | 18.3 / 19.4 / 39.9 | 0.869 | 1.80 | 80% | 0.58 | 5 |
| Central online search (alpha 1) | 79.3 ± 1.2 | +9.5 ± 1.8 | 18.8 / 20.5 / 40.0 | 0.882 | 1.87 | 100% | 0.58 | 5 |
| Global-CW OSCAR (central actor) | 78.1 ± 0.1 | +8.1 ± 1.6 | 19.4 / 19.0 / 39.8 | 0.878 | 1.89 | 100% | 0.58 | 5 |
| Independent per-AP OSCAR | 61.9 ± 0.4 | -14.3 ± 1.2 | 16.4 / 6.3 / 39.2 | 0.691 | 0.63 | 0% | 0.71 | 5 |
| Independent PF learner | 80.2 ± 0.1 | +10.9 ± 1.5 | 18.0 / 22.0 / 40.2 | 0.884 | 1.80 | 100% | 0.56 | 5 |
