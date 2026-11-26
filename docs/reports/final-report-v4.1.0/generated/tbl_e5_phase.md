Table: Scenario 5, adaptation metrics over the six phases (active stations per AP 10, 15, 20, 25, 15, 10; 20 s each). Dip = lowest 1 s goodput in the first 5 s after a change, relative to the previous phase's level (three joining steps, two leaving steps); recovery = seconds until goodput stays within 5% of the phase's second-half level; CW settling = seconds until the mean CW stays within 10% of its second-half level. Means over the five transitions and over evaluation seeds.
| Controller | Mean goodput (Mbit/s) | Dip when stations join (%) | Dip when stations leave (%) | Recovery (s) | CW settling (s) | Retry rate | Runs |
|---|---|---|---|---|---|---|---|
| BEB (802.11) | 28.8 | -7.0 | -21.5 | 2.0 | 0.0 | 0.604 | 10 |
| BEB + RTS/CTS | 20.5 | -6.7 | 0.0 | 0.8 | 0.0 | 0.333 | 10 |
| DAC | 37.8 | -0.8 | -34.2 | 2.0 | 6.0 | 0.202 | 10 |
| BLADE | 35.9 | 0.9 | -34.3 | 2.0 | 2.0 | 0.109 | 10 |
| IdleSense | 37.2 | 0.6 | -34.6 | 2.0 | 2.0 | 0.165 | 10 |
| KW (online) | 27.4 | -13.7 | -29.4 | 13.0 | 3.6 | 0.378 | 10 |
| Static, Patras model | 35.5 | -5.8 | -33.8 | 4.8 | 0.0 | 0.383 | 10 |
| Static, proportional | 37.3 | 2.0 | -34.4 | 2.0 | 0.0 | 0.161 | 10 |
| Static, common (a=0) | 37.3 | 1.9 | -34.4 | 2.0 | 0.0 | 0.161 | 9 |
| Static, common (a=1) | 37.3 | 2.0 | -34.4 | 2.0 | 0.0 | 0.161 | 10 |
| Central search (a=0) | 34.3 | -8.0 | -36.2 | 2.4 | 0.2 | 0.408 | 10 |
| Central search (a=1) | 35.5 | -4.6 | -34.5 | 2.6 | 0.6 | 0.353 | 10 |
| Global-CW OSCAR | 33.3 | 7.1 | -34.5 | 2.0 | 0.0 | 0.088 | 10 |
| Independent OSCAR | 22.7 | -14.7 | -25.3 | 2.0 | 0.0 | 0.525 | 10 |
| PF learner | 37.2 | -2.5 | -33.0 | 3.0 | 2.0 | 0.272 | 10 |
