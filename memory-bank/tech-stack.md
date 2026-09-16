# Tech Stack

## Core

- C++ — ns-3 simulation
- Python 3.7.16 — RL/training
- ns-3.29
- ns3-gym C++ 1.0.0 / Python 0.1.0
- PyTorch 1.13.1+cu117
- DDPG — Actor-Critic reinforcement learning
- ZeroMQ / Protocol Buffers — ns3-gym communication
- W&B 0.18.7 — experiment tracking

## Current Environment

- Gym 0.26.2
- NumPy 1.21.6
- protobuf 3.20.3
- pyzmq 26.2.1
- GCC/G++ 11.4.0
- CUDA 11.7

Treat these as the currently verified environment. Do not upgrade dependencies without approval.

## Commands

Build ns-3:

```bash
cd ~/college/major/ns-allinone-3.29/ns-3.29
./waf build
```

Run OSCAR:

```bash
cd ~/college/major/ns-allinone-3.29/ns-3.29/scratch/linear-mesh
python OSCAR_train.py
```

## Testing / Linting

No formal automated test framework, linting tool, or formatter currently exists.

Do not introduce one unless explicitly requested.

## External Services
- Weights & Biases for experiment tracking.

Credentials/API keys must never be hardcoded or committed. Use the appropriate environment/local authentication mechanism.