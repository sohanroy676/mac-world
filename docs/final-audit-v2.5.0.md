# v2.5.0 Final audit

Date 2026-10-19. Branch `feature/v2.5.0-final-audit` off main (0ff81e1). Audit only: no code change, no rebuild needed, no long run.
Method: **C** = checked in committed files/code, **R** = re-run today on the current binary. Status: PASS / PARTIAL / FAIL.

## 1. Runs done today (one ns-3 job at a time)

| Run | Result |
|---|---|
| `./waf build --target=linear-mesh` | no-op, `'build' finished successfully (1.6 s)`, so the binary is current. waf compares content hashes; source mtimes (09:27) are newer than the binary (05:27) only because of checkout touch, nothing was recompiled. |
| `--nWifi=5 --dryRun=true --disableGym=true --simTime=2` | 10533 packets (committed value 10533), 19 s |
| `baseline_v0_1_0.py --smoke` | cumulative reward 10.59458 (committed 10.59458), 30 s |
| 2-AP demo `--apStaCounts 2,3 --mode independent ... --check` | `RESULT: PASS | steps: 30`, 30 rows x 19 W&B keys, final CW AP1 105 / AP2 161 (different per AP), 32 s |
| 10-AP small `--apStaCounts 2,...,11 --mode independent --simTime 3 --stepTime 0.1 --historyLength 20 --start_timesteps 10 --batch_size 8 --check` | `RESULT: PASS | steps: 30`, 30 rows x 75 keys, 3:50. Flags are my choice (the v1.5.0 doc elides them), so it is "same size as v1.5.0 small check", not a byte-for-byte rerun. |

## 2. Checklist

### Implementation
| Item | Status | Evidence |
|---|---|---|
| 2 AP works | PASS | R: demo check above. C: `docs/validation-v0.9.0.md`, `docs/core-v1.0.0.md` |
| 10 AP works | PASS (caveat) | R: 10-AP small check. C: `docs/scaling-v1.5.0.md` 9/9 long runs. Caveat: full-size dry association check FAILS (late association, deassoc bursts); cause traced in v2.0.0 batch D to traffic starting at t=0 plus MaxMissedBeacons (n=1), benchmarks still start at t=0 |
| AP-specific CW | PASS | R: different CW per AP in demo. C: v0.5.0 per-node `Config::Set`, CW readback; STAs round CW to 2^k-1 via beacon (documented, accepted) |
| Per-AP observations | PASS | C: `--check` Test A (`validation-v0.9.0.md`); trainer reshapes obs per AP (`OSCAR_multi_ap_train.py` `reshape_obs`) |
| Per-AP rewards | PASS | C: Test D; per-AP rewards and a checked `Global/CumulativeReward` sum (`OSCAR_multi_ap_train.py:352-367`) |
| Agents decentralized | PASS | C: independent mode builds one `DDPG` and one `ReplayBuffer` per AP (`:109-110`), distinct-replay check (`:150`). Central mode is a separate, optional `--mode` |
| No cross-AP leakage | PASS | C: per-agent replay row checks (`:221-224`), actor-input isolation check in `--check`. Not claimed: radio-level coupling between APs, which is real and intended |
| Reset works | PASS | C: `reproducibility-v2.1.0.md` (`--episodes 2` PASS, seed and reset checks) |
| Seeds/config documented | PASS | C: `reproducibility-v2.1.0.md`, `config.json` with `git_rev`; seed bug fixed in v1.1.0 |
| W&B works | PARTIAL | R: offline runs written, key counts checked. NOT done: online sync of the final runs (deferred, `wandb sync <run_dir>/run-*.wandb`). The 9 tracked `.wandb` files are offline copies |

### Evaluation
| Item | Status | Evidence |
|---|---|---|
| Standard baseline (BEB) | PASS | `baseline_beb.py`, `--mode beb`, all tables |
| OSCAR/global-CW baseline | PASS | `--mode global`, tables from v1.1.0 |
| Proposed method | PASS | `--mode independent` (negative result at N>=4: that is the finding) |
| 2 AP evaluation | PASS | `benchmark-v1.1.0.md`, n=5 at 20,40 |
| 10 AP evaluation | PASS | `scaling-v1.5.0.md`, n=3 |
| Scaling analysis | PASS | `scaling-v1.6.0.md`, recomputed from raw traces, cross-check PASS |
| Important metrics recorded | PASS | throughput, Jain, per-AP, reward, association events (v2.2.0 plots and CSVs) |
| Results reproducible | PARTIAL | Short runs byte-identical (v2.1.0). Long runs: 205 files of raw traces/logs for v1.1-v1.5 and early multi-ap dirs are tracked; the final 81 fixed-binary runs (v2.0.0+) exist only locally under `results/`, so a reader gets the tables and figures but not the raw traces for those. Rerun is possible from the documented commands. |

