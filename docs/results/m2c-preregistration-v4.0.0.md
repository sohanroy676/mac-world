# M2c pre-registration: learned rivals retrained on Actions CPU (written before any M2c result)

Date: 2026-11-10. Jobs: `.github/jobs/m2c.json` (30 jobs, 138 commands, GitHub Actions CPU).

## Why
- The M2 learned rivals (Global, PF learner, CCOD) were trained on the lab machine, which uses the GPU when present.
- RAFA is trained on Actions CPU, and learned runs are not bit-identical across platforms (step 0).
- So every learned run in a comparison is retrained on Actions, as the brief requires. Non-learned runs are
  byte-identical across platforms, but they are rerun here anyway, so the GC tables for this batch share one results set.
- Plan M2c: Global and the PF learner at 12 episodes x 3 seeds, and CCOD at 3 seeds.
  The lab had CCOD seed 1 only, and here all 3 seeds are retrained on CPU.

## Design
- **Cells:** S2 (20,40, load 10, `--rewardNorm 150`), S4 (10,10,10 hidden 1-3, load 10, `--rewardNorm 150`),
  S5a (S4 with `--apLoads 150,150,1`).
- **Training:** 12 episodes x 15 s, `--varySeeds`, python seeds 2000-2002 (ns-3 2001+), `--check`.
  - Global: `--mode global`.
  - PF learner: `--mode independent --reward pf`.
  - CCOD: `--mode ccod --historyLength 300`, as in M2.
- **Stage 1 evaluation:** frozen, 30 s, seeds 100-102.
- **References** at the same seeds: BEB, IdleSense, static oracles (S2 512,512; S4 128,64,128 and 64,64,64;
  S5a 128,128,128).
- **Scoring:** GC with `gc_analysis.py`, tag prefix `m2c-`, at alpha 0, 1 and 4. The alpha-4 oracle is the best feasible
  static among those run.

## Selection rule (fixed now)
- For each method, cell and alpha, the strongest seed is the one with the highest mean GC over seeds 100-102.
  Feasible seeds come first; an infeasible seed is chosen only if no seed is feasible.
- That seed runs at n = 10 (seeds 100-109) in M4. Picking per cell and alpha is the most generous choice for the rivals.
