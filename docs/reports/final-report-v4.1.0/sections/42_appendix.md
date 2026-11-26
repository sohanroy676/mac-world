## Appendix A. Mentor scenarios mapped to simulator settings
Table: how each mentor scenario was set up in the simulator
| Mentor cell | Stations per AP | Hearing between BSSs | Load | Simulator flags |
|---|---|---|---|---|
| 1A, 1B, 1C, 1D | 10/10, 15/15, 20/20, 25/25 | one collision domain | 10 Mbps per station (saturated) | `--apStaCounts` |
| 2A | 10,10,10 | AP3 hears neither AP1 nor AP2 | saturated | `--apHidden 1-3,2-3` |
| 2B | 10,10,10 | AP1 hears neither AP2 nor AP3 | saturated | `--apHidden 1-2,1-3` |
| 2C | 15,15,15 | AP1-AP3 hidden (chain) | saturated | `--apHidden 1-3` |
| 3A, 3B, 3C, 3D | 3x10, 3x20, 4x10, 4x20 | one collision domain | saturated | `--apStaCounts` |
| 4A, 4B, 4C, 4D | 4x10; 10,20,30,40; 5,15,25,35; 40,20,10,5 | one collision domain | saturated | `--apStaCounts` |
| 5 | 25,25,25 (10 to 25 active) | one collision domain | saturated, six phases of 20 s | `--staSchedule` |
| 6 saturated / unsaturated | 4x10 | one collision domain | per AP 50/100/150/200 Mbps; 2.5/5/7.5/10 Mbps | `--apLoads` |
| 7 | 10,10,10 | AP1-AP3 hidden | saturated, RTS/CTS off and on | `--apHidden 1-3`, `--useRts` |
Not simulated: 2D (graded interference), 7 (asymmetric strengths and distances), 8 (uplink and downlink) and the OBSS-PD extension.

## Appendix B. Glossary
- **AP, STA, BSS:** access point, station, basic service set (an AP and its stations).
- **CW:** contention window; CWmin and CWmax are its lower and upper limits.
- **BEB:** binary exponential backoff, the standard 802.11 rule.
- **DDPG:** deep deterministic policy gradient, an actor-critic reinforcement-learning algorithm.
- **OSCAR:** the DDPG-based CW controller this project starts from.
- **Goodput:** payload data actually received by the AP.
- **Jain index:** fairness measure between 1/N and 1.
- **Alpha-fair utility:** family of fairness measures; alpha 0 is throughput, alpha 1 proportional fairness, alpha 4 close to max-min.
- **Share of the ceiling:** (U - U_BEB) / (U_ceiling - U_BEB).
- **Gate C:** a test that applies the controller's CW every 100 ms, rounded to 2^k-1, like a beacon would.
- **Hidden node:** two transmitters that cannot hear each other but interfere at a common receiver.

## Appendix C. References
1. OSCAR: Grasso, Raftopoulos and Schembra, IEEE ICC 2023, doi 10.1109/ICC45041.2023.10279663.
2. Heusse, Rousseau, Guillier and Duda, "Idle Sense: an optimal access method for high throughput and fairness in rate diverse wireless LANs", ACM SIGCOMM 2005.
3. Patras et al., dynamic CW adaptation controller (DAC), IEEE Transactions on Mobile Computing, 2011.
4. Gawłowicz, Walrand and Wolisz, distributed proportional-fair CW optimization, arXiv 2102.05149 (2021).
5. BLADE, arXiv 2603.16119 (2026).
6. Yan, Du, Zhang and Dong, drlCW, IEEE VTC2024-Spring.
7. CCOD, arXiv 2003.01492.
8. Hao, Li and Duan, in-context learning for MAC control, arXiv 2508.09146.
9. Nunez et al., multi-AP scheduling with PPO, arXiv 2507.19377.
10. Lillicrap et al., "Continuous control with deep reinforcement learning" (DDPG), ICLR 2016.
11. ns-3 network simulator (version 3.29) and ns3-gym (Gawłowicz and Zubow, 2019).
12. IEEE Std 802.11 (DCF, EDCA) and 802.11ax.
