# Post-report TODO (after the MAC-WORLD final report)

Status: not started. Decided with the project owner on 2026-11-24: these are deferred until the final report is merged.
Labels: **fact** = read in the code, **estimate** = not measured. Mentor scenario numbers refer to the mentor's scenario list.

## 1. Mixed uplink and downlink traffic (mentor scenario 8)
- Fact: today every BSS carries constant-rate UDP uplink only; each AP has a UDP receiver and per-AP goodput is counted there (`cw.cc`).
- Work: a downlink sender on each AP and receivers on the stations; goodput counted at the stations; the CW controller must also set the AP's own CW (today it writes STA CWs); per-AP direction flag (uplink, downlink, both); new ADR; oracle grids for the new cells.
- Estimate: 1-2 days to implement and validate; about 150 runs (about 60 lab-hours) for 3-4 APs, uplink / downlink / both, 5 methods, 10 seeds.

## 2. Graded asymmetric interference and distances (mentor 2D, scenario 7)
- Fact: `--apHidden` is a yes/no switch (pairs of BSSs that cannot hear each other); no graded strengths.
- Work: per-pair path loss or AP/STA positions with a distance-based loss model; read how `--apHidden` and `--hiddenLoss` are built first (ADR-0005); keep the BSS-level loss matrix in the state.
- Estimate: about 1 day; about 100 runs (about 40 lab-hours).

## 3. OBSS-PD approximation (mentor extension)
- Fact: ns-3.29 has no OBSS-PD or BSS colour. A per-AP carrier-sense (CCA) threshold is the closest stand-in and would be a PHY change, which `CLAUDE.md` puts out of scope: needs the owner's approval and an ADR. Label as an approximation, never as OBSS-PD.
- Estimate: 2-3 days; about 100 runs (about 40 lab-hours).

## 4. Other traffic types
- TCP and bursty traffic (mentor scenario 6 lists them): UDP constant-rate and on/off windows (ADR-0006) only today.

## 5. Open items from the v4.1.0 final report
- Target worst-cell share 0.95 not met (0.85 on S4 alpha 1); Gate C failure on S2 not separated into period vs tuning; a run of the original independent per-AP OSCAR in the max-CW cells.
