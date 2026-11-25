Table: Scenario 5, adaptation metrics over the six phases (active stations per AP 10, 15, 20, 25, 15, 10; 20 s each). Dip = lowest 1 s goodput in the first 5 s after a change, relative to the previous phase's level (three joining steps, two leaving steps); recovery = seconds until goodput stays within 5% of the phase's second-half level; CW settling = seconds until the mean CW stays within 10% of its second-half level. Means over the five transitions and over evaluation seeds.
| Controller | Mean goodput (Mbit/s) | Dip when stations join (%) | Dip when stations leave (%) | Recovery (s) | CW settling (s) | Retry rate | Runs |
|---|---|---|---|---|---|---|---|
| BEB (802.11 default) | 28.7 | -7.2 | -22.1 | 2.0 | 0.0 | 0.605 | 5 |
| BEB + RTS/CTS | 20.5 | -7.2 | 1.1 | 0.8 | 0.0 | 0.332 | 5 |
| DAC | 37.8 | -1.0 | -34.5 | 2.0 | 6.0 | 0.202 | 5 |
| BLADE | 35.9 | 0.8 | -34.2 | 2.0 | 2.0 | 0.109 | 5 |
| IdleSense | 37.2 | 0.5 | -34.9 | 2.0 | 2.0 | 0.165 | 5 |
| KW (online) | 26.4 | -19.6 | -28.9 | 15.0 | 7.4 | 0.392 | 5 |
| Static, model (Patras) | 35.5 | -6.8 | -33.9 | 6.0 | 0.0 | 0.383 | 5 |
| Static, proportional | 37.3 | 1.9 | -34.3 | 2.0 | 0.0 | 0.161 | 5 |
| Static, common best (alpha 0) | 37.3 | 1.9 | -34.3 | 2.0 | 0.0 | 0.161 | 5 |
| Static, common best (alpha 1) | 37.3 | 1.9 | -34.3 | 2.0 | 0.0 | 0.161 | 5 |
| Central online search (alpha 0) | 32.6 | -12.0 | -38.8 | 3.4 | 2.0 | 0.469 | 5 |
| Central online search (alpha 1) | 35.2 | -5.8 | -35.3 | 3.2 | 2.2 | 0.358 | 5 |
| Global-CW OSCAR (central actor) | 33.2 | 7.0 | -34.7 | 2.0 | 0.0 | 0.087 | 5 |
| Independent per-AP OSCAR | 22.8 | -14.9 | -25.9 | 2.0 | 0.0 | 0.527 | 5 |
| Independent PF learner | 37.2 | -2.5 | -33.8 | 2.6 | 2.0 | 0.271 | 5 |
