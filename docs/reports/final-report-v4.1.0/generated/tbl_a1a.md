Table: cell a1a (mentor 1A), stations per AP 10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 34.6 ± 0.3 | – | 17.5 / 17.1 | 0.999 | 1.69 | 80% | 0.66 | 5 |
| BEB + RTS/CTS | 24.2 ± 0.1 | -30.2 ± 0.7 | 12.0 / 12.1 | 1.000 | 1.20 | 0% | 0.81 | 5 |
| DAC | 40.0 ± 0.1 | +15.4 ± 1.1 | 20.9 / 19.1 | 0.995 | 1.87 | 100% | 0.55 | 5 |
| BLADE | 36.6 ± 0.0 | +5.7 ± 1.0 | 18.5 / 18.1 | 0.999 | 1.81 | 100% | 0.53 | 5 |
| IdleSense | 37.9 ± 0.0 | +9.4 ± 1.1 | 19.2 / 18.7 | 0.999 | 1.87 | 100% | 0.53 | 5 |
| KW (online) | 40.0 ± 0.0 | +15.6 ± 1.1 | 19.9 / 20.2 | 1.000 | 1.97 | 100% | 0.56 | 5 |
| Static, model (Patras) | 37.3 ± 0.4 | +7.7 ± 1.4 | 18.4 / 18.8 | 1.000 | 1.83 | 100% | 0.62 | 5 |
| Static, proportional | 40.1 ± 0.1 | +15.9 ± 0.9 | 20.1 / 20.1 | 1.000 | 2.01 | 100% | 0.57 | 5 |
| Static, common best (alpha 0) | 40.1 ± 0.1 | +15.9 ± 0.9 | 20.1 / 20.1 | 1.000 | 2.01 | 100% | 0.57 | 5 |
| Static, common best (alpha 1) | 40.1 ± 0.1 | +15.9 ± 0.9 | 20.1 / 20.1 | 1.000 | 2.01 | 100% | 0.57 | 5 |
| Central online search (alpha 0) | 39.1 ± 1.6 | +13.0 ± 5.0 | 19.6 / 19.6 | 0.997 | 1.89 | 100% | 0.59 | 5 |
| Central online search (alpha 1) | 38.4 ± 1.7 | +10.9 ± 5.6 | 19.2 / 19.2 | 0.998 | 1.85 | 100% | 0.60 | 5 |
| Global-CW OSCAR (central actor) | 40.1 ± 0.0 | +16.0 ± 2.4 | 20.3 / 19.8 | 0.999 | 1.98 | 100% | 0.56 | 5 |
| Independent per-AP OSCAR | 23.1 ± 0.4 | -32.9 ± 2.6 | 10.2 / 13.0 | 0.985 | 1.02 | 0% | 0.80 | 5 |
| Independent PF learner | 40.1 ± 0.0 | +16.1 ± 2.5 | 20.4 / 19.8 | 0.999 | 1.98 | 100% | 0.56 | 5 |
