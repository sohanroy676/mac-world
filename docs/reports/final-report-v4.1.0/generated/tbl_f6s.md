Table: cell f6s (mentor 6 saturated), stations per AP 10,10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 30.7 ± 0.2 | – | 7.3 / 8.3 / 8.1 / 6.9 | 0.993 | 0.69 | 100% | 0.70 | 5 |
| BEB + RTS/CTS | 21.7 ± 0.1 | -29.3 ± 0.4 | 4.8 / 6.0 / 6.0 / 4.8 | 0.987 | 0.47 | 0% | 0.83 | 5 |
| DAC | 39.9 ± 0.0 | +30.2 ± 0.9 | 9.7 / 11.1 / 10.3 / 8.8 | 0.991 | 0.88 | 100% | 0.56 | 5 |
| BLADE | 36.8 ± 0.1 | +20.2 ± 0.9 | 9.4 / 9.3 / 9.1 / 9.0 | 0.999 | 0.88 | 100% | 0.53 | 5 |
| IdleSense | 38.4 ± 0.1 | +25.2 ± 1.0 | 9.8 / 9.7 / 9.5 / 9.4 | 0.999 | 0.92 | 100% | 0.54 | 5 |
| KW (online) | 33.0 ± 3.0 | +7.6 ± 9.2 | 8.9 / 7.8 / 8.5 / 7.9 | 0.984 | 0.72 | 40% | 0.67 | 5 |
| Static, model (Patras) | 29.8 ± 0.4 | -2.8 ± 2.1 | 7.2 / 7.9 / 7.6 / 7.1 | 0.996 | 0.68 | 60% | 0.71 | 5 |
| Static, proportional | 40.1 ± 0.1 | +30.8 ± 1.0 | 9.9 / 10.1 / 10.2 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Static, common best (alpha 0) | 40.1 ± 0.1 | +30.8 ± 1.0 | 9.9 / 10.1 / 10.2 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Static, common best (alpha 1) | 40.1 ± 0.1 | +30.8 ± 1.0 | 9.9 / 10.1 / 10.2 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Central online search (alpha 0) | 39.3 ± 1.1 | +28.2 ± 3.6 | 9.8 / 10.3 / 10.4 / 8.8 | 0.988 | 0.87 | 100% | 0.61 | 5 |
| Central online search (alpha 1) | 39.2 ± 1.0 | +27.8 ± 3.9 | 9.6 / 9.7 / 9.7 / 10.2 | 0.983 | 0.86 | 100% | 0.60 | 5 |
| Global-CW OSCAR (central actor) | 38.4 ± 0.1 | +25.8 ± 0.7 | 9.6 / 9.5 / 9.8 / 9.4 | 0.999 | 0.92 | 100% | 0.54 | 5 |
| Independent per-AP OSCAR | 9.7 ± 0.2 | -68.4 ± 1.8 | 2.5 / 2.2 / 2.3 / 2.7 | 0.991 | 0.22 | 0% | 0.94 | 5 |
| Independent PF learner | 39.0 ± 0.0 | +27.6 ± 0.7 | 10.7 / 7.3 / 11.9 / 9.1 | 0.969 | 0.73 | 80% | 0.55 | 5 |
