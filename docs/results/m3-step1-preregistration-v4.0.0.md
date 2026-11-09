# M3 step 1 pre-registration (written before any step 1 result)

Date: 2026-11-09. Code: `OSCAR_multi_ap_train.py` on `feature/v4` (`--mode shared --obs rafa --reward spf`). Jobs: `.github/jobs/step1.json` (30 jobs on GitHub Actions CPU).

## Design
- Cells: S4 (`10,10,10 --apHidden 1-3`, 10 Mbps per STA, `--rewardNorm 150`), S5a (`10,10,10 --apHidden 1-3 --apLoads 150,150,1`), S2 (`20,40`, 10 Mbps, norm 150). Alpha 1 only.
- Training: 6 episodes x 15 s, `--varySeeds`, python seeds 2000, 2001, 2002 (ns-3 seeds 2001 and up), warm-up 300 steps, defaults otherwise (Gaussian N(0, 0.1), discount 0.7, batch 32, 128-unit nets), `--check` on.
- Evaluation of each trained actor (frozen, no noise): 30 s, selection seeds 0, 1, 2 (never used for training). References on the same seeds and length: BEB, IdleSense, static oracle (S4 128,64,128; S5a 128,128,128; S2 512,512; from M1 at alpha 1). GC, floors and feasibility use `gc_analysis.py` (5 % floor slack, policy window after 300 steps).
- Noise test: the same S4 and S2 jobs with `--noiseDist gumbel` (centred, same SD) and `gumbel-raw` (Gumbel(0, 0.1), uncentred), same three training seeds.

## Decision rules (fixed now)
- G1 (S4): per training seed, ratio = mean edge CW (AP1, AP3) / middle CW (AP2) over the policy window and the three eval seeds. Pass if the ratio is >= 2 in at least 2 of 3 seeds.
- G2 (S2): per training seed, mean GC over the three eval seeds. Pass if >= 0.86 (IdleSense 0.91 minus 0.05) in at least 2 of 3 seeds and the run is floor-feasible.
- S5a: reported, no gate.
- Gumbel adoption: adopt `gumbel` (or `gumbel-raw`) only if, in both S4 and S2, its GC is above the Gaussian GC for every one of the 3 matching training seeds and the mean gain over the 3 seeds is >= max(0.05, one SD of the Gaussian per-seed GC over the 3 seeds), in the same cell. Otherwise the default stays Gaussian.
- Failures follow the plan's kill rules (G1 fails: independent actors for fixed topologies; G2 fails: add one idle-target-error input, else S2 is RAFA's weak cell). No further tuning on the selection seeds beyond what the kill rules allow.
- The rule is a screen on 3 training seeds and 3 eval seeds; it is not a claim test.
