Table: cell d4c (mentor 4C), stations per AP 5,15,25,35. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 25.2 ± 1.1 | – | 1.9 / 5.2 / 8.3 / 9.9 | 0.983 | 0.28 | 40% | 0.77 | 5 |
| BEB + RTS/CTS | 17.8 ± 0.1 | -29.3 ± 3.5 | 1.2 / 3.5 / 5.9 / 7.2 | 0.994 | 0.20 | 0% | 0.87 | 5 |
| DAC | 39.3 ± 0.4 | +55.9 ± 7.0 | 3.2 / 7.8 / 12.9 / 15.4 | 0.979 | 0.44 | 100% | 0.62 | 5 |
| BLADE | 37.8 ± 0.3 | +49.8 ± 7.6 | 2.5 / 7.3 / 12.0 / 15.9 | 0.992 | 0.42 | 100% | 0.54 | 5 |
| IdleSense | 38.8 ± 0.2 | +54.0 ± 6.0 | 2.6 / 7.6 / 12.4 / 16.2 | 0.992 | 0.43 | 100% | 0.56 | 5 |
| KW (online) | 17.9 ± 2.2 | -29.0 ± 9.2 | 3.4 / 4.3 / 5.2 / 4.9 | 0.717 | 0.14 | 0% | 0.88 | 5 |
| Static, model (Patras) | 32.1 ± 0.9 | +27.2 ± 5.9 | 9.6 / 10.2 / 7.5 / 4.8 | 0.542 | 0.14 | 0% | 0.69 | 5 |
| Static, proportional | 39.9 ± 0.0 | +58.2 ± 7.2 | 12.0 / 12.4 / 10.0 / 5.4 | 0.540 | 0.15 | 0% | 0.56 | 5 |
| Static, common best (alpha 0) | 39.5 ± 0.1 | +56.6 ± 6.9 | 2.6 / 7.8 / 13.0 / 16.2 | 0.996 | 0.46 | 100% | 0.57 | 5 |
| Static, common best (alpha 1) | 39.5 ± 0.1 | +56.6 ± 6.9 | 2.6 / 7.8 / 13.0 / 16.2 | 0.996 | 0.46 | 100% | 0.57 | 5 |
| Central online search (alpha 0) | 38.8 ± 1.3 | +53.9 ± 2.9 | 5.3 / 8.5 / 12.0 / 13.1 | 0.828 | 0.37 | 100% | 0.63 | 5 |
| Central online search (alpha 1) | 39.1 ± 0.5 | +55.0 ± 6.9 | 2.9 / 7.4 / 12.5 / 16.3 | 0.980 | 0.45 | 100% | 0.60 | 5 |
| Global-CW OSCAR (central actor) | 38.6 ± 0.4 | +55.4 ± 12.4 | 2.6 / 7.6 / 12.7 / 15.8 | 0.991 | 0.42 | 100% | 0.57 | 5 |
| Independent per-AP OSCAR | 11.6 ± 0.4 | -53.1 ± 6.5 | 3.0 / 1.3 / 5.1 / 2.1 | 0.551 | 0.06 | 0% | 0.92 | 5 |
| Independent PF learner | 39.0 ± 0.3 | +57.1 ± 15.1 | 9.8 / 8.4 / 9.6 / 11.2 | 0.592 | 0.32 | 80% | 0.55 | 5 |
