# v1.1.0 batch 3 (20,40) — PARTIAL (2026-10-13)

Only `20,40 beb seed 0` completed (PASS, 2500 s). `20,40 global seed 0` was killed by a terminal restart
(~14:50) and is NOT in the manifest. Remaining 8 runs: beb s1 s2; global s0 s1 s2; independent s0 s1 s2.
Files: `manifest.csv` (all PASS rows incl. batch 2), `20,40-beb-s0.log`, `20,40-beb-s0-trace.csv`, `20,40-beb-s0-config.json`.
No aggregate/figures yet. Do NOT treat this dir as the final b3; the final one is `docs/figures/v1.1.0-b3`.

## 20,40 BEB seed 0 (summarize_run.py, policy window, Mbps)
AP1 8.853 | AP2 18.392 | Global 27.245 | Jain 0.891 | CW 16 throughout | loss 0.747 | reward 0.003
Deassociation: 1 event (STA nodeId=42 off AP2 at t=1.144 s) in the BEB run — so it is NOT trained-mode-only.
