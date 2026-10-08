# Roadmap

- Read the `docs/detailed_roadmap.md` for a more detailed roadmap of the project.

## Now — Core Two-AP Implementation

### v0.1.0 — Baseline
- Freeze and reproduce the existing single-AP OSCAR baseline.
- Status: ✅ CLOSED 2026-09-16 — tag `v0.1.0` on `major-project`. Freeze runner
  + docs + smoke validation + episode-1 baseline numbers recorded (full
  3-episode run stopped by user decision during episode 2; redo anytime with
  one command). See `docs/baseline-v0.1.0.md`.

### v0.2.0 — Design
- Define multi-AP topology, observations, actions, rewards, statistics, and ns3-gym interface.
- Status: ✅ CLOSED 2026-09-16 — design contract accepted with one shared
  ns-3 process, two APs by default, per-AP DDPG agents, AP-local observation/
  reward/CW/statistics, sequential joint stepping, and no central critic in the
  core v1 path. See `docs/multi-ap-design-v0.2.0.md` and ADR-0002.

### v0.3.0 — Two APs
- Create two APs in one ns-3 simulation.
- Support different station counts per AP.
- Status: ✅ CLOSED 2026-10-07 — tag `v0.3.0` on `main`. 2 APs / unequal
  STAs in one ns-3 sim, per-STA association and per-AP sink traffic verified, no RL dependency.

### v0.4.0 — Per-AP Statistics
- Separate throughput, packet, loss/collision, reward, and other required measurements by AP.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.4.0` on `main`. Per-AP rx/PHY-tx/app-tx, loss, throughput, totals and Jain; validated on 2,3 / 5,15 / 20,40 and single-AP.

### v0.5.0 — AP-Specific CW
- Give each AP independent CW control.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.5.0` on `main`. Per-AP CW via per-node paths + `--apCws` + readback check; validated on 5,15 and single-AP.

### v0.6.0 — Multi-AP ns3-gym
- Support multiple AP observations, actions, and rewards through the Python/ns-3 interface.
- Status: ✅ CLOSED 2026-10-08 — tag `v0.6.0` on `main`. Joint per-AP obs/action/reward via ns3-gym; validated on 2,3 / 5,15 and single-AP.

### v0.7.0 — Independent Agents
- Add one independent AP-level DDPG Actor-Critic agent per AP.
- Status: 🟡 IMPLEMENTED 2026-10-08 on `feature/v0.7.0-independent-agents` (not merged/tagged). `OSCAR_multi_ap_train.py --check` PASS on 2,3.

### v0.8.0 — W&B
- Add clear per-AP and aggregate experiment logging.

### v0.9.0 — Validation
- Validate the complete two-AP system with different station distributions.

### v1.0.0 — Core Milestone
- Working, repeatable two-AP multi-agent OSCAR implementation.

## Next — Scaling and Benchmarking

### v1.1.0
- Benchmark against relevant baseline configurations.

### v1.2.0
- Scale to 4 APs.

### v1.3.0
- Scale to 6 APs.

### v1.4.0
- Scale to 8 APs.

### v1.5.0
- Scale to 10 APs.

### v1.6.0
- Analyze scaling behavior and performance.

## Later — Central Critic

### v1.7.0
- Design centralized critic.

### v1.8.0
- Implement centralized critic prototype.

### v1.9.0
- Evaluate centralized critic against independent AP agents.

## Later — Finalization

### v2.0.0
- Additional robustness experiments.

### v2.1.0
- Reproducibility and cleanup.

### v2.2.0
- Final experimental results.

### v2.3.0
- Technical report.

### v2.4.0
- Presentation and demonstration.

### v2.5.0
- Final project audit.

## Not Planned for v1

- Mobility
- Dynamic station addition
- Detailed AP interference modeling
- Per-station Actor agents
