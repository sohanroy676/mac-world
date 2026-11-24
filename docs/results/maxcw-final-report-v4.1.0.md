# Max-CW optimisation: final report (v4.1.0)

Plan: `docs/planning/max-cw-optimization-plan-2026-11-14.md`. Scope of this report: cells S2, S4, S5a at alpha 0, 1, 4 (9 cell-alpha pairs). Other cells (S7/S8 delay cells) are not covered here.

## Question and metric
- Question: how close can an online CW controller get to the best static CW per cell, and does it beat BEB and the learned OSCAR-family controllers?
- Metric: share = (U - U_BEB) / (U_ceiling - U_BEB), BEB paired per seed, second half of each run (`thr_half2`). 0 = BEB, 1 = validated ceiling. A seed with any AP below 0.95 x its floor counts as 0.
- Primary criterion: worst-cell share of the best online candidate, target 0.95. The target was a hypothesis set in advance.

## What was built (project code, not upstream)
- Measurement modes: CW bounds, hold, schedules, PHY durations, static CWmin-only (`docs/design/measurement-modes-v4.1.0.md`, ADR-0008). Measured Tc 242 us, Ts 226 us.
- Controllers (`ap_layered_v4_1_0.py`): L1 DAC loop, L2 KWPlus (SPSA-style search on log2 CW with floor penalty and accept/revert guard), L3 max-weight muting (coord, qcsma), `kwdirect` (L2 without L1). kwdirect and coord see all APs' goodput (central, breaks per-AP isolation by design).
- Gate C mode (`--cwGateC`): CW applied every 100 ms and rounded to 2^k-1; no beacon delay modelled.
- Pipeline: image build, packs, wave workflows, collector; all runs on the owner's own GitHub account, results hash-checked (0 mismatches).

## Results
1. Ceilings (seeds 200-209, U): S2 39.72 / -24.83 / -69.27; S4 77.28 / 21.39 / -1.54; S5a 49.98 / 13.28 / -4.24 for alpha 0 / 1 / 4.
2. Tournament (Wave 3a, seeds 300-309): kwdirect best worst-cell share 0.90; learners and other rivals far lower in some cell (`wave3a-v4.1.0.md`).
3. Confirmation (Wave 4a, seeds 103-122, 300 s, 760/760 runs; `wave4a-v4.1.0.md`):
   - kwdirect: worst 0.85 (S4 alpha 1); the other 8 cells 0.93-1.02; feasible on 20/20 seeds in every cell. Better than BEB in all 9 pairs.
   - Target 0.95 NOT met.
   - Versus the static F1 point: not shown non-inferior (IU p 0.83); worse in 7 cells by at most 0.065, better in 2. F1 is a tuned static reference, not an online method.
   - Versus DAC514: better (p < 0.001); DAC is infeasible on every S4 and S5a cell.
   - Versus learners (each run only on its tuned cells): PF/RAFA fail on S4 alpha 0 (about -1.9); Global ties on S2 (0.97-0.98); PF is slightly ahead on S5a alpha 1/4 (no test run); PF 0.92 and RAFA 0.94 beat kwdirect 0.85 on S4 alpha 1.
   - Gate C (100 ms, 2^k-1): worst share 0.41; S2 cost -0.50 to -0.56 and many seeds infeasible (9-13 of 20); S4 cost -0.09 to -0.28; S5a -0.01 to -0.19.

## Limitations and unknowns
- Target missed by 0.10 in one cell (S4 alpha 1); not tuned further.
- Gate C failure on S2: not separated into "100 ms period itself" versus "controller untuned for slow updates". Unknown.
- kwdirect is a central controller (sees all AP goodputs), unlike per-AP OSCAR agents; comparisons with isolated agents are not like for like.
- No run of original independent per-AP OSCAR in this wave; earlier audit found independent agents no better than BEB.
- Learner seeds were chosen on seeds 0-2; tournament and confirmation seeds are out of sample. Rival tuning on seeds 0-3, kwdirect per-alpha settings: slight advantage to kwdirect.
- Three Actions runs were cancelled by GitHub (cause unknown); lost jobs were rerun, data complete.
- Novelty versus Gawlowicz et al. (KW) and related work not checked line by line.

## Reproduce
`ns-3.29/scratch/linear-mesh/confirm_v4_1_0.py --prefix w4a <merged summaries.jsonl>`; batches in `.github/waves/w4/`; data on branch `wave-collected`.
