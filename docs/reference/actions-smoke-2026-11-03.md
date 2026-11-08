# GitHub Actions smoke test, 2026-11-03

Branch `feature/actions-compute`, workflow `.github/workflows/actions-smoke.yml`, 5 runs. Only run 5 passed end to end; runs 1-4 each found one problem (listed below). Nothing outside `.github/` and this note was changed.

## Setup that works (fact, run 5)
- `runs-on: ubuntu-24.04` with `container: ubuntu:22.04`: GCC 11.4.0, protoc 3.12.4, libzmq 4.3.4-2, the same versions as the lab machine.
- Python 3.7 from the deadsnakes PPA (`.github/scripts/install_py37.sh deadsnakes`). `uv` failed at install; micromamba gave Python 3.7.12 but its venv pip could not build gym.
- Pins in `.github/ci/requirements-py37.txt`: torch 1.13.1+cpu, numpy 1.21.6, gym 0.26.2, wandb 0.18.7, protobuf 3.20.3, pyzmq 26.2.1, tqdm, matplotlib<3.6. The last two are not in the reproducibility pin table; the trainer imports them.
- Build with `./waf configure` then `./waf --run ...`. `./waf build --target=linear-mesh` on a clean tree failed with `ns3/event-id.h: No such file` (run 3). Cause not proven; `waf --run` posts the header tasks first (see `ns-3.29/wscript`), and switching fixed it.

## Measured (fact)
| Item | Value |
|---|---|
| CPU | AMD EPYC 7763, 4 vCPU = 2 cores x 2 threads (runs 2 and 3) |
| RAM / disk | 15 GB / 145 GB overlay with 85 GB free (not the 14 GB the docs list) |
| Checkout | 22-27 s |
| `waf configure` | 2-3 s |
| Clean debug build + 2 s dry run (20,40 APs) | 5 min 53 s (run 4), 3 min 38 s (run 5) |
| Python 3.7 + pinned installs | about 60-90 s |
| Trainer cell: `--apStaCounts 2,3 --mode independent --simTime 2 --start_timesteps 50 --seed 0 --check` | 20 s, `RESULT: PASS`, 200 steps, W&B check 200 rows x 19 keys |
| Whole workflow | about 6 minutes |

## Not measured yet
- A full 1500-step run (15 s simulated) against the lab timings in `docs/results/`.
- Two simulations side by side on one runner.
- Variation across runner machines (the build took 3:38 and 5:53 on two runs with the same setup).
- Build caching, and artifacts for full runs.
