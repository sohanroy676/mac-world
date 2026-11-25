Table: cell c3a (mentor 3A), stations per AP 10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 32.3 ± 0.1 | – | 10.3 / 11.7 / 10.4 | 0.996 | 1.01 | 80% | 0.68 | 5 |
| BEB + RTS/CTS | 22.7 ± 0.1 | -29.8 ± 0.2 | 7.1 / 8.4 / 7.3 | 0.994 | 0.70 | 0% | 0.83 | 5 |
| DAC | 39.9 ± 0.0 | +23.4 ± 0.5 | 12.4 / 15.0 / 12.6 | 0.989 | 1.21 | 100% | 0.55 | 5 |
| BLADE | 36.8 ± 0.1 | +13.7 ± 0.6 | 12.0 / 12.4 / 12.4 | 0.999 | 1.20 | 100% | 0.53 | 5 |
| IdleSense | 38.0 ± 0.1 | +17.6 ± 0.6 | 12.5 / 12.8 / 12.8 | 0.999 | 1.24 | 100% | 0.54 | 5 |
| KW (online) | 38.6 ± 2.3 | +19.4 ± 6.7 | 12.7 / 13.1 / 12.9 | 0.998 | 1.24 | 100% | 0.58 | 5 |
| Static, model (Patras) | 33.8 ± 0.1 | +4.6 ± 0.5 | 11.1 / 11.7 / 10.9 | 0.999 | 1.09 | 100% | 0.66 | 5 |
| Static, proportional | 40.0 ± 0.1 | +23.7 ± 0.7 | 13.2 / 13.5 / 13.3 | 1.000 | 1.32 | 100% | 0.55 | 5 |
| Static, common best (alpha 0) | 40.0 ± 0.1 | +23.7 ± 0.7 | 13.2 / 13.5 / 13.3 | 1.000 | 1.32 | 100% | 0.55 | 5 |
| Static, common best (alpha 1) | 40.0 ± 0.1 | +23.7 ± 0.7 | 13.2 / 13.5 / 13.3 | 1.000 | 1.32 | 100% | 0.55 | 5 |
| Central online search (alpha 0) | 38.8 ± 1.0 | +19.8 ± 3.1 | 13.0 / 12.5 / 13.3 | 0.988 | 1.15 | 100% | 0.61 | 5 |
| Central online search (alpha 1) | 35.6 ± 2.8 | +10.2 ± 8.5 | 11.4 / 12.6 / 11.6 | 0.995 | 1.12 | 100% | 0.65 | 5 |
| Global-CW OSCAR (central actor) | 38.8 ± 0.1 | +20.2 ± 0.1 | 13.1 / 12.8 / 12.9 | 0.999 | 1.26 | 100% | 0.55 | 5 |
| Independent per-AP OSCAR | 14.7 ± 0.7 | -55.5 ± 0.3 | 3.2 / 5.5 / 6.0 | 0.941 | 0.32 | 0% | 0.89 | 5 |
| Independent PF learner | 40.1 ± 0.0 | +24.0 ± 0.2 | 11.3 / 16.4 / 12.4 | 0.973 | 1.13 | 100% | 0.56 | 5 |
