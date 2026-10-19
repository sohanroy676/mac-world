# Agent Instructions

This project extends OSCAR into a multi-AP ns-3 DRL system. The project root is `~/mac-world` (git repo; project code in `ns-3.29/scratch/linear-mesh/`).

**Stack:** ns-3.29, C++, Python 3.7.16, ns3-gym, PyTorch 1.13.1+cu117, DDPG, W&B.

```bash
cd ~/mac-world/ns-3.29 && ./waf build --target=linear-mesh
cd ~/mac-world/ns-3.29/scratch/linear-mesh && ../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --check
```

- Preserve the existing working environment and dependencies.
- Keep AP observations, rewards, actions, statistics, and CWs isolated.
- Distinguish project changes from upstream ns-3/ns3-gym code.
- Never commit credentials, build files, virtual environments, caches, or generated artifacts.

See .clinerules/ for detailed rules.