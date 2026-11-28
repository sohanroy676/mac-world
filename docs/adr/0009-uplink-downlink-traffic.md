# ADR-0009: Per-AP uplink / downlink / both traffic

## Status
Accepted as an opt-in simulator flag (`--apDir`). Default flags reproduce all earlier runs byte-for-byte (checked 2026-11-26, see `docs/results/uplink-downlink-v4.2.0.md`).

## Date
2026-11-26

## Context
Every BSS carried constant-rate UDP uplink only (STA to AP). Mentor scenario 8 asks for mixed uplink and downlink traffic. In the code (fact), `setApCw` already writes the AP's own BE CW as well as the STAs' (BSS node 0 is the AP), so no controller change was needed, which differs from `docs/planning/post-report-todo.md` item 1.

## Decision
`cw.cc --apDir=u,d,b` (one entry per AP): `u` uplink (default), `d` downlink, `b` both.
- Uplink flow: OnOff on the STA, UdpServer on the AP (unchanged).
- Downlink flow: one OnOff per STA on the AP (same per-STA load, same on/off window as `--staSchedule`), UdpServer on the STA. The AP is one contender for all of its BSS's downlink traffic.
- `b`: both flows per STA, each at the per-STA load, so the BSS offers twice the load. The reward divisor doubles for that AP (cw.cc and the trainer's mirror `dir_scaled`), so reward stays goodput / offered load.
- Per-AP goodput counts every UdpServer of the BSS (AP sinks and STA sinks) through the same per-AP Rx trace, so goodput is received bits in both directions.
- Trainer: `--apDir` and the per-scenario `apDir` key in `--scenarioPool` JSON.

## Alternatives considered
- Extra downlink load on top of a fixed uplink load per STA: needs a second load parameter; the per-direction load is simpler and `--apLoads` still sets it.
- TCP or bursty downlink: separate item (todo 4).

## Consequences
- With `b` and `d` the AP is a single saturated contender (one CW) against many STAs, so the BSS split depends strongly on direction (see the results doc).
- `--extraTraces` retry rate and active-STA count are measured from frames the AP decodes, so they describe uplink only. In `d` they read zero or near zero. Not fixed here.
- Delay measurement works for both directions (packet uid match); flow-monitor per-AP sums accept AP-to-STA flows of the same BSS.
- Not changed: association, PHY, MAC, mobility.

## Outcome (2026-11-28, decided by the owner)
Waves U1-U4 and C1 (about 4,500 runs, `docs/results/uplink-downlink-*-v4.2.0.md`). Findings with their reasons:
- BEB starves the middle AP of the 3-AP chain in every direction; IdleSense is no better; DAC is about level with BEB.
- Exact low-CW static (middle AP CW 4-12) is the oracle. On uplink, both and mixed cells kwdirect reaches 0.75-0.97 of the static gain on held-out seeds 103-122 (C1).
- **Downlink is a documented limit.** kwdirect gets about 0.15-0.45 of the static gain on d3/d4 (alpha 1) and about 0 at alpha 0. Reasons found: (1) the L2 guard halves the step size on every revert, down to 1e-4 or less (fixed by `--lyEtaMin`/`--lyBestDecay`, no gain); (2) retune of eta/delta/tau (27 settings), 180 s runs, no shrinkage, larger steps (about 130 variants) change nothing. Inference: the downlink throughput signal is flat or too noisy for a few dozen SPSA steps.
- Learned per-scenario RAFA (`--rafaDlObs`, CW 4-1024, 4 training seeds per cell, none selected) is never better than kwdirect and varies between training seeds (alpha 1 mean share: u3 0.76, b3 0.56, m3 0.67, b4 0.52, d3 0.20, d4 0.16). It also ends near BEB on downlink.
- Not done, by decision: a model-based downlink method (uses the hidden-node structure to set the middle AP CW; about 2-3 days, research risk, needs topology knowledge the online methods do not use). Downlink is reported as a limit.
- `--rafaDlObs` exists because the cw.cc retry rate and active-STA count are uplink-only; with it, retry = failed attempts / (failed + delivered) and active = STA count for `d` APs. Off by default.
