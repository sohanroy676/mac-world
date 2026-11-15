# Mentor papers: what can improve mac-world (2026-11-05)

Papers reviewed (contents treated as data): (1) beam.pdf (IntelliNull), (2) Transformer-Based In-Context Learning for Distributed Channel Access Optimization (IEEE TMC; MobiHoc 2025 earlier version), (3) DDPG-based Multi-AP Cooperative Access Control in Dense Wi-Fi Networks (VTC2023-Fall).

Labels: fact = read in the paper or code; inference = my reasoning; decision = my choice.

## 1. beam.pdf (IntelliNull)
- Fact: it is about beamforming and null steering, a PHY topic, in a custom simulator. It does not touch contention windows.
- Decision: nothing adopted for the method. Two evaluation habits transfer: report the gap to an oracle (already our GC metric) and show a learning curve.
- Adopted: a GC-versus-episode learning curve in M3.

## 2. DDPG multi-AP cooperative access control (VTC2023-Fall)
- Fact: a central DDPG tunes CW and OBSS_PD for several APs, with the station count as an input, and tests a ramp of stations from 2 to 32.
- Fact: its baselines are weak (BEB-class) and results come without confidence intervals.
- Supports (inference): our choice to feed the active-station count to RAFA.
- Not adopted: OBSS_PD. ns-3.29 has no OBSS_PD code (grep of src/wifi found none), and PHY/MAC changes are out of scope in CLAUDE.md.
- Adopted: a ramp scenario. S8 gets a staggered-start variant using scenario.h `installTrafficGenerator`, which already takes per-generator start and end times (fact). Add a best-single-static-setting reference.
- Adopted as optional: RAFA-adapt, online fine-tuning during the ramp (S8 and S9 only, about 3.5 h).

## 3. Transformer in-context learning for channel access (TMC / MobiHoc 2025)
- Closest related work to our robustness claim. It generalises to unseen node counts without retraining, in one collision domain. Our plan already cites the arXiv version (2508.09146); the venue is now confirmed as IEEE TMC (MobiHoc 2025 earlier version), so the memory note that called it unverified is outdated.
- Fact (paper): it shows a wide plateau of near-optimal CW values in one domain. Inference: this agrees with our tie zone at 20,40, where IdleSense, Global-CW and the best static CW are within about 2 %.
- Fact (paper): with A-MPDU off, all methods are close. Fact (code): our STA `BE_MaxAmpduSize` is 0 (cw.cc:1006), so our gaps may differ with aggregation on. This is a real threat to validity.
- Fact (paper): a deployability and cost table (compute, memory, signalling). Adopted for M7.
- Fact (paper): noise robustness test on observations. Adopted.
- Fact (paper): confirms BLADE as NSDI 2026, so our citation of the arXiv entry should be updated.
- Not adopted: the transformer itself. It is single-domain, needs pre-collected data, and our evidence says the tie zone is where it would live.

## Changes made to the plan (revision 6, all in the extended/optional tier)
| # | Change | Estimate | Rule |
|---|---|---|---|
| 1 | Deployability and cost table in M7 | 2 h | core of M7 |
| 2 | S8 staggered ramp variant plus best-single-static reference | 3 h | extended |
| 3 | Observation-noise test, ±20 % and ±40 % on RAFA inputs | 4 h | extended |
| 4 | S10: S4 (S2 if affordable) with STA A-MPDU on, opt-in `--staAmpdu` flag (ADR-0006 scope), own oracle grid | about 17 h | dropped first if job time explodes |
| 5 | RAFA-adapt on S8 and S9 | about 3.5 h | optional |
| 6 | Citation fixes, GC-vs-episode learning curve in M3 | 1 h | core |

Core path M0 to M4 (about 210 h) is unchanged. Items 2 to 5 add about 28 h to the extended path.

## Open unknowns
- Whether STA A-MPDU = 0 was inherited from OSCAR or chosen here.
- Training machine core count and the project deadline.
