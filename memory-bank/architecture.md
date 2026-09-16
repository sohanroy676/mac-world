
# Architecture

## Workspace

```text
~/college/major/ns-allinone-3.29/
├── ns-3.29/
│   ├── contrib/opengym/       # ns3-gym
│   └── scratch/linear-mesh/   # OSCAR project
├── .clinerules/
├── AGENTS.md
├── tech-stack.md
├── architecture.md
├── projectBrief.md
└── ROADMAP.md
```

The repository root is the ns-allinone-3.29 directory because future work may modify ns-3 as well as the OSCAR code.

## Current Baseline

Original OSCAR:

```text
1 AP
  ↓
1 Actor-Critic agent
  ↓
CW applied to associated stations
```

## Target Architecture
```text
                 One ns-3 simulation
                        │
          ┌─────────────┴─────────────┐
          │                           │
        AP 1                        AP 2 ... AP N
          │                           │
      Agent 1                     Agent 2 ... Agent N
          │                           │
        CW 1                        CW 2 ... CW N
          │                           │
       STAs 1                      STAs 2 ... STAs N
```

- One independent AP-level Actor-Critic agent per AP.
- Each AP has its own CW.
- Each AP agent uses local AP information.
- AP agents must not receive another AP's local observations.
- Initial target: 2 APs, then scale toward 10 APs.
- Station counts may differ between APs.
- A centralized critic is a later phase, not required for v1.

## Data Flow

```text
ns-3 local statistics
        ↓
AP observation
        ↓
AP's RL agent
        ↓
CW action
        ↓
AP-specific ns-3 configuration
        ↓
simulation
        ↓
reward/statistics
```

The multi-AP implementation must keep observations, rewards, statistics, and CW configuration AP-specific.

## ns3-gym

contrib/opengym connects Python RL code with ns-3.

Any interface changes must support multiple APs while keeping all APs inside the same ns-3 simulation.

## External Services

W&B is used for experiment tracking.

Never hardcode W&B credentials or API keys. Use environment/local authentication.