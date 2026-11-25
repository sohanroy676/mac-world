Table: cell b2c (mentor 2C), stations per AP 15,15,15. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 69.1 ± 0.8 | – | 33.9 / 1.2 / 34.1 | 0.689 | 0.08 | 40% | 0.65 | 5 |
| BEB + RTS/CTS | 48.8 ± 0.1 | -29.4 ± 0.8 | 24.1 / 0.5 / 24.2 | 0.680 | 0.03 | 0% | 0.81 | 5 |
| DAC | 77.4 ± 0.3 | +12.0 ± 1.5 | 37.9 / 1.5 / 37.9 | 0.693 | 0.10 | 100% | 0.55 | 5 |
| BLADE | 70.4 ± 0.2 | +1.9 ± 1.3 | 34.1 / 2.2 / 34.1 | 0.709 | 0.15 | 100% | 0.53 | 5 |
| IdleSense | 73.7 ± 0.3 | +6.7 ± 1.1 | 36.3 / 1.3 / 36.2 | 0.690 | 0.08 | 20% | 0.53 | 5 |
| KW (online) | 55.5 ± 2.4 | -19.8 ± 3.9 | 23.5 / 8.9 / 23.0 | 0.882 | 0.60 | 100% | 0.60 | 5 |
| Static, model (Patras) | 77.2 ± 0.6 | +11.8 ± 1.2 | 37.6 / 2.0 / 37.6 | 0.701 | 0.13 | 100% | 0.57 | 5 |
| Static, proportional | 68.9 ± 0.2 | -0.4 ± 1.4 | 31.3 / 6.3 / 31.3 | 0.792 | 0.42 | 100% | 0.53 | 5 |
| Static, common best (alpha 0) | 76.1 ± 0.7 | +10.1 ± 1.5 | 36.6 / 3.0 / 36.6 | 0.719 | 0.20 | 100% | 0.56 | 5 |
| Static, common best (alpha 1) | 68.9 ± 0.2 | -0.4 ± 1.4 | 31.3 / 6.3 / 31.3 | 0.792 | 0.42 | 100% | 0.53 | 5 |
| Central online search (alpha 0) | 76.1 ± 1.4 | +10.1 ± 2.6 | 37.2 / 2.0 / 36.8 | 0.703 | 0.14 | 100% | 0.58 | 5 |
| Central online search (alpha 1) | 66.0 ± 6.3 | -4.5 ± 9.5 | 29.1 / 8.0 / 28.9 | 0.833 | 0.53 | 100% | 0.58 | 5 |
| Global-CW OSCAR (central actor) | 75.9 ± 1.0 | +9.5 ± 1.1 | 36.7 / 2.6 / 36.7 | 0.713 | 0.17 | 100% | 0.57 | 5 |
| Independent per-AP OSCAR | 64.7 ± 2.8 | -8.3 ± 3.6 | 30.5 / 4.1 / 30.1 | 0.753 | 0.27 | 100% | 0.63 | 5 |
| Independent PF learner | 65.3 ± 0.7 | -5.7 ± 1.7 | 29.3 / 6.7 / 29.3 | 0.807 | 0.45 | 100% | 0.53 | 5 |
