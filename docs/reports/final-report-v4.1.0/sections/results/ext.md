### Result for this extension

**Status: not available in version v4.1.0; no experiment was run.**

- **Fact.** ns-3.29, the simulator used here, has no OBSS-PD (overlapping-BSS packet detect) and no BSS colour. Joint CW and OBSS-PD control therefore cannot be implemented as stated.
- **Closest stand-in.** A per-AP carrier-sense (CCA) threshold that the controller sets next to the CW. This is a change to the PHY, which the project's design rules place out of scope for version 1, so it needs the owner's approval and a design record first. If built, it would be reported as an approximation of OBSS-PD, never as OBSS-PD itself.
- **Plan.** About two to three days of work and about 100 runs (about 40 lab-hours). It is the third item of the post-report list and is on the roadmap.
- **What the results of this report say about it.** Nothing directly. What they do show is how much a per-AP CW matters in hidden-node topologies (Scenario 7 and Section 5 of Part II); that is the part of the problem an OBSS-PD threshold would also act on.