Cross-check: the load-sweep rows (0.5 / 1 / 150 Mbps) in the report (`technical-report-v2.3.0.md:200-202`) equal `final-results-v2.2.0.md:46-48` and `robustness-v2.0.0.md`. Wording nuance: the report headline "+29.5 % to +33.2 %" covers the saturated topologies at 150 Mbps; at 1 Mbps global is +39.9 %.

### Documentation
| Item | Status | Evidence / gap |
|---|---|---|
| README | PARTIAL | Root `README` is the stock ns-3-allinone text. `ns-3.29/scratch/linear-mesh/README.md` is the OSCAR original plus a "Multi-AP (v1.0.0)" section that predates `--mode`, the benchmark runner, results docs and `reproducibility-v2.1.0.md`. Fixed after the audit: the multi-AP section now covers `--mode`, the runner and the docs (root `README` is still the stock ns-3 text) |
| Setup instructions | PASS | `reproducibility-v2.1.0.md` (pinned versions, no machine paths). `AGENTS.md` root path fixed after the audit |
| Architecture documentation | PASS | `multi-ap-design-v0.2.0.md`, ADR-0001..0003 (ADR-0003 status updated after the audit to accepted-optional, negative result) |
| Experiment configuration | PASS | `reproducibility-v2.1.0.md`, per-doc command tables |
| Final report | PARTIAL | `technical-report-v2.3.0.md` complete; waiting for user review |
| References | **FAIL** | 21 `[REF:key]` placeholders (`grep -c REF: docs/technical-report-v2.3.0.md` = 21) until you supply them |
| Presentation | PARTIAL | `presentation-v2.4.0.md` + 14-slide artifact; title slide placeholder `[Team names · course · date]`; layout not reviewed by you or by me |
| Demo instructions | PASS | `presentation-v2.4.0.md` line ~40, rerun today: 32 s, PASS |

## 3. Upstream provenance of the import (bc6f12c)

bc6f12c is the **root commit** (3946 files); it imports ns-3.29 and opengym and adds the v0.2.0 design docs in one commit. Compared against downloads in the scratchpad (not in the repo):

- `ns-3.29/src`: `diff -r` against `ns-allinone-3.29/ns-3.29/src` from nsnam.org finds **no difference**. Top-level ns-3.29 files (excluding scratch, contrib/opengym, build, venv) also show no difference.
- `contrib/opengym`: no ns3-gym release tag matches. Closest is tkn-tub/ns3-gym commit `db016f8b3` (2022-01-18, README says "ns-3 versions <= 3.35"). Against it, `model/` and `helper/` sources are identical. Differences are limited to: `README.md` (header lines), `examples/opengym/simple_test.py` (uses `ns3env.Ns3Env()` instead of `gym.make`, i.e. a local edit or a different upstream revision), and generated/untracked files (`messages.pb.*`, `messages_pb2.py`, `__pycache__`, `egg-info`, ignored by `.gitignore`).
- Conclusion (fact): src is pristine ns-3.29; opengym core is byte-identical to that upstream commit. Inference: the example/README differences are not project logic. Whether `simple_test.py` was edited locally or matches another upstream revision was not determined, and nothing in the project runs it.

## 4. Repository hygiene
- Secrets: `git grep` for key/token/password assignments finds only placeholders (`api_key: "XXXXXXXXXXXX"` in inherited `loggers.py`, `<key from ...>` in a pre-v0.1 audit doc). No key found.
- Machine paths: `/home/pranay/...` appear only inside committed run logs under `docs/figures/v1.1.0-b3-partial/`; `/home/gloomyleader/...` in the pre-v0.1.0 audit docs; `~/college/major/...` in `AGENTS.md`. None in code.
- No tracked pcap, `cw.csv`, `wandb/` dir, venv, `__pycache__` or build output. **Tracked but against the CLAUDE.md "never commit results/" rule:** 205 files under `scratch/linear-mesh/results/` (incl. 9 `.wandb`). Memory records v1.6.0 force-committed raw traces on purpose; I did not change it.
- `.python-version`, `ns-3.29/*.pcap`, netanim files are untracked and stay uncommitted.

## 5. Open items (not blocking the code; recorded)
1. References (21) and your review of the report and deck; title slide placeholder.
2. Central-critic N=10 collapse cause: untested.
3. Traffic starts at t=0 in all benchmarks; association failures at large N are linked to it (v2.0.0 D, n=1).
4. Active-sink count for BEB: not measured.
5. W&B online sync of the final runs: deferred.
6. Fixed after the audit: project README multi-AP section, `AGENTS.md` root path, ADR-0003 status.
7. Raw data for the final 81 runs is local only.

## 6. Verdict
Implementation 9/10 PASS (W&B online sync partial). Evaluation 7/8 PASS (reproducibility partial). Documentation 4/8 PASS, 3 PARTIAL, 1 FAIL (references). Nothing in the code or results blocks submission; the open items are your inputs (references, review) plus small doc edits I can make on request.
