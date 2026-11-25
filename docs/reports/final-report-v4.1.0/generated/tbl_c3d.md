Table: cell c3d (mentor 3D), stations per AP 20,20,20,20. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 25.8 ± 0.6 | – | 6.5 / 7.1 / 6.4 / 5.9 | 0.978 | 0.25 | 20% | 0.76 | 5 |
| BEB + RTS/CTS | 18.1 ± 0.0 | -30.1 ± 1.7 | 4.1 / 4.9 / 4.9 / 4.1 | 0.992 | 0.20 | 0% | 0.86 | 5 |
| DAC | 39.5 ± 0.5 | +52.7 ± 4.1 | 10.2 / 10.9 / 9.4 / 9.0 | 0.976 | 0.38 | 80% | 0.62 | 5 |
| BLADE | 37.6 ± 0.8 | +45.5 ± 5.5 | 9.6 / 9.5 / 9.4 / 9.1 | 0.988 | 0.40 | 100% | 0.54 | 5 |
| IdleSense | 38.9 ± 0.5 | +50.4 ± 4.5 | 9.8 / 9.7 / 10.1 / 9.2 | 0.992 | 0.43 | 100% | 0.56 | 5 |
| KW (online) | 19.7 ± 2.1 | -23.6 ± 6.9 | 4.8 / 5.0 / 5.2 / 4.8 | 0.993 | 0.22 | 0% | 0.86 | 5 |
| Static, model (Patras) | 28.7 ± 0.4 | +10.9 ± 3.6 | 6.9 / 7.4 / 7.4 / 6.9 | 0.997 | 0.33 | 100% | 0.73 | 5 |
| Static, proportional | 39.6 ± 0.1 | +53.2 ± 3.5 | 9.8 / 10.0 / 10.0 / 9.8 | 1.000 | 0.49 | 100% | 0.57 | 5 |
| Static, common best (alpha 0) | 39.6 ± 0.1 | +53.2 ± 3.5 | 9.8 / 10.0 / 10.0 / 9.8 | 1.000 | 0.49 | 100% | 0.57 | 5 |
| Static, common best (alpha 1) | 39.6 ± 0.1 | +53.2 ± 3.5 | 9.8 / 10.0 / 10.0 / 9.8 | 1.000 | 0.49 | 100% | 0.57 | 5 |
| Central online search (alpha 0) | 39.2 ± 0.6 | +51.8 ± 4.7 | 10.0 / 9.7 / 9.9 / 9.6 | 0.965 | 0.39 | 100% | 0.62 | 5 |
| Central online search (alpha 1) | 39.2 ± 0.6 | +51.8 ± 4.9 | 9.3 / 10.6 / 9.4 / 9.9 | 0.989 | 0.43 | 100% | 0.59 | 5 |
| Global-CW OSCAR (central actor) | 38.8 ± 0.5 | +49.7 ± 8.0 | 9.9 / 9.9 / 9.7 / 9.3 | 0.991 | 0.42 | 100% | 0.55 | 5 |
| Independent per-AP OSCAR | 7.0 ± 1.5 | -69.6 ± 4.1 | 1.5 / 0.2 / 3.2 / 2.1 | 0.715 | 0.01 | 0% | 0.96 | 5 |
| Independent PF learner | 37.9 ± 0.6 | +45.8 ± 7.9 | 8.9 / 8.9 / 8.7 / 11.3 | 0.980 | 0.41 | 100% | 0.54 | 5 |
