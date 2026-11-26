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
