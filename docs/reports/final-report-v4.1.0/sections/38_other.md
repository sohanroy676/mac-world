## 8. Other configurations

### 8.1 Load, imbalance and station count
Covered in section 4: offered load 0.5, 1 and 150 Mbps per station, unbalanced BSSs (5 and 55; 5,5,5 and 45), and 2 to 10 APs at a fixed 60 stations. In short, a shared-CW learner gains most when the channel is saturated or nearly so, the gain vanishes at light load, and independent per-AP agents are never better than BEB there.

### 8.2 Delay cells (S7)
The delay objective was prepared but not completed: oracles exist (S2 at 0.37 Mbps per station: best static CW 256,256 gives a 99th-percentile delay of 19.5 ms against 27.3 ms for BEB; S4 with loads 1.93, 1.0 and 1.93 Mbps: static 128,64,128 gives 9.3 ms against 10.7 ms, a weak separation), but the baselines and learners were not run on them in v4.1.0. Part I reports delay (mean, median and 99th percentile) for the new unsaturated cell.

### 8.3 Dynamic load (S8)
S8 switches half of the edge stations on and off during a 60 s run. A change detector for the online controllers gave no measurable benefit at this shift size (the 5-station load shift at 30 s is tracked by the search without a restart); a stronger shift is needed to show a benefit. Part I (scenario 5) studies a stronger dynamic case: 25 stations per AP switched on and off in six phases.

### 8.4 RTS/CTS
See section 5.4: RTS/CTS lowers goodput in every project cell, and Part I (scenarios 2 and 7) repeats the comparison on the new hidden topologies.

### 8.5 What was not covered
A-MPDU aggregation at the stations, TCP and bursty traffic, downlink traffic, graded interference strengths and OBSS-PD. The last three are the first items on the post-report list (section 11).
