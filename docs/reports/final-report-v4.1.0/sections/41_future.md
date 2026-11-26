## 11. Future work
- Mixed uplink and downlink traffic (a downlink sender on every AP, goodput counted at the stations, the controller also setting the AP's own CW).
- Graded asymmetric interference and distance-based path loss (the simulator knows only whether two BSSs hear each other).
- An OBSS-PD approximation through a per-AP carrier-sense threshold (a PHY change that needs an explicit decision).
- TCP and bursty traffic.
- A controller that matches the beacon-style update rate (Gate C), and a test of the original independent per-AP OSCAR in the max-CW cells.
- A central-critic variant that scales beyond four APs.
- Closing the 0.10 gap of kwdirect in S4 at alpha 1 (hidden chain) with a schedule-aware search.
