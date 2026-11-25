Table: cell a1c (mentor 1C), stations per AP 20,20. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 30.2 ± 0.3 | – | 14.9 / 15.3 | 0.999 | 0.74 | 100% | 0.71 | 5 |
| BEB + RTS/CTS | 21.1 ± 0.0 | -30.2 ± 0.7 | 10.5 / 10.6 | 1.000 | 0.53 | 0% | 0.84 | 5 |
| DAC | 39.5 ± 0.1 | +30.7 ± 1.3 | 19.9 / 19.6 | 0.999 | 0.96 | 100% | 0.56 | 5 |
| BLADE | 36.9 ± 0.1 | +22.1 ± 1.4 | 18.4 / 18.5 | 0.999 | 0.91 | 100% | 0.53 | 5 |
| IdleSense | 38.2 ± 0.1 | +26.4 ± 1.6 | 19.0 / 19.2 | 0.999 | 0.94 | 100% | 0.54 | 5 |
| KW (online) | 37.2 ± 1.8 | +23.2 ± 5.0 | 18.5 / 18.7 | 1.000 | 0.92 | 100% | 0.59 | 5 |
| Static, model (Patras) | 35.6 ± 0.6 | +18.0 ± 2.6 | 17.8 / 17.8 | 1.000 | 0.89 | 100% | 0.63 | 5 |
| Static, proportional | 39.6 ± 0.1 | +31.1 ± 1.3 | 19.8 / 19.8 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Static, common best (alpha 0) | 39.6 ± 0.1 | +31.1 ± 1.3 | 19.8 / 19.8 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Static, common best (alpha 1) | 39.6 ± 0.1 | +31.1 ± 1.3 | 19.8 / 19.8 | 1.000 | 0.99 | 100% | 0.57 | 5 |
| Central online search (alpha 0) | 39.0 ± 1.5 | +29.1 ± 6.2 | 18.4 / 20.6 | 0.994 | 0.92 | 100% | 0.61 | 5 |
| Central online search (alpha 1) | 38.7 ± 2.2 | +28.0 ± 8.5 | 19.9 / 18.7 | 0.998 | 0.94 | 100% | 0.60 | 5 |
| Global-CW OSCAR (central actor) | 38.2 ± 0.1 | +26.0 ± 3.1 | 18.9 / 19.4 | 0.999 | 0.93 | 100% | 0.55 | 5 |
| Independent per-AP OSCAR | 16.4 ± 0.9 | -45.0 ± 5.6 | 11.3 / 5.1 | 0.872 | 0.25 | 0% | 0.87 | 5 |
| Independent PF learner | 39.6 ± 0.1 | +30.5 ± 3.6 | 19.2 / 20.4 | 0.998 | 0.96 | 100% | 0.55 | 5 |
