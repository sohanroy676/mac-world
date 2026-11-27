# Wave U4: downlink signal for kwdirect and the learned per-scenario method (v4.2.0)

Branch `claude/project-thread-qtjqjo`, PR #4. Scripts: `.github/scripts/apdir_u4_batch.py`, `apdir_u4_analyse.py`, `apdir_u4_learned_analyse.py`. Details: `uplink-downlink-u4p-v4.2.0.md` (pilot), `uplink-downlink-u4l-v4.2.0.md` (learned).

## What was built
- `--lyEtaMin`, `--lyBestDecay` (kwdirect L2 guard; 0 = old behaviour) and a per-run print of updates, reverts and eta.
- `--rafaDlObs` (RAFA input for `d` APs: Retry = failed attempts / (failed + delivered), active = STA count, because the cw.cc retry and active fields are uplink-only).
- `--cwLo 4` now allowed with `--mode shared`, with the CW start exponent and the first RAFA CW input corrected for `--cwExpLo` below 0 (identical output at the default range).

## Findings (seeds 0-2 for kwdirect pilots, 103-110 / 103-104 for the learned method; no claims)
- **The kwdirect freeze has a mechanism, but fixing it does not help.** In the old guard the step size halves on every revert and reaches 1e-4 to 1e-22 (U4 pilot, L2 lines in the log). With an eta floor and a best-utility decay, eta stays at 0.1-0.25, and the downlink share stays the same: d4 alpha 1 0.14-0.15, d3 alpha 1 0.42-0.45, alpha 0 about 0 (d3 -0.05, d4 0.13).
- **Longer runs (180 s), no offset shrinkage, larger eta (0.5) and delta (0.8) do not help either** (48 shrink-free runs: d3 alpha 1 0.33-0.43, d4 0.13-0.14). My inference: on the downlink cells the throughput signal is flat or too noisy for a few dozen SPSA updates to find the low-CW middle point; this is not a tuning problem.
- **Learned per-scenario RAFA (4 training seeds, none selected):**
  - uplink u3 alpha 1: mean share 0.76 (0.52-0.95) against kwdirect 0.97.
  - both b3: 0.56 (0.32-0.80) against kwdirect 0.90. m3: 0.67 (0.31-0.89, one seed breaks a floor) against kwdirect 0.75.
  - b4: 0.52 (0.38-0.67, three seeds finished) against kwdirect 0.93.
  - **downlink d3: 0.20 (0.17-0.30), d4: 0.16 (all four seeds identical)**, i.e. it ends near BEB, like kwdirect.
  - So the learner is no better than kwdirect anywhere and high-variance across training seeds. It also does not solve downlink.
- **Conclusion:** on the downlink chain cells only the exact static point reaches the oracle gain; the online methods tried (kwdirect with several variants, RAFA) reach about 0.15-0.45 of it. A method with a model of the hidden-node structure (or direct collision-based CW setting) would be needed; not attempted.

## Caveats
- Job `u4-b4-rafa-t2000` is missing: its pack hit the 6 h GitHub job limit and was cancelled (b4 evals take about 1000 s each). b4 has 3 training seeds.
- n is 2 seeds for alpha 0 and 4 in the learned wave, 8 seeds for alpha 1; kwdirect and static come from C1 on the same seeds. Selection seeds (0-2) were not used for the learned method.
- The RAFA gp input still divides by the offered load; for `b` APs this may saturate (not changed).
- Pilot reference values U_BEB / U_static for seeds 0-2 are copied from `uplink-downlink-u3-v4.2.0.md`.
