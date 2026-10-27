# Does a coordinated design improve on OSCAR? Claim report

Status: draft, 2026-10-27. Seeds 20-24 confirmation (20/20 PASS) and static-CW control (5/5 PASS) are in; the static-CW code lives on branch `feature/static-cw-baseline`. Remaining `TBD` cells are dev-seed (0-2) details that need a lookup in the source tables; nothing else is open. Not merged, pushed or tagged.

## 1. Question and definitions
Question: does a coordinated multi-AP variant give higher aggregate throughput than OSCAR deployed per AP?

Definitions (source: [coop-v2.8.0](coop-v2.8.0.md) §0):
- **Original OSCAR** (Grasso, Raftopoulos, Schembra, ICC 2023): one DDPG agent, one CW, one BSS.
- **Per-AP OSCAR = `independent`**: one OSCAR agent per AP. The baseline for every claim below.
- **`global`**: one agent, one CW for all APs, network-wide reward. Centralized, privileged; not OSCAR, not decentralized.
- **Variants under test**: `coop` (mixed reward), `shared` (one actor-critic for all APs, ADR-0004), `central` (per-AP actors, central critic). **BEB** = standard 802.11.
- Metric: aggregate Mbps over the last 300 steps (`tot_policy`), 15 s runs, 10 ms steps, 150 Mbps per STA, `--check` must PASS. Paired by ns-3 seed, 95 % t-interval.

## 2. Paper reference (relative numbers only)
The paper gives +11 % (15 STAs) to +40 % (50 STAs) over standard 802.11 for a single AP, convergence in about 300 epochs, and no absolute Mbps. mac-world has **not** reproduced these (run (A) in [oscar-baseline-metrics](oscar-baseline-metrics.md) not done), so no statement is made about matching the paper. Setup match and mismatches (batch, discount, tau, reward) are listed there.

## 3. Rule (fixed before the runs)
Source: [claim-prereg-v2.8.1](claim-prereg-v2.8.1.md). A claim needs the lower bound of the paired CI to be above 0 on seeds not used for tuning. One positive among several comparisons is "suggestive, not confirmed". Seeds 0-2 are tuning/dev seeds and never count as confirmation.

## 4. Evidence
All values are Δ aggregate Mbps versus `independent` unless stated; mean ± 95 % CI.

| Seed set | Topology | Variant − independent | Δ Mbps | Seeds above | Status |
|---|---|---|---|---|---|
| 0-2 (dev, tuning) | 6x10 | central | +15.1 ± 10.4 | TBD (check source) | dev only, no claim |
| 0-2 (dev, tuning) | 15,15,15,15 | shared ×1 / ×100 | TBD (levels: 34.6 ± 15.1 / 38.50 ± 1.06 vs independent 20.14) | TBD | dev only, no claim |
| 10-14 (confirmation) | 15,15,15,15 | shared (P1) | +7.62 ± 15.84 | 4/5 | not shown |
| 10-14 (confirmation) | 15,15,15,15 | coop L=1 (P2) | +8.10 ± 8.61 | 5/5 | not shown (lower bound ≈ −0.5) |
| 10-14 (confirmation) | 6x10 | central (P3) | +9.29 ± 7.73 | 5/5 | suggestive, not confirmed |
| 20-24 (confirmation) | 15,15,15,15 | shared ×100 (pre-registered, Addendum A) | **+19.67 ± 1.31** (+111 %) | 5/5 | confirmed on this topology |
| 20-24 (control) | 15,15,15,15 | static CW 850, no agent (pre-registered, Addendum B) | **+19.94 ± 1.73** (+113 %) | 5/5 | same gain with no learning |

Context rows (same seeds 10-14, from claim-prereg-v2.8.1):
- `independent` is below BEB at 6x10 by −13.19 ± 2.53 Mbps (0/5 seeds above), and 20.14 vs 27.85 Mbps at 15x4.
- `global − independent` at 6x10 is +19.13 ± 9.38 (5/5).
- No variant beats BEB or `global` with CI > 0. `central − global` at 6x10 is −9.84 ± 7.43.
- Shared ×1 collapsed in 1 of 5 confirmation seeds (seed 10, 3.28 Mbps); shared ×100 on seed 10 did not (35.77, diagnostic only, not counted).

