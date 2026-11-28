# Post-report TODO (after the MAC-WORLD final report)

Status: item 1 simulator support built 2026-11-26 (`--apDir`, ADR-0009, `docs/results/uplink-downlink-v4.2.0.md`); waves U1, U1c and U2 run on the owner's Actions (2286 runs, selection seeds 0-2, `docs/results/uplink-downlink-u1-v4.2.0.md`, `-u2-`); owner set no lab-hour cap on 2026-11-26. Not done: kwdirect retune for downlink, learned method, confirmation seeds. Items 2-5 not started. Decided with the project owner on 2026-11-24: these are deferred until the final report is merged.
Labels: **fact** = read in the code, **estimate** = not measured. Mentor scenario numbers refer to the mentor's scenario list.

## 1. Mixed uplink and downlink traffic (mentor scenario 8)
- Fact: today every BSS carries constant-rate UDP uplink only; each AP has a UDP receiver and per-AP goodput is counted there (`cw.cc`).
- Done 2026-11-26: items below except oracle grids and the run wave. Correction: `setApCw` already wrote the AP's own CW (BSS node 0 is the AP), so no controller change was needed.
- Work: a downlink sender on each AP and receivers on the stations; goodput counted at the stations; the CW controller must also set the AP's own CW (today it writes STA CWs); per-AP direction flag (uplink, downlink, both); new ADR; oracle grids for the new cells.
- Estimate: 1-2 days to implement and validate; about 150 runs (about 60 lab-hours) for 3-4 APs, uplink / downlink / both, 5 methods, 10 seeds.

## 2. Graded asymmetric interference and distances (mentor 2D, scenario 7)
- Fact: `--apHidden` is a yes/no switch (pairs of BSSs that cannot hear each other); no graded strengths.
- Work: per-pair path loss or AP/STA positions with a distance-based loss model; read how `--apHidden` and `--hiddenLoss` are built first (ADR-0005); keep the BSS-level loss matrix in the state.
- Estimate: about 1 day; about 100 runs (about 40 lab-hours).

## 3. OBSS-PD approximation (mentor extension)
- Fact: ns-3.29 has no OBSS-PD or BSS colour. A per-AP carrier-sense (CCA) threshold is the closest stand-in and would be a PHY change, which `CLAUDE.md` puts out of scope: needs the owner's approval and an ADR. Label as an approximation, never as OBSS-PD.
- Estimate: 2-3 days; about 100 runs (about 40 lab-hours).

**Status 2026-11-27:** item 1 built and run (ADR-0009, waves U1-U3, C1; docs/results/uplink-downlink-*). Wave U4 done (kwdirect guard variants, learned RAFA): neither reaches the downlink oracle; closed 2026-11-28 by the owner: downlink reported as a limit (ADR-0009 Outcome); a model-based downlink method was not built (about 2-3 days, research risk).

## 4. Other traffic types
- TCP and bursty traffic (mentor scenario 6 lists them): UDP constant-rate and on/off windows (ADR-0006) only today.

## 5. Open items from the v4.1.0 final report
- Target worst-cell share 0.95 not met (0.85 on S4 alpha 1); Gate C failure on S2 not separated into period vs tuning; a run of the original independent per-AP OSCAR in the max-CW cells.
