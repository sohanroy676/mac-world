# Graded and one-way BSS loss, validation (v4.2.0)

Spec: `docs/adr/0009-graded-and-one-way-bss-loss.md`. Code: `--apHidden` entries `a-b`, `a-b:dB`, `a>b:dB` in `cw.cc`.
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
