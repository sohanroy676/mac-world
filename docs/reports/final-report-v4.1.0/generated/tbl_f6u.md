Table: cell f6u (mentor 6 unsaturated), stations per AP 10,10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed.
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Seeds |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 25.0 ± 0.0 | – | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.71 | 5 |
| BEB + RTS/CTS | 21.1 ± 0.1 | -15.5 ± 0.3 | 2.5 / 4.8 / 6.8 / 7.1 | 0.890 | 0.25 | 80% | 0.84 | 5 |
| DAC | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.56 | 5 |
| BLADE | 24.1 ± 0.0 | -3.7 ± 0.1 | 2.3 / 4.8 / 7.2 / 9.8 | 0.825 | 0.23 | 0% | 0.71 | 5 |
| IdleSense | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.63 | 5 |
| KW (online) | 25.0 ± 0.0 | -0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.63 | 5 |
| Static, model (Patras) | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.66 | 5 |
| Static, proportional | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.54 | 5 |
| Static, common best (alpha 0) | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.54 | 5 |
| Static, common best (alpha 1) | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.54 | 5 |
| Central online search (alpha 0) | 25.0 ± 0.0 | -0.0 ± 0.1 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.67 | 5 |
| Central online search (alpha 1) | 24.9 ± 0.1 | -0.2 ± 0.6 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.66 | 5 |
| Global-CW OSCAR (central actor) | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.64 | 5 |
| Independent per-AP OSCAR | 24.6 ± 0.1 | -1.7 ± 0.1 | 2.4 / 4.9 / 7.5 / 9.8 | 0.833 | 0.24 | 100% | 0.68 | 5 |
| Independent PF learner | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.59 | 5 |
