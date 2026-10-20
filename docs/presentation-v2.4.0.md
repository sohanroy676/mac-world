# v2.4.0 Final presentation and demo

Source: `docs/technical-report-v2.3.0.md` (tag v2.3.0) and `docs/figures/v2.2.0/`. No new benchmark runs.
Deck: private slides artifact https://claude.ai/artifact/5XPK3JfEWvoZjAdJpMb6AY (14 slides, figures uploaded from `docs/figures/v2.2.0/`; only the owner can open it until shared). Title slide has a `[Team names · course · date]` placeholder. Talk length about 12–15 min, 14 slides + backup.

## Slide outline

| # | Slide | Source |
|---|---|---|
| 1 | Title | report title |
| 2 | Problem: CW in dense multi-AP WLANs | §2–3, §6 |
| 3 | Original OSCAR and what its code does (state = 1 scalar, lr, τ) | §7 |
| 4 | Original OSCAR vs proposed system | §7 vs §9, §16 |
| 5 | Architecture: N APs → local actor/critic → per-AP CW → one shared ns-3 | §9–10, §15 |
| 6 | RL formulation: obs = own loss, CW = 2^(4+6(a+1)/2) in 16..1024, reward = own normalized goodput | §11–14 |
| 7 | Modes: BEB, Global-CW, Independent (Central = appendix) | §16, §19 |
| 8 | Setup: 81 fixed-binary runs, n = 3, 95 % CI, 4 experiments | §18 |
| 9 | Result 1: 20,40 at 150 Mbps | §20.1; `main-20-40/aggregate_throughput.png`, `cw_traces.png` |
| 10 | Result 2: scaling at 60 STAs, N = 2..10 | §21; `fixed60-scaling/aggregate_vs_n.png`, `paired_delta_vs_n.png` |
| 11 | Fairness at large N | `fixed60-scaling/min_ap_vs_n.png`, `jain_vs_n.png` |
| 12 | Robustness: imbalance and load | §20.2–20.3; `load-sweep/load_sweep.png` |
| 13 | Takeaways (fact vs inference) and limitations | §22–23 |
| 14 | Future work, central critic negative result, Q&A | §24, App. A |

Backup: `convergence.png`, `reward.png`, per-AP throughput, App. B/C.

Numbers to state exactly (report §20–21): Global-CW +33.0 ± 29.0 % at 20,40; Independent −5.6 ± 76.0 %.
At 60 STAs: Global +29.5 % to +32.3 % at every N; Independent +3.8 ± 27.2 % (N=2), −27.0 ± 21.8 % (N=4), −35.8 ± 109.7 % (N=6), −46.2 ± 12.2 % (N=10).
Global-CW breaks per-AP isolation, so it is an upper reference, not a deployable method.

## Demo (live part about 35 s)

A full 15 s run takes 842–1054 s (`docs/figures/v2.2.0/fixed60-scaling/scaling_table.md`), so it is never run live.

1. `pgrep -x linear-mesh` must print nothing (one ns-3 job at a time).
2. From `ns-3.29/scratch/linear-mesh`:

```bash
../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --mode independent \
  --simTime 3 --stepTime 0.1 --historyLength 20 --start_timesteps 10 --batch_size 8 --check
```

3. Rehearsal 2026-10-19: wall time 32.7 s, `RESULT: PASS | steps: 30`, W&B check 30 rows × 19 keys, offline run written.
   AP1 and AP2 chose different CWs on every logged step (step 20: 66 vs 285; step 30: 105 vs 161), with per-AP reward and loss.
4. Show from committed files: `main-20-40/cw_traces.png`, `per_ap_throughput.png`, results tables.
5. W&B: the demo run is offline only (syncing it needs the workaround in `docs/final-results-v2.2.0.md` §5); show the local run summary printed at the end. The 81 final runs are online in project `contention_window` (tag `final-v2.2.0`).
6. If the live run fails: continue with slides and committed figures.

Note: 3 s of simulated time shows mechanics only (per-AP CW, isolation, W&B logging), not the benchmark result.
