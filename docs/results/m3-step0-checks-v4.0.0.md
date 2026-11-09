# M3 step 0 checks (v4.0.0), run on GitHub Actions, 2026-11-09

Runs: [42656890646](https://github.com/sohanroy676/mac-world/actions/runs/42656890646) (29 jobs), [42660670957](https://github.com/sohanroy676/mac-world/actions/runs/42660670957) (14 jobs), [42661069290](https://github.com/sohanroy676/mac-world/actions/runs/42661069290) (7 smoke jobs), [42662489954](https://github.com/sohanroy676/mac-world/actions/runs/42662489954) (8 float probes). All jobs PASS `--check`. Run dirs and logs: `docs/figures/v4.0.0-step0/`. Comparability with the lab: `actions-comparability-2026-11-08.md`.

## 1. STA CW granularity (fact)
Readback of every STA's CW in a `2,3` learner run (`independent`, seed 100, 6 s), counting STA-samples at the exact CW written by `setApCw` against the 2^k - 1 value (samples where the CW is already 2^k - 1 are excluded):

| Step time | Readback every | AP samples | STA-samples exact | rounded | Share exact | Other |
|---|---|---|---|---|---|---|
| 0.01 s (production) | 0.01 s | 1204 | 2695 | 292 | 0.90 | 0 |
| 0.01 s | 0.0073 s | 1646 | 3874 | 203 | 0.95 | 0 |
| 0.1 s | 0.01 s | 1202 | 1570 | 1375 | 0.53 | 0 |

Conclusion: with 10 ms steps, adaptive methods (RAFA, Global, PF learner, IdleSense, KW, UCB, CCOD) keep STAs at the exact, sub-octave CW about 90-95 % of the time; beacons round them to 2^k - 1 only for the rest. The note "only powers of two matter" in the M1/M2 docs is wrong for adaptive methods (it holds for statics). The static oracle is therefore octave-only by definition, as the plan states. The 0.1 s row shows the share depends on step time, so it must not be quoted for other step times. Script: `docs/figures/v4.0.0-step0/granularity/gran.py`.

## 2. Determinism (fact, with one open item)
- `independent` and `shared` same-seed `2,3` reruns (30 steps) on Actions CPU: identical trace on the same CPU vendor (`independent` a/b `db439d30...`; `shared`: 4 of 4 AMD runners `87d2e618...`, pinned 4 of 4 AMD `6ae0ae86...`).
- Across CPU vendors the learner trace differs: AMD EPYC (7763, 9V74, 9V45) versus Intel Xeon (8370C, 8573C, 6973P-C) split perfectly, with and without `ATEN_CPU_CAPABILITY=default MKL_CBWR=COMPATIBLE OMP/MKL_NUM_THREADS=1`. The first difference is the first actor action after warm-up (1 ulp in float32, step 11), so it is the torch forward pass, not ns-3. Float probes (`fp_probe.py`): torch Linear/exp/tanh/sigmoid/randn hashes differ by vendor; numpy exp/tanh/pow and torch log do not (pinned). Non-learned runs were identical on every AMD runner seen; an Intel runner has not been tested for ns-3 itself.
- Inference: 1-ulp differences grow into different trajectories, so a learner run is reproducible bit for bit only on the same CPU vendor. Consequence for the design: learned methods are stochastic across training seeds anyway; no claim pairs a learner with another run through its initial weights, only through the ns-3 seed. A rerun of a learner on another vendor is a new sample, not a replay. The pins do not fix this and cost nothing, but are off by default; keep them off to stay close to the lab setup.
- Not done (unknown): lab GPU (CUDA) versus Actions CPU for the same seed. The two cannot be bit-identical (different kernels); it needs one lab run of the `det-sh` command (`--mode shared --apStaCounts 2,3 --simTime 3 --stepTime 0.1 --historyLength 20 --obsWindow 20 --start_timesteps 10 --batch_size 8 --seed 100 --check`) to quantify, and does not block anything. Rule: every learner that enters one comparison is trained on Actions CPU; lab-trained actors (M2 Global, PF learner, CCOD) are re-trained in M2c on Actions.
- Lab `2,3` reference trace is not in the repo; the Actions BEB `2,3` trace hash is `044cf770...1958` (identical on all runners and before/after the trainer changes).

## 3. Pool BEB references at 10 Mbps per STA (fact)
24 configs, python seed 2000+k, 15 s, equal-load cells at `--offeredLoad 10 --rewardNorm 150`, `apLoads` cells unchanged. Table: `pool-beb-refs-10mbps-v4.0.0.csv` (per-AP Mbps, floors, and the old 150 Mbps values side by side). The five `apLoads` configs reproduce the committed v3.5.0 traces byte for byte (extra platform check, 5 of 5 identical). Equal-load cells differ from the 150 Mbps references by 1-21 % per AP in the one-domain and edge APs; the starved middle AP of the chains moves most (chain 10,10,10: 0.30 vs 1.55 Mbps; chain 8,8,8: 1.68 vs 0.99), which is single-seed noise on a near-zero value, so floors for the pool come from these 10 Mbps runs, not the old file.

## 4. Input scales for ADR-0007 (decision)
Idle slots / 20 (clipped to 1), Retry rate as is (0..1), goodput per active STA / offered per-STA load (0..1), active STAs / 50 (clipped to 1), CW exponent (previous action + 1) / 2. Reward: station-weighted PF, mean over STAs of ln(max(0.01 Mbps, per-STA Mbps)), mapped affinely so 0.01 Mbps gives 0 and 10 Mbps gives 1. Written into ADR-0007. Caveat (fact, cw.cc:566): "active" counts STAs whose data frames the AP decoded in the 10 ms step, so it is a noisy proxy for the STA count with 10 STAs.
