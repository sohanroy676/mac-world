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