Seeds 20-24, 15,15,15,15 (source: claim-prereg-v2.8.1 Addendum A confirmation; tables `docs/figures/v2.8.2/confirm-shared-rs100/`):

| Mode | Aggregate Mbps | Jain |
|---|---|---|
| BEB | 27.56 ± 0.65 | 0.991 |
| `independent` (per-AP OSCAR) | 17.74 ± 1.40 | 0.725 |
| `global` (centralized) | 23.77 ± 21.30 | 0.992 |
| `shared` ×100 | 37.41 ± 1.15 | 0.994 |
| static CW 850 (no agent) | 37.68 ± 0.47 | 0.995 |

Control (Addendum B): shared ×100 − static850 = −0.27 ± 1.61 (1/5); static850 − BEB = +10.12 ± 1.10 (5/5).

Secondary: shared ×100 − BEB +9.85 ± 0.67 (5/5, CI > 0); shared ×100 − `global` +13.64 ± 22.01 (3/5, no claim). `global` collapsed to about 5.5 Mbps in 2 of 5 seeds; shared ×100 never did (minimum 36.86).

## 5. Verdict
- **Confirmed, but not as learning (one topology):** `shared` with `--rewardScale 100` has higher throughput than per-AP OSCAR at 15,15,15,15 on fresh seeds 20-24: +19.67 ± 1.31 Mbps, 5/5, under the rule fixed before the runs (also +9.85 ± 0.67 over BEB).
- **The learning is not shown to matter:** a fixed CW 850 with no agent gets the same throughput (37.68 ± 0.47 vs 37.41 ± 1.15; shared − static −0.27 ± 1.61, 1/5), so by the pre-registered reading rule (Addendum B) the gain over per-AP OSCAR is not shown to need a learned policy. The honest statement is: per-AP OSCAR is far from a good operating point here (CW stays low, 17.74 Mbps), and any policy that reaches CW of several hundred does much better.
- **Suggestive, not confirmed:** `central` over per-AP OSCAR at 6x10 (P3, +9.29 ± 7.73). No static-CW control was run at 6x10.
- **Not shown:** `coop` and `shared` ×1 over per-AP OSCAR (CIs include 0).
- **Not claimed:** beating `global` (+13.64 ± 22.01, 3/5; `global` collapsed in 2/5 seeds); beating a well-chosen fixed CW; generalizing to other topologies; beating the paper's single-AP OSCAR.
- **Open:** only CW 850 was tried as the fixed baseline; the best fixed CW is unknown and might beat shared ×100. Shared ×100's own CW varied by seed (about 470 to 960).

## 6. Limits
n = 5 per comparison; two topologies; one run per cell; 15 s simulated, single channel; `central` collapsed at 4..40 and 22x10 in earlier runs; shared ×100 sits at a high CW (about 940-960 in four seeds, about 470 in seed 22, grand mean about 850; the lock-in is not removed, only its side changed in the seed-10 diagnostic), and `--rewardScale 100` was chosen on dev seeds 0-2 plus that diagnostic; the 15x4 independent seed 0-2 and 10-14 means are equal by coincidence; no paper reproduction; `global` mislabelled as OSCAR in older docs and legends (PNG figures made before 2026-10-25 still show the old text).

## 7. Sources
[claim-prereg-v2.8.1](claim-prereg-v2.8.1.md), [coop-v2.8.0](coop-v2.8.0.md), [final-results-v2.2.0](final-results-v2.2.0.md), [oscar-baseline-metrics](oscar-baseline-metrics.md); tables in `docs/figures/v2.8.0/`, `docs/figures/v2.8.1/`, `docs/figures/v2.8.2/` (`confirm-shared-rs100/`, `confirm-static850/`).
