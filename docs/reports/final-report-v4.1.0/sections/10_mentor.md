# Scenarios to be considered:

## Scenario 1: Two APs with fully overlapping coverage

### Topology

- Number of APs: 2.

- Stations per AP: 10 initially.

- Total stations: 20.

- Channel: Same channel for both APs.

- Channel width: 20 MHz.

- Coverage: Both APs and their associated stations are within the mutual interference region.

- Traffic: Saturated uplink initially.

### Experimental variations

| **Experiment** | **AP1 stations** | **AP2 stations** |
|----------------|------------------|------------------|
| 1A             | 10               | 10               |
| 1B             | 15               | 15               |
| 1C             | 20               | 20               |
| 1D             | 25               | 25               |

### Objective

Investigate whether a centralized Actor can learn different CW values for two competing BSSs and improve aggregate throughput.

For example, the controller may learn that AP1 requires a larger CW than AP2 under particular traffic and contention conditions.

### Research questions

1.  Can the global Actor learn appropriate CW values for both APs?

2.  Does joint CW optimization outperform applying the same CW to both APs?

3.  Does the approach reduce collisions compared with independent per-AP CW optimization?

4.  Does it improve inter-BSS fairness?

This should be your first experiment because it establishes the feasibility of centralized multi-AP control.

{{results:1}}

## Scenario 2: Partially overlapping BSSs

### Topology

- Number of APs: 3.

- Stations per AP: 10–15.

- AP1 and AP2 overlap.

- AP2 and AP3 overlap.

- AP1 and AP3 have negligible interference.

- Same operating channel.

### Experimental variations

| **Experiment** | **AP relationships**             | **Stations** |
|----------------|----------------------------------|--------------|
| 2A             | AP1–AP2 overlap only             | 10 each      |
| 2B             | AP2–AP3 overlap only             | 10 each      |
| 2C             | AP1–AP2 and AP2–AP3 overlap      | 15 each      |
| 2D             | Different interference strengths | 15 each      |

### Objective

Study the impact of interference relationships on optimal CW selection.

This is more interesting than Scenario 1 because the APs do not all experience identical contention conditions.

For example:

- AP1 may contend primarily with AP2.

- AP2 experiences interference from both AP1 and AP3.

- AP3 primarily contends with AP2.

The global Actor should learn the joint CW configuration that balances these different contention conditions.

Important observation: Include an AP-to-AP interference matrix in the state representation. This will help the Actor distinguish between fully connected and partially connected topologies.

{{results:2}}

## Scenario 3: Three or four APs with fully overlapping BSSs

### Topology

- APs: 3 and 4.

- Stations per AP: 10, 15 and 20.

- Same channel.

- All APs experience substantial mutual interference.

- Fixed MCS and transmission power.

### Experimental variations

| **Experiment** | **APs** | **Stations per AP** |
|----------------|---------|---------------------|
| 3A             | 3       | 10                  |
| 3B             | 3       | 20                  |
| 3C             | 4       | 10                  |
| 3D             | 4       | 20                  |

### Objective

Evaluate scalability as the number of APs increases.

The Actor output dimension increases with the number of APs:

- Two APs: 2-dimensional action.

- Three APs: 3-dimensional action.

- Four APs: 4-dimensional action.

The same global Critic evaluates the resulting network performance.

### Research questions

- Does the learning algorithm converge as the number of APs increases?

- Does the performance improvement remain consistent?

- Does the joint action space affect sample efficiency?

- How does the learned CW distribution change with AP density?

This scenario is important for establishing the scalability of your proposed algorithm.

{{results:3}}

## Scenario 4: Unequal station distribution across APs

### Topology

Deploy four APs with different station densities.

| **Experiment** | **AP1** | **AP2** | **AP3** | **AP4** | **Total** |
|----------------|---------|---------|---------|---------|-----------|
| 4A             | 10      | 10      | 10      | 10      | 40        |
| 4B             | 10      | 20      | 30      | 40      | 100       |
| 4C             | 5       | 15      | 25      | 35      | 80        |
| 4D             | 40      | 20      | 10      | 5       | 75        |

Keep the BSSs fully or partially overlapping, depending on the experiment.

### Objective

Investigate whether the centralized controller can assign different CW values based on the number of contending stations and traffic demand.

For example:

- AP1 has fewer stations and relatively low contention.

- AP4 has more stations and potentially higher contention.

- A common CW may not provide good performance to all BSSs.

### Research questions

1.  Does the controller adapt CW according to station density?

2.  Does it improve fairness between heavily and lightly loaded BSSs?

3.  Does it prevent one AP from dominating channel access?

This experiment is particularly valuable because aggregate throughput alone may hide poor performance in smaller BSSs.

{{results:4}}

## Scenario 5: Dynamic station association and disassociation

Priority 4 – Dynamic environment

### Topology

- Initially deploy three APs.

- Initially associate 10 stations with each AP.

- Gradually increase the number of stations.

- Subsequently decrease the number of stations.

Example:

| **Simulation phase** | **AP1** | **AP2** | **AP3** |
|----------------------|---------|---------|---------|
| Initial              | 10      | 10      | 10      |
| Phase 2              | 15      | 15      | 15      |
| Phase 3              | 20      | 20      | 20      |
| Phase 4              | 25      | 25      | 25      |
| Phase 5              | 15      | 15      | 15      |
| Phase 6              | 10      | 10      | 10      |

### Objective

Evaluate how effectively the global Actor adapts its CW decisions to changing network density.

Measure:

- Convergence after topology changes.

- Time taken to stabilize CW.

- Throughput degradation during transitions.

- Collision probability.

- Recovery time.

This is an important experiment for evaluating the adaptability of RE-DARC.

{{results:5}}

## Scenario 6: Heterogeneous traffic loads across Aps

### Topology

Three or four APs, with different offered traffic loads.

For example:

| **AP** | **Traffic load** |
|--------|------------------|
| AP1    | 50 Mbps          |
| AP2    | 100 Mbps         |
| AP3    | 150 Mbps         |
| AP4    | 200 Mbps         |

Use both saturated and unsaturated traffic experiments.

### Objective

Study how the global Actor responds when different BSSs have different traffic demands.

Possible traffic types:

- Constant-rate UDP traffic.

- Bursty traffic.

- Mixed UDP and TCP traffic.

### Research questions

- Can the Actor allocate channel access opportunities according to traffic demand?

- Does the optimization improve delay under heterogeneous loads?

- Does it avoid starving low-load APs?

This scenario will make your work more realistic than evaluating only saturated networks.

{{results:6}}

## Scenario 7: Hidden-node and asymmetric interference

### Topology

- Three APs.

- Some stations cannot sense transmissions from neighboring BSSs.

- Interference is asymmetric.

- Different distances between APs and stations.

### Objective

Evaluate whether global CW optimization can improve performance when carrier sensing does not accurately represent interference.

Measure:

- Collision probability.

- Packet loss.

- Throughput.

- Delay.

- Impact of RTS/CTS.

I would keep RTS/CTS disabled in the initial experiment and introduce it as a separate comparison.

{{results:7}}

## Scenario 8: Mixed uplink and downlink traffic

### Topology

- Three or four APs.

- Each AP has associated stations.

- Some BSSs carry uplink traffic.

- Others carry downlink traffic.

- Finally, evaluate simultaneous bidirectional traffic.

### Objective

Determine whether the centralized CW controller can handle competition between AP transmissions and station transmissions.

This is particularly important because the contention participants differ between uplink and downlink traffic.

{{results:8}}

## Extension:

You can consider joint CW and OBSS-PD optimization as a subsequent research extension.

{{results:ext}}
