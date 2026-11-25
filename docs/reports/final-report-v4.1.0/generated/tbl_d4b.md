Table: cell d4b (mentor 4B), stations per AP 10,20,30,40. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 24.6 ± 1.1 | – | 3.2 / 5.8 / 7.8 / 7.7 | 0.954 | 0.18 | 40% | 0.78 | 5 |
| BEB + RTS/CTS | 16.6 ± 0.1 | -32.2 ± 3.0 | 1.8 / 3.6 / 5.3 / 6.0 | 0.995 | 0.15 | 0% | 0.88 | 5 |
| DAC | 39.2 ± 0.4 | +57.7 ± 6.3 | 5.2 / 8.6 / 12.3 / 13.1 | 0.949 | 0.26 | 100% | 0.73 | 4 |
| BLADE | 38.4 ± 0.4 | +56.4 ± 8.4 | 4.5 / 8.8 / 11.8 / 13.3 | 0.966 | 0.29 | 100% | 0.54 | 5 |
| IdleSense | 39.1 ± 0.2 | +59.5 ± 6.9 | 4.6 / 9.0 / 12.1 / 13.5 | 0.966 | 0.30 | 100% | 0.56 | 5 |
| KW (online) | 15.9 ± 2.9 | -35.3 ± 11.2 | 3.6 / 3.5 / 4.4 / 4.4 | 0.800 | 0.11 | 0% | 0.91 | 5 |
| Static, model (Patras) | 33.0 ± 0.5 | +34.4 ± 5.0 | 11.0 / 10.9 / 6.9 / 4.1 | 0.624 | 0.10 | 0% | 0.67 | 5 |
| Static, proportional | 39.8 ± 0.1 | +62.0 ± 6.9 | 13.7 / 13.7 / 8.4 / 4.1 | 0.610 | 0.10 | 0% | 0.57 | 5 |
| Static, common best (alpha 0) | 39.3 ± 0.2 | +60.0 ± 6.5 | 4.5 / 9.1 / 13.0 / 12.6 | 0.978 | 0.32 | 100% | 0.58 | 5 |
| Static, common best (alpha 1) | 39.3 ± 0.2 | +60.0 ± 6.5 | 4.5 / 9.1 / 13.0 / 12.6 | 0.978 | 0.32 | 100% | 0.58 | 5 |
| Central online search (alpha 0) | 38.8 ± 1.4 | +58.3 ± 8.0 | 5.0 / 9.5 / 12.8 / 11.6 | 0.916 | 0.29 | 100% | 0.63 | 5 |
| Central online search (alpha 1) | 39.1 ± 0.6 | +59.2 ± 4.6 | 4.5 / 7.4 / 12.0 / 15.3 | 0.991 | 0.36 | 100% | 0.60 | 5 |
| Global-CW OSCAR (central actor) | 38.7 ± 0.5 | +59.1 ± 22.3 | 4.5 / 8.7 / 12.2 / 13.3 | 0.975 | 0.31 | 100% | 0.54 | 5 |
| Independent per-AP OSCAR | 5.7 ± 1.1 | -76.1 ± 9.6 | 2.2 / 2.7 / 0.7 / 0.2 | 0.539 | 0.00 | 0% | 0.97 | 5 |
| Independent PF learner | 38.0 ± 0.2 | +56.0 ± 16.1 | 9.8 / 8.4 / 11.4 / 8.4 | 0.744 | 0.21 | 60% | 0.58 | 5 |
