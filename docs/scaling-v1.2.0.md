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
Data: `docs/figures/v1.2.0/` (raw `results/` stays local). Run time 716 / 728 / 793 s (BEB / global / independent), all PASS incl. `--check`.

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

## 3. Open
n=1 only; more seeds needed before any 4-AP claim.
t=1.144 s deassociation (fact, from run logs): BEB 0 events, global 4, independent 5; every event at t=1.144 s and every STA re-associates (re-assoc count == deassoc count). Same pattern as 20,20 / 20,40 in v1.1.0 (trained modes only here); cause still unproven.
