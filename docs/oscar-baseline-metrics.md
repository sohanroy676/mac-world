# OSCAR baseline metrics for comparison

As of 2026-10-25 · requested by xyz

## Bottom line

OSCAR publishes only relative numbers: +11 % (15 STAs) to +40 % (50 STAs) throughput over standard 802.11, convergence in about 300 decision epochs (3 s), and 36x faster learning than CCOD. The paper gives no absolute Mbps, no collision, fairness or delay values, and no released logs; its W&B project could not be reached. A fair comparison therefore means re-running OSCAR and BEB in mac-world's own simulator and reporting the paper's numbers only as a relative reference.

## OSCAR paper metrics

All values are from [Grasso, Raftopoulos, Schembra, ICC 2023](https://doi.org/10.1109/ICC45041.2023.10279663), read via the [ResearchGate full text](https://www.researchgate.net/publication/374931185_OSCAR_A_Contention_Window_Optimization_Approach_Using_Deep_Reinforcement_Learning). Fig. 2 plots more station counts than 15 and 50, but only those two are stated in the text.

| Metric | Value | Scenario | Where |
| --- | --- | --- | --- |
| Throughput gain vs standard 802.11 | +11 % at 15 STAs, +40 % at 50 STAs | after 3 s of learning | Sec. V, Fig. 2a |
| Throughput gain vs CCOD (DDPG) | +30 % at 15 STAs, +15 % at 50 STAs | after 3 s of learning | Sec. V, Fig. 2a |
| Throughput vs CCOD after 110 s | "basically the same" | CCOD converged | Sec. V, Fig. 2b |
| Convergence | about 300 decision epochs (about 3 s) | 10 ms epochs | Sec. V, Fig. 1b |
| CCOD convergence | 11000 decision epochs (about 2 min) | same | Sec. V, Fig. 1b |
| Learning speed | 36x faster than CCOD | same | Sec. V |
| Compute | 12 runs of 15 s in about 10 min on 2x RTX 3070 | training cost | Sec. V |
| Runs per experiment | 12 rounds of 15 s simulations | all figures | Sec. IV |
| Absolute throughput (Mbps) | not stated in text; only on Fig. 1 and Fig. 2 axes | | Figs. 1-2 |

Paper hyper-parameters (Table I): 10 ms epoch, actor 128x128 lr 3e-4, critic 128x128 lr 4e-3, batch 64, discount 0.9, replay 1e6, tau 0.1, action a in [4, 10] with CW = round(2^a - 1). Reward = frames correctly received in the epoch; state = frame loss rate of the previous epoch.

Secondary reference: [CCOD, Wydmanski and Szott (arXiv 2003.01492)](https://arxiv.org/pdf/2003.01492v4.pdf), same ns3-gym setup, reports CCOD +1.5 % (5 STAs) to +40 % (50 STAs) over 802.11, and in the dynamic 5 to 50 STA run 802.11 loses up to 28 % throughput while CCOD loses about 1 %. Also relative only.

## Repo, W&B and data

| Source | What is there | Usable numbers? |
| --- | --- | --- |
| [raoulraft/OSCAR-contention-window-RL](https://github.com/raoulraft/OSCAR-contention-window-RL) | Code only: `OSCAR_train.py`, `CCOD_train.py`, `standard_test_and_ccod_train.py`, `cw.cc`, `scenario.h`, agents. 9 commits, no releases, no data. mac-world's `ns-3.29/scratch/linear-mesh/` is this code. | No |
| W&B entity `xraulz`, project `contention_window` (named in the README) | `wandb.ai/xraulz/contention_window` redirects to a login-rendered page; no runs or reports visible to an anonymous fetch. | Unknown |
| Released logs or datasets | None found on GitHub, IRIS ([UNICT record](https://www.iris.unict.it/handle/20.500.11769/677573), no file attached) or ResearchGate. | No |
| mac-world's own W&B (`sohanroy676-vasavi-college-of-engineering/contention_window`, private) | 81 final multi-AP runs + 7 older runs. The v0.1.0 single-AP OSCAR run (`7y4kp9yr`) exists locally; whether it is among the 7 synced runs is not verified. | Yes, your data |

## Setup match: paper vs mac-world

The PHY/MAC scenario matches closely; the agent settings do not, because mac-world inherits the released code, which already differs from the paper's Table I.

| Aspect | OSCAR paper | mac-world (code) | Match |
| --- | --- | --- | --- |
| Simulator | ns-3 + ns3-gym, PyTorch DDPG | ns-3.29 + ns3-gym, PyTorch DDPG | Yes |
| PHY | 802.11ax, 20 MHz, 1024-QAM 5/6, single-user | 802.11ax 5 GHz, HeMcs11, 20 MHz, 800 ns GI | Yes |
| Channel | error-free | fixed 50 dB loss, all nodes hear all | Yes (inference) |
| Aggregation | disabled | `BE_MaxAmpduSize = 0` | Yes |
| Traffic | CBR UDP uplink, 1500 B, saturating | OnOff UDP uplink 150 Mbps/STA, 1464 B payload | Yes |
| Topology | 1 AP, 15 to 50 STAs | 1 AP x 40 STAs (v0.1.0); multi-AP 2 to 10 APs, 60 to 220 STAs | Partly |
| Run length / repeats | 15 s, 12 rounds | 15 s, 3 seeds (n=3) | Partly |
| Batch / discount / tau | 64 / 0.9 / 0.1 | 32 / 0.7 / 1e-3 | No |
| Actor lr | 3e-4 | 4e-4 | No |
| Action to CW | CW = round(2^a - 1), a in [4, 10] | CW = 2^(a+4), clamp 16 to 1024 | Close |
| Reward | frames received per epoch | normalized per-AP goodput | No |
| 802.11 baseline | standard 802.11ax BEB | `--mode beb` (standard BEB) | Yes |
| CCOD baseline | CCOD w/ DDPG | `CCOD_train.py` present, never run in mac-world | Not run |

## Comparison-ready table

The metric OSCAR reports is throughput gain over standard 802.11, so the comparable mac-world figure is each mode's paired gain over BEB in the same simulator. mac-world's `independent` mode is vanilla OSCAR deployed per AP (one agent per AP) and is the fair OSCAR baseline here; `global` is a centralized single-agent baseline (one agent, one CW for every AP, network-wide reward), not original OSCAR (definitions: [coop-v2.8.0](coop-v2.8.0.md) §0). Rows below keep the v2.2.0 table wording; read "OSCAR-style global CW" as the centralized baseline. mac-world values are from [final-results-v2.2.0](https://github.com/sohanroy676/mac-world/blob/main/docs/final-results-v2.2.0.md) (mean over 3 seeds, 95 % CI) and [baseline-v0.1.0](https://github.com/sohanroy676/mac-world/blob/main/docs/baseline-v0.1.0.md).

| Metric | OSCAR paper (1 AP) | mac-world measured | Comparable now? |
| --- | --- | --- | --- |
| Gain vs 802.11 at 15 STAs | +11 % | not run | Needs run (A) |
| Gain vs 802.11 at 50 STAs | +40 % | not run | Needs run (A) |
| Single-AP OSCAR throughput, 40 STAs | not stated | 33.9 Mibit/s policy mean, CW 117 to 315 (n=1, no paired BEB) | Partly |
| Centralized single-agent (`global`) vs BEB, 2 APs (20,40) | n/a | +33.0 ± 29.0 % (36.29 vs 27.30 Mbps) | Yes, but not OSCAR |
| Per-AP OSCAR (`independent`) vs BEB, 2 APs (20,40) | n/a | -5.6 ± 76.0 % (25.78 Mbps) | Yes |
| Centralized (`global`) vs BEB, 60 STAs over N = 2/4/6/10 APs | n/a | +32.3 / +29.5 / +31.5 / +32.2 % | Yes |
| Per-AP OSCAR vs BEB, same | n/a | +3.8 / -27.0 / -35.8 / -46.2 % | Yes |
| Fairness (Jain), 20,40 | not reported | BEB 0.913, global 0.911, independent 0.837 | mac-world only |
| Loss / collision rate, 20,40 | not reported | BEB 0.747, global 0.624, independent 0.765 | mac-world only |
| Convergence | about 300 epochs (3 s) | convergence step logged per run (`scaling_table.md`) | Yes, same 10 ms epoch |
| Delay | not reported | not measured | No |
| vs CCOD | +30 % (15 STAs), +15 % (50 STAs) | CCOD never run | Needs run (B) |

Important for the goal: per-AP OSCAR (`independent`) is at or below BEB from 4 APs on (v2.2.0, seeds 0-2) and clearly below BEB at 6x10 on fresh seeds 10-14 (-13.2 ± 2.5 Mbps). The centralized `global` baseline is the only mode with a measured gain over BEB in v2.2.0, but it is not decentralized and not original OSCAR. The relevant claim is therefore "a coordinated variant beats per-AP OSCAR": only `central` at 6x10 has a paired CI above 0 (+9.29 ± 7.73, suggestive, not confirmed); no variant beats BEB or `global` (see [claim-prereg-v2.8.1](claim-prereg-v2.8.1.md)).

Runs that would make the comparison fair (not started, each needs your go-ahead):

1. (A) Single-AP OSCAR vs BEB at 15 and 50 STAs (ideally 5 to 50 in steps of 5), 15 s, at least 3 seeds. This checks that mac-world reproduces the paper's +11 % / +40 % before claiming anything beyond it. Whether `OSCAR_multi_ap_train.py --apStaCounts 15 --mode global` runs with one AP is not verified; the fallback is the original `OSCAR_train.py` with `nWifi` set.
2. (B) Optional: CCOD via the inherited `CCOD_train.py` at the same station counts, to reproduce the paper's second baseline.
3. Optional: a paper-hyper-parameter variant (batch 64, discount 0.9, tau 0.1, actor lr 3e-4) so the OSCAR numbers come from the published settings, not only the released code.

## Not verified or not available

- Absolute OSCAR throughput in Mbps: only on figure axes; reading them off the plot would be an estimate, so none is given here.
- Full list of station counts in Fig. 2: only 15 and 50 are named in the text.
- OSCAR W&B project `xraulz/contention_window`: could not be opened (login-rendered page, API blocked from this environment). Public or not is unknown.
- Collision rate, fairness, delay and per-station results: the paper reports none.
- The paper's numbers were read from the ResearchGate full text, not the IEEE Xplore page (empty to an anonymous fetch).
- mac-world numbers were taken from the repo's docs, not re-run in this check.

## Sources

- [OSCAR paper, IEEE ICC 2023 (DOI)](https://doi.org/10.1109/ICC45041.2023.10279663) and [full text on ResearchGate](https://www.researchgate.net/publication/374931185_OSCAR_A_Contention_Window_Optimization_Approach_Using_Deep_Reinforcement_Learning)
- [UNICT IRIS record](https://www.iris.unict.it/handle/20.500.11769/677573)
- [raoulraft/OSCAR-contention-window-RL](https://github.com/raoulraft/OSCAR-contention-window-RL)
- [CCOD paper, arXiv 2003.01492](https://arxiv.org/pdf/2003.01492v4.pdf)
- mac-world: [final-results-v2.2.0](https://github.com/sohanroy676/mac-world/blob/main/docs/final-results-v2.2.0.md), [baseline-v0.1.0](https://github.com/sohanroy676/mac-world/blob/main/docs/baseline-v0.1.0.md), project review `reviews/mac-world-repo-review-2026-10-07.md`
