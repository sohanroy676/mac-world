## 2. System, simulator and metrics

### 2.1 Simulator
| Item | Value |
|---|---|
| Simulator | ns-3.29 with ns3-gym (upstream code used unchanged; the project code is in `ns-3.29/scratch/linear-mesh/`) |
| PHY / MAC | 802.11ax, one 5 GHz channel, 20 MHz, HE MCS 11, 800 ns guard interval, constant-rate station manager |
| Traffic | Constant-rate UDP uplink from each station to its AP, 1464-byte payload; offered load per station is set per scenario (10 Mbps per station is saturating) |
| Topology | N APs, each with its own SSID and its stations, fixed positions. One collision domain by default; `--apHidden` removes the hearing between listed AP pairs |
| Measured frame times | Successful exchange Ts = 226 us, collision Tc = 242 us; scheduled-access capacity 51.82 Mbps per BSS |
| Step | 10 ms of simulated time per decision step |
| CW control | The AP writes a CW to its stations every 10 ms. Static runs keep a fixed CW. The CW range is 16 to 1024 in the early studies and 4 to 32767 in the max-CW study |
| Hidden node and RTS/CTS | Hidden pairs through `--apHidden`; `--useRts` turns RTS/CTS on for every frame |
| Dynamic load | `--staSchedule` switches groups of stations on and off in time windows |
| Per-AP load | `--apLoads` sets the offered load per station of each AP |
| Seeds | ns-3 seed = trainer seed + 1; training seeds 2000 and up; evaluation seeds are disjoint from training and selection seeds |

Simulator limits, which apply to every result in this report:
- constant-rate UDP uplink only (no TCP, no bursty traffic, no downlink traffic);
- one channel, no mobility, no OBSS-PD or BSS colouring (ns-3.29 has no such model);
- binary hearing between BSSs (no graded interference strengths);
- the exact CW write every 10 ms, which a real AP cannot do (Gate C in section 6 tests a beacon-style update).

### 2.2 Metrics
- **Goodput** of an AP: payload bits received at its sink per second, in Mbps; reported per AP, as an aggregate, and as the minimum over APs.
- **Jain fairness index** over the per-AP goodputs, J = (sum x)^2 / (N sum x^2), from 1/N to 1.
- **Collision proxy:** the PHY loss ratio of the policy window, 1 - (frames received) / (frames sent by the PHY), and, in runs with extra traces, the per-AP retry rate.
- **Delay:** per-AP mean, median and 99th percentile of the one-way delay of received packets.
- **Station-weighted alpha-fair utility** of a run: U_alpha = sum over APs of n_i u_alpha(x_i / n_i), where n_i is the number of stations of AP i, x_i its goodput, u_0(y) = y, u_1(y) = ln y and u_alpha(y) = y^(1-alpha) / (1-alpha) otherwise. Alpha 0 is total throughput, alpha 1 is proportional fairness and alpha 4 is close to max-min fairness.
- **Fair floor:** a run is feasible if every AP gets at least 0.95 of its BEB floor, where the floor of AP i is min(BEB goodput of AP i, BEB aggregate x n_i / sum n). A run that breaks the floor counts as share 0 in the max-CW study.
- **Share of the validated ceiling:** share = (U - U_BEB) / (U_ceiling - U_BEB), with BEB paired per seed. Share 0 is BEB, share 1 is the validated static optimum of that cell. The primary criterion of the max-CW study is the worst-cell share of the best online method, with 0.95 as a target set in advance.
- **Statistics:** means with 95 % confidence intervals (Student t) over seeds; paired differences use the same ns-3 seed; the confirmation tests use intersection-union non-inferiority with a margin of 0.05 and Holm correction.

### 2.3 Scenario suite of the project (internal names)
| Name | Topology | Role |
|---|---|---|
| S2 | 20 and 40 stations, one collision domain, 10 Mbps per station | Two-AP unequal BSSs |
| S4 | 10,10,10 stations, APs 1 and 3 cannot hear each other (flow-in-the-middle chain) | Hidden node, fairness |
| S5a | S4 with per-station loads 150, 150 and 1 Mbps | Unequal load |
| S7 | Delay cells: S2 at 0.37 Mbps per station, S4 with loads 1.93, 1.0, 1.93 | Latency |
| S8 | S4 with a time-varying load (stations switched on and off by a schedule); static ceilings exist for its last phase only | Dynamic |
| Mentor cells | 1A to 1D, 2A to 2C, 3A to 3D, 4A to 4D, 5, 6, 7 (Part I) | New simulations for this report |
