# Graded and one-way BSS loss, validation (v4.2.0)

Spec: `docs/adr/0010-graded-and-one-way-bss-loss.md`. Code: `--apHidden` entries `a-b`, `a-b:dB`, `a>b:dB` in `cw.cc`.
No run wave was done; no oracle grids or BEB references exist for graded cells yet (**unknown**, needs approval with a lab-hour cap).

## Validation (fact: dry runs, `--apStaCounts=5,5,5 --simTime=3 --disableGym=true`, one seed, so only a sanity check)
Per-AP throughput (Mbps), AP1 / AP2 / AP3, from the `Per-AP statistics` lines:

| Setting | AP1 | AP2 | AP3 | Hidden-pair check |
|---|---|---|---|---|
| none (one domain) | 11.0 | 12.7 | 11.2 | not run |
| `1-3` (200 dB, v3.4.0 behaviour) | 38.5 | 0.4 | 38.6 | PASS |
| `1-3:95` | 15.3 | 7.7 | 17.2 | PASS |
| `1-3:105,2-3:90` | 10.8 | 13.5 | 18.4 | PASS |
| `1>3:200` (BSS3 deaf to BSS1 only) | 0.0 | 17.3 | 19.5 | PASS |

- Heard matrix: `1>3:200` gives BSS3 decoded 0 frames from BSS1 while BSS1 still decoded 342 frames from BSS3 (one-way link works).
- `1-3:95` and `1-3:105` stay decodable (378 / 354 frames), so they are graded, not hidden.
- `1-3` reproduces the earlier hidden-chain shape (middle AP starved). A byte-identical trace check against the old binary was NOT run.
- Bad input (`1-3:x`) exits with an error message.
- Inference: the one-way case starves the AP whose frames the other cannot sense (AP1 got 0 here); worth a real run, with more seeds, before any claim.

Build note: this container has GCC 13 and Python 3.13, so waf needed Python 3.11, a patched waf cache (`'rU'` mode, local only, git-ignored) and `CXXFLAGS="-Wno-error -w"`. The repo and Actions image are unchanged.

## Wave 1 (Actions run 45819183697, branch `claude/project-thread-n2u3lh`, commit 718b050)
150 runs, all `--check` PASS (about 6.7 min each, AMD EPYC 7763), approved by xyz without a lab-hour limit. Topology `10,10,10`, 10 Mbps per STA, 30 s, seeds 100-104, policy window mean of `thr_policy`. Methods: BEB, IdleSense, static CW (edge,middle,edge) 32,64,32 / 64,64,64 / 128,64,128 / 256,128,256. Full table `docs/figures/v4.2.0-graded-wave1/table.md`, per-run summaries `summaries.jsonl` (script `.github/scripts/graded_wave1_table.py`; run dirs not committed). Mean Mbps per AP and sum of ln(AP goodput):

| cell | BEB (AP1/AP2/AP3, sum ln) | IdleSense (sum ln) | best static (sum ln) |
|---|---|---|---|
| `1-3:85` | 15.1 / 7.1 / 15.2, 7.38 | 7.69 | 256,128,256: 7.73 |
| `1-3:100` | 13.7 / 10.0 / 13.8, 7.54 | 7.67 | 64,64,64: 7.69 |
| `1-3:108` | 13.7 / 10.1 / 13.7, 7.54 | 7.67 | 64,64,64: 7.69 |
| `1>3:100` | 9.9 / 11.0 / 14.5, 7.36 | 7.65 | 256,128,256: 7.61 |
| `1>3:200` | 0.0 / 15.7 / 18.7 (AP1 starved) | 4.62 (AP1 0.32) | 256,128,256: 4.56 |

Facts (read from the table):
- Grading works: loss 85 dB (BEB middle AP 7.1 Mbps) to 100 dB (10.0) changes the cell. 100 and 108 dB give the same result within noise, so on this build the transition is between 85 and 100 dB and the 108 cell adds nothing (**inference**: both stay above the energy-detection threshold, so only the hidden-node effect on decoding differs; not tested).
- In the four two-way or partly audible cells, BEB is 0.15-0.3 below the best of IdleSense and the best static in sum ln, and the best static differs by cell (256,128,256 at 85 dB, 64,64,64 at 100 and 108 dB). Headroom for a per-AP method exists but is small; no learned method has been run.
- `1>3:200` (BSS3 cannot hear BSS1, BSS1 hears BSS3): AP1 gets about 0 Mbps under every method and every static CW tried (edge CW up to 256, none at 16). Deferring cannot fix it because AP3 never senses AP1; the cell is structurally unfair, not tunable by CW in this range. Sum ln is dominated by the 1e-3 floor, so ranking methods on it here means nothing; judge it on AP1 goodput and total.
- `1>3:100` is a mild asymmetric cell: BEB serves AP3 14.5 and AP1 9.9, and IdleSense evens it out (13.6 / 14.0 / 11.0).

