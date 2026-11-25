Table: cell b2b (mentor 2B), stations per AP 10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 72.6 ± 0.5 | – | 37.9 / 17.3 / 17.4 | 0.862 | 1.72 | 100% | 0.64 | 5 |
| BEB + RTS/CTS | 50.3 ± 0.1 | -30.7 ± 0.5 | 26.2 / 12.1 / 12.0 | 0.865 | 1.19 | 0% | 0.80 | 5 |
| DAC | 79.9 ± 0.1 | +10.0 ± 0.8 | 39.9 / 19.9 / 20.0 | 0.887 | 1.89 | 100% | 0.55 | 5 |
| BLADE | 72.9 ± 0.0 | +0.3 ± 0.8 | 36.3 / 18.3 / 18.3 | 0.892 | 1.83 | 100% | 0.53 | 5 |
| IdleSense | 75.1 ± 0.1 | +3.4 ± 0.8 | 37.2 / 18.9 / 19.0 | 0.895 | 1.89 | 100% | 0.53 | 5 |
| KW (online) | 79.9 ± 0.4 | +10.0 ± 0.8 | 39.9 / 19.8 / 20.2 | 0.890 | 1.98 | 100% | 0.56 | 5 |
| Static, model (Patras) | 78.4 ± 0.7 | +7.9 ± 1.2 | 40.2 / 19.3 / 18.8 | 0.872 | 1.86 | 100% | 0.59 | 5 |
| Static, proportional | 78.8 ± 0.1 | +8.5 ± 0.9 | 38.7 / 20.1 / 20.0 | 0.899 | 2.00 | 100% | 0.55 | 5 |
| Static, common best (alpha 0) | 78.8 ± 0.1 | +8.5 ± 0.9 | 38.7 / 20.1 / 20.0 | 0.899 | 2.00 | 100% | 0.55 | 5 |
| Static, common best (alpha 1) | 78.8 ± 0.1 | +8.5 ± 0.9 | 38.7 / 20.1 / 20.0 | 0.899 | 2.00 | 100% | 0.55 | 5 |
| Central online search (alpha 0) | 78.4 ± 3.5 | +8.0 ± 4.3 | 39.9 / 19.6 / 19.0 | 0.877 | 1.88 | 100% | 0.58 | 5 |
| Central online search (alpha 1) | 79.7 ± 0.6 | +9.7 ± 1.1 | 39.8 / 20.1 / 19.7 | 0.889 | 1.96 | 100% | 0.57 | 5 |
| Global-CW OSCAR (central actor) | 72.0 ± 0.4 | -0.6 ± 1.7 | 34.6 / 18.8 / 18.5 | 0.911 | 1.85 | 100% | 0.55 | 5 |
| Independent per-AP OSCAR | 63.8 ± 0.3 | -12.3 ± 1.3 | 39.9 / 12.3 / 11.6 | 0.722 | 1.16 | 0% | 0.69 | 5 |
| Independent PF learner | 79.1 ± 0.2 | +8.9 ± 2.1 | 39.7 / 19.8 / 19.6 | 0.887 | 1.94 | 100% | 0.56 | 5 |
