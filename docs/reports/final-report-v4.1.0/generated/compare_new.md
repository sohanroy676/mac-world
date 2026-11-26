### 7.4 The report cells: every controller on 17 cells

Part I ran 17 cells (scenarios 1 to 6, seeds 400 to 409; the dynamic-station cell 5 and the hidden-chain cell S4 are reported with their own metrics). The figure and the table summarise the total-goodput change of every controller against BEB. "Better" counts the cells where the change is positive, larger than 0.5 % and larger than its 95 % confidence interval. "Floor met" is the share of runs in which every AP keeps at least 95 % of the smaller of its BEB goodput and its proportional share (the fair-floor test of Part II section 2.2).

![Total goodput change against BEB for every controller and cell](figures/rep_heatmap.png){w=600}

Table: Summary over the 17 report cells (total goodput change against BEB).
| Controller | Cells better than BEB | Median change (%) | Worst (%) | Best (%) | Floor met |
|---|---|---|---|---|---|
| BEB + RTS/CTS | 0 / 17 | -30.0 | -32.2 | -15.5 | 5 % |
| DAC | 15 / 17 | +29.8 | +0.0 | +53.3 | 95 % |
| BLADE | 14 / 17 | +20.3 | -3.7 | +56.4 | 93 % |
| IdleSense | 16 / 17 | +25.2 | +0.0 | +59.4 | 95 % |
| KW (online) | 8 / 17 | +5.2 | -46.4 | +23.7 | 64 % |
| Static, Patras model | 13 / 17 | +11.6 | -2.4 | +33.0 | 73 % |
| Static, proportional | 15 / 17 | +30.7 | -0.6 | +61.8 | 82 % |
| Static, common (a=0) | 16 / 17 | +30.7 | +0.0 | +59.7 | 100 % |
| Static, common (a=1) | 15 / 17 | +30.7 | -0.6 | +59.7 | 100 % |
| Central search (a=0) | 16 / 17 | +28.4 | -0.0 | +58.4 | 99 % |
| Central search (a=1) | 15 / 17 | +28.3 | -4.8 | +58.9 | 100 % |
| Global-CW OSCAR | 15 / 17 | +27.0 | -0.9 | +57.1 | 99 % |
| Independent OSCAR | 0 / 17 | -52.5 | -80.7 | -1.9 | 12 % |
| PF learner | 15 / 17 | +26.8 | -5.8 | +55.4 | 87 % |

Reading the table:
- No single controller is best everywhere (best controller per cell: Static, proportional 11, PF learner 3, DAC 2, KW (online) 1).
- Global-CW OSCAR is within 8.5 points of the common static CW chosen for alpha 1 in the 12 single-domain cells (largest gap in cell 3B); it is below it in every one of these cells (smallest gap 0.1 points).
- In the hidden chain (2C) the central online search and the PF learner are the controllers that raise the starved middle BSS (8.3 and 6.7 Mbit/s against 1.1 for BEB), at -4.8 % and -5.8 % of total goodput.
- Independent per-AP OSCAR, trained for this report with a small budget (12 episodes of 15 s per agent), is below BEB in 17 of the 17 cells; the result does not say what a longer training would reach (limit).
- BEB with RTS/CTS is 29 % to 32 % below BEB in every cell where the load saturates the channel (all except 6U).
