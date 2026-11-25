Table: cell c3c (mentor 3C), stations per AP 10,10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 30.7 ± 0.5 | – | 7.3 / 8.0 / 8.2 / 7.2 | 0.992 | 0.69 | 60% | 0.70 | 5 |
| BEB + RTS/CTS | 21.6 ± 0.1 | -29.6 ± 1.2 | 4.9 / 5.9 / 6.0 / 4.8 | 0.988 | 0.48 | 0% | 0.83 | 5 |
| DAC | 40.0 ± 0.1 | +30.3 ± 2.4 | 9.4 / 10.7 / 10.8 / 9.1 | 0.991 | 0.89 | 100% | 0.56 | 5 |
| BLADE | 36.8 ± 0.1 | +20.1 ± 2.1 | 9.5 / 8.9 / 9.2 / 9.3 | 0.995 | 0.83 | 100% | 0.53 | 5 |
| IdleSense | 38.3 ± 0.1 | +24.9 ± 2.4 | 9.9 / 9.3 / 9.5 / 9.6 | 0.995 | 0.86 | 100% | 0.54 | 5 |
| KW (online) | 30.5 ± 3.0 | -0.6 ± 10.0 | 7.2 / 7.6 / 7.6 / 8.0 | 0.989 | 0.65 | 20% | 0.68 | 5 |
| Static, model (Patras) | 30.2 ± 0.4 | -1.7 ± 2.2 | 7.2 / 8.1 / 8.1 / 6.8 | 0.992 | 0.66 | 20% | 0.71 | 5 |
| Static, proportional | 40.0 ± 0.0 | +30.6 ± 2.1 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Static, common best (alpha 0) | 40.0 ± 0.0 | +30.6 ± 2.1 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Static, common best (alpha 1) | 40.0 ± 0.0 | +30.6 ± 2.1 | 9.9 / 10.1 / 10.1 / 9.9 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Central online search (alpha 0) | 39.8 ± 0.3 | +29.7 ± 1.3 | 9.2 / 10.2 / 10.4 / 10.0 | 0.980 | 0.84 | 100% | 0.59 | 5 |
| Central online search (alpha 1) | 39.4 ± 1.2 | +28.4 ± 5.2 | 9.7 / 10.2 / 10.1 / 9.4 | 0.993 | 0.88 | 100% | 0.59 | 5 |
| Global-CW OSCAR (central actor) | 39.9 ± 0.1 | +29.7 ± 3.2 | 10.0 / 10.1 / 9.7 / 10.2 | 0.996 | 0.90 | 100% | 0.55 | 5 |
| Independent per-AP OSCAR | 11.3 ± 0.4 | -63.0 ± 2.1 | 3.4 / 2.6 / 1.9 / 3.5 | 0.947 | 0.19 | 0% | 0.93 | 5 |
| Independent PF learner | 38.8 ± 0.1 | +26.1 ± 3.5 | 10.3 / 8.1 / 8.9 / 11.4 | 0.980 | 0.80 | 80% | 0.54 | 5 |
