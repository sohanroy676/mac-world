# v1.2.0 — Scale to 4 APs (2026-10-15)

Branch `feature/v1.2.0-four-aps`. No ns-3 / cw.cc change: the code was already N-generic (fact, verified by runs below).
Only two 2-AP leftovers fixed (trainer reward-column check, aggregate bar plot). Binary unchanged since Oct 12.

## 1. Validation (all PASS)

| Criterion | Command (seed 1 unless noted) | Result |
|---|---|---|
| Single-AP regression | `--nWifi=5` dry, simTime 2 | 10533 pkts |
| 2-AP regression | `--apStaCounts=5,15` dry | 9000 pkts |
| 4 APs associate, per-AP stats | `--apStaCounts=2,3,4,5` dry | association ok 2/3/4/5, wrongAp 0, Σ per-AP == global (9559 pkts), 42 s |
| same, larger | `--apStaCounts=5,10,15,20` dry | all checks PASS, 7283 pkts, 139 s |
| Per-AP CW | `2,3,4,5 --apCws=16,64,256,1024` | CW check PASS; throughput 25.6 / 9.8 / 3.1 / 1.0 Mbps (falls with CW) |
| Gym obs/action/reward shapes | `test_multi_ap_gym.py --staCounts 2,3,4,5 --phases "0,2,4,6;6,4,2,0"` | readback == action per AP, both phases |
| Trainer | `OSCAR_multi_ap_train.py --apStaCounts 2,3,4,5 ... --check` (30 steps) | PASS, 33 W&B keys/row, also after the check fix |

Not re-run: gym smoke (10.59458); binary unchanged.

## 2. Long runs (5,10,15,20 STAs; seed 0; n=1; 1500 steps; policy window = steps >= 300)
Data: `docs/figures/v1.2.0/` (raw run dirs under `ns-3.29/scratch/linear-mesh/results/` are force-committed for this milestone only, user-approved exception). Run time 716 / 728 / 793 s (BEB / global / independent), all PASS incl. `--check`.

| Mode | Aggregate Mbps | AP1 | AP2 | AP3 | AP4 | Jain | CW last-100 (AP1..AP4) |
|---|---|---|---|---|---|---|---|
| BEB | 27.64 | 2.80 | 6.46 | 9.15 | 9.22 | 0.874 | 16 x4 |
| Global-CW | 39.53 | 1.87 | 11.36 | 3.87 | 22.44 | 0.600 | 174 x4 |
| Independent | 23.34 | 1.37 | 7.39 | 3.73 | 10.85 | 0.724 | 29 / 18 / 19 / 30 |

Single seed: no CI; do not read as a claim.

- Fact: training is stable in the sense of no crash / NaN / check failure at 4 agents; four distinct CW traces for independent.
- Fact (figures): global-CW holds ~39.5 Mbps from step ~400 on, but at the cost of fairness (Jain 0.60; AP4 22.4 vs AP1 1.9 Mbps).
- Fact (figures): independent agents all fall to CW ~2^4 (near the lower bound) by step ~600-800; aggregate throughput drops from ~38 to ~18 Mbps (below BEB ~27.6), partially recovers to ~22.6 by step 1500. Same late-drift pattern as 20,20 in v1.1.0.
- Inference, untested: with all agents pinned near CW 16 and no exponential backoff, collisions rise; not verified.
- Unknown: whether AP1<->AP4 (150 m) hidden-node effects matter; not examined.

## 2b. Seeds 0,1,2 (n=3; same topology, same policy window; 9/9 runs PASS incl. `--check`)
Data: `docs/figures/v1.2.0-b2/` (tables.md, 4 figures, manifest.csv). Run time 716-850 s each. Mean ± 95% CI (Student t).

| Mode | Aggregate Mbps | Jain | CW last-100 (AP1..AP4) |
|---|---|---|---|
| BEB | 28.63 ± 2.26 | 0.862 ± 0.030 | 16 x4 |
| Global-CW | 37.29 ± 4.81 | 0.660 ± 0.161 | 193 ± 132 (shared) |
| Independent | 23.27 ± 13.19 | 0.737 ± 0.366 | 22 / 31 / 30 / 46 (CIs 14-56) |

Paired vs BEB (same ns-3 seed): global +8.66 ± 6.99 Mbps (+30.5 ± 27.2 %), CI excludes 0; independent -5.37 ± 14.07 Mbps (-18.6 ± 47.6 %), CI includes 0.

- Supported by CI (n=3): global-CW beats BEB aggregate throughput at 5,10,15,20. Consistent with 20,20 (+26 %) and 20,40 (+32 %) in v1.1.0.
- Not supported: any claim that independent agents are better or worse than BEB; the interval is wide (seed spread large).
- Fact (convergence figure): mean independent throughput starts ~37 Mbps, falls to ~18.5 Mbps near step ~970, recovers to ~23 by step 1500. Global holds ~37-38. Same late-drift shape as seed 0 and as 20,20 in v1.1.0.
- Fact: mean Jain is lower for both trained modes than BEB. Global 0.660 ± 0.161 (0.50-0.82) vs BEB 0.862 ± 0.030 (0.83-0.89): the intervals barely do not overlap. Independent's interval (0.37-1.10) overlaps BEB's. These are unpaired intervals, not a paired test, so treat it as a trend: global-CW's aggregate gain comes with lower fairness.
- Unknown: why independent agents drift down; the "pinned near CW 16, more collisions" idea in §2 is still untested.

## 3. Open
t=1.144 s deassociation (fact, from run logs; deassoc count == re-assoc count in every run, every STA re-associates):

| Seed | BEB | Global | Independent |
|---|---|---|---|
| 0 | 0 | 4 | 5 |
| 1 | 0 | 10 | 10 |
| 2 | 0 | 17 | 17 |

Fact: BEB has 0 events at all 3 seeds here; the trained modes have events at every seed, and the count varies by seed (global and independent match exactly at seeds 1, 2). Same pattern as 20,20 / 20,40 in v1.1.0 (where BEB showed 1 event at 20,40); cause still unproven.
Next options: v1.3.0 (6 APs), or tag v1.2.0 (user deferred the tag; not tagged).