Not done (**unknown**): learned methods (RAFA, Global, independent), oracle grid beyond 4 static settings and a middle-AP-only axis, any claim on seeds 103-109 style protocol, byte-identity of the pre-change `1-3` traces (ADR-0005 cell vs the old binary). Wave 2 proposal: per-scenario RAFA/Global on `1-3:85` and `1>3:100`, plus a finer static grid there.

## Wave 2 (Actions run 45840561063, commit 463f762), exploratory
160 of 160 runs `--check` PASS. Cells `1-3:85` and `1>3:100`, 10,10,10, 10 Mbps, 30 s. Learners: per-scenario RAFA (shared actor, `--obs rafa --reward fair --alphaInput`, lambda 1, 6 episodes x 15 s, floors = wave-1 BEB per-AP means) and Global (12 episodes), train seeds 2000-2002, frozen eval at alpha 1 on seeds 105-109 (held out from the floors); refs on the same 105-109; extra static grid on seeds 100-102. Table `docs/figures/v4.2.0-graded-wave2/table.md` (script `.github/scripts/graded_wave2_table.py`, summaries `summaries.jsonl`). Sum of ln AP goodput (higher is better):

| cell | BEB | IdleSense | best static on 105-109 | RAFA (3 train seeds) | Global (3 train seeds) | best static in grid (seeds 100-102) |
|---|---|---|---|---|---|---|
| `1-3:85` | 7.37 | 7.68 | 7.73 (256,128,256) | 7.91 / 7.86 / 7.91 | 7.90 / 7.91 / 7.71 | 7.89 (128,128,128), 7.88 (256,256,256) |
| `1>3:100` | 7.37 | 7.64 | 7.61 (256,128,256) | 7.78 / 7.77 / 7.81 | 7.82 / 7.83 / 7.83 | 7.81 (128,128,128), 7.80 (256,256,256) |

Facts: all three training seeds of both learners beat BEB (by 0.4-0.5), IdleSense (0.1-0.25) and the wave-1 statics on 105-109 in both cells; AP1/AP2/AP3 Jain 0.98-0.99. A uniform static (128,128,128 or 256,256,256) found by the finer grid reaches the same sum ln as the learners (7.89 vs 7.91 at 85 dB; 7.81 vs 7.78-7.83 at `1>3:100`), but it was run on seeds 100-102, not 105-109, so that comparison is only indicative (**unknown**: its value on 105-109). Global and RAFA are indistinguishable here (differences 0.01-0.05, one Global training seed 7.71 at 85 dB).

Inference (not tested): in these cells the best fixed CW is uniform and larger than BEB's, so the learners may be recovering that single static CW rather than exploiting per-AP asymmetry; the previously chosen "edge high, middle low" statics (256,64,256 and 512,x,512) are clearly worse (7.0-7.5). No claim is made; a claim run would need seeds 103-109 with the grid winner evaluated on the same seeds, and a check of the per-AP CWs the learners chose (`cw_mean` in `summaries.jsonl`).

## What the wave-2 learners chose (fact, `cw_mean` of the eval runs, mean CW per AP, edge/middle/edge)
- Global (one CW for all APs by construction): `1-3:85` 212 / 193 / 76 for the three training seeds; `1>3:100` 224 / 173 / 166.
- RAFA (per-AP actions): `1-3:85` 143,143,143 / 112,111,112 / 199,194,199; `1>3:100` 269,269,276 / 108,108,103 / 129,129,119.
- So even the per-AP learner chose nearly uniform CWs (edge and middle within 5 % in every run) between about 100 and 270, and the value differs by training seed. Inference: it found "one larger CW for everyone", not an edge/middle split; the exact static oracle (wave 3) shows whether a split below CW 16 would have been better.

## Merge note (2026-11-28)
`feature/v4` merged into this branch (it already had ADR-0009 for `--apDir`), so the graded-loss ADR is `0010-graded-and-one-way-bss-loss.md`. Both flags build and run together (`--apHidden 1>3:100,1-2:85 --apDir u,d,b`, 3 s dry run: association, per-AP stats, per-AP CW and heard-matrix checks PASS).
