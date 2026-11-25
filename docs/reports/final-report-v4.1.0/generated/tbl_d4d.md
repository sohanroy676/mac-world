Table: cell d4d (mentor 4D), stations per AP 40,20,10,5. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 26.5 ± 0.4 | – | 12.0 / 8.3 / 4.3 / 1.8 | 0.973 | 0.28 | 80% | 0.75 | 5 |
| BEB + RTS/CTS | 18.2 ± 0.1 | -31.4 ± 1.3 | 8.7 / 5.4 / 2.7 / 1.3 | 0.992 | 0.22 | 0% | 0.86 | 5 |
| DAC | 39.1 ± 0.7 | +47.6 ± 3.8 | 18.2 / 11.6 / 6.3 / 2.9 | 0.982 | 0.45 | 100% | 0.57 | 5 |
| BLADE | 37.4 ± 0.4 | +41.1 ± 2.3 | 19.0 / 10.5 / 5.3 / 2.6 | 0.989 | 0.43 | 80% | 0.54 | 5 |
| IdleSense | 38.7 ± 0.4 | +46.1 ± 1.8 | 19.7 / 10.8 / 5.5 / 2.6 | 0.989 | 0.45 | 100% | 0.56 | 5 |
| KW (online) | 20.8 ± 1.3 | -21.5 ± 5.2 | 6.7 / 5.6 / 4.7 / 3.8 | 0.774 | 0.17 | 0% | 0.83 | 5 |
| Static, model (Patras) | 32.2 ± 0.3 | +21.5 ± 2.1 | 3.7 / 9.2 / 10.0 / 9.2 | 0.624 | 0.09 | 0% | 0.69 | 5 |
| Static, proportional | 39.9 ± 0.1 | +50.9 ± 2.5 | 4.3 / 11.9 / 12.0 / 11.7 | 0.617 | 0.11 | 0% | 0.55 | 5 |
| Static, common best (alpha 0) | 39.6 ± 0.1 | +49.7 ± 2.7 | 19.2 / 11.7 / 5.8 / 2.9 | 0.992 | 0.48 | 100% | 0.56 | 5 |
| Static, common best (alpha 1) | 39.6 ± 0.1 | +49.7 ± 2.7 | 19.2 / 11.7 / 5.8 / 2.9 | 0.992 | 0.48 | 100% | 0.56 | 5 |
| Central online search (alpha 0) | 39.3 ± 0.3 | +48.6 ± 2.2 | 18.3 / 10.4 / 6.6 / 4.0 | 0.909 | 0.44 | 100% | 0.62 | 5 |
| Central online search (alpha 1) | 39.2 ± 0.4 | +48.1 ± 1.4 | 19.4 / 12.0 / 5.0 / 2.8 | 0.969 | 0.43 | 100% | 0.59 | 5 |
| Global-CW OSCAR (central actor) | 38.4 ± 0.3 | +44.6 ± 3.7 | 19.1 / 11.2 / 5.6 / 2.5 | 0.987 | 0.44 | 80% | 0.55 | 5 |
| Independent per-AP OSCAR | 9.5 ± 1.3 | -66.0 ± 4.3 | 1.0 / 1.2 / 4.1 / 3.2 | 0.548 | 0.02 | 0% | 0.92 | 5 |
| Independent PF learner | 39.6 ± 0.3 | +48.8 ± 2.0 | 11.4 / 6.1 / 11.6 / 10.5 | 0.624 | 0.28 | 0% | 0.56 | 5 |
