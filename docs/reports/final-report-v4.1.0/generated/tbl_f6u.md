Table: cell f6u (mentor 6 unsaturated), stations per AP 10,10,10,10. Goodput in the second half of each 60 s run, mean ± 95% CI over evaluation seeds 400-409. Learners are averaged over three training seeds per evaluation seed. a = the alpha of the alpha-fair utility used to pick or tune the controller (0: total goodput, 1: proportional fairness).
| Controller | Total goodput (Mbit/s) | Δ vs BEB (%) | Per AP (Mbit/s) | Jain (per station) | Worst station (Mbit/s) | Floor met | PHY loss | Runs |
|---|---|---|---|---|---|---|---|---|
| BEB (802.11) | 25.0 ± 0.0 | – | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.71 | 10 |
| BEB + RTS/CTS | 21.1 ± 0.0 | -15.5 ± 0.1 | 2.5 / 4.8 / 6.8 / 7.1 | 0.891 | 0.25 | 90% | 0.84 | 10 |
| DAC | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.56 | 10 |
| BLADE | 24.1 ± 0.0 | -3.7 ± 0.1 | 2.3 / 4.8 / 7.2 / 9.8 | 0.824 | 0.23 | 0% | 0.71 | 10 |
| IdleSense | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.63 | 10 |
| KW (online) | 25.0 ± 0.0 | -0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.63 | 10 |
| Static, Patras model | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.66 | 10 |
| Static, proportional | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.54 | 10 |
| Static, common (a=0) | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.54 | 10 |
| Static, common (a=1) | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.54 | 10 |
| Central search (a=0) | 25.0 ± 0.0 | -0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.66 | 10 |
| Central search (a=1) | 24.9 ± 0.1 | -0.4 ± 0.5 | 2.5 / 5.0 / 7.5 / 9.9 | 0.834 | 0.25 | 100% | 0.66 | 10 |
| Global-CW OSCAR | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.64 | 10 |
| Independent OSCAR | 24.5 ± 0.0 | -1.9 ± 0.2 | 2.4 / 4.9 / 7.5 / 9.7 | 0.834 | 0.24 | 100% | 0.69 | 10 |
| PF learner | 25.0 ± 0.0 | +0.0 ± 0.0 | 2.5 / 5.0 / 7.5 / 10.0 | 0.833 | 0.25 | 100% | 0.59 | 10 |
