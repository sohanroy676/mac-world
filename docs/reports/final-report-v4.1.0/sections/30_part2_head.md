# Part II. The MAC-WORLD project

This part describes the project behind Part I: the problem, the simulator and the metrics, every controller that was compared, what each version of the project found, and the complete set of results up to version v4.1.0. Statements are facts taken from the result files unless they are marked as inference. All numbers are generated from the committed result files by the build script described in the reproducibility section.

## Executive summary

- **What MAC-WORLD is.** An ns-3.29 simulation of several 802.11ax access points (APs) sharing one 20 MHz channel, in which the contention window (CW) of every AP is controlled. It extends OSCAR (a single-AP DDPG controller) to N APs and compares it with the standard binary exponential backoff (BEB), published rule-based controllers, learned controllers and static optima.
- **Headline finding on the original question.** Applying OSCAR's idea to several APs works only when one agent sets a shared CW (Global-CW OSCAR: about +30 % aggregate throughput over BEB in saturated networks at 2 to 10 APs). Independent per-AP OSCAR agents, each optimizing its own goodput, are on par with BEB at 2 APs and fall below it from 4 APs on (-27 % at 4 APs, -46 % at 10 APs).
- **Beyond a shared CW.** With a fair utility instead of raw throughput, and with a hidden-node topology (a chain of three BSSs in which the outer two cannot hear each other), a per-AP CW is necessary: the middle BSS is starved under BEB and under any common CW.
- **Best online method at the end of the project (v4.1.0).** `kwdirect`, a central online search on the CW of every AP, reaches 0.93 to 1.02 of the distance between BEB and the validated static optimum in 8 of 9 cells and 0.85 in the worst cell (target 0.95 not met). It beats DAC (Patras et al.), BLADE, IdleSense, the original KW and the learned controllers in their weakest cells. It is a central controller (it sees every AP's goodput), unlike per-AP OSCAR agents.
- **Honest limits.** All results are simulation results (ns-3.29, constant-rate UDP uplink, one channel). The simulator lets the AP write an exact CW to its stations every 10 ms; when the update is restricted to beacon timing and rounded to 2^k-1 (Gate C), the worst-cell share falls to 0.41.
{{include:generated/exec_new.md}}

## Reading guide
- Part I answers the mentor's eight scenarios, one by one, with new simulations run for this report (seeds 400 to 409).
- Part II explains the system (sections 1 to 3), the earlier two-AP and scaling studies (section 4), the hidden-node and fairness studies (section 5), the final max-CW study (section 6), a single comparison of BEB, OSCAR and the other optimizers (section 7), other configurations (section 8), limits (section 9) and how to reproduce everything (section 10).
