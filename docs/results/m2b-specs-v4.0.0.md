# M2b: new rivals, specs, decisions and job plan (written before any M2b result)

Date: 2026-11-12. Code: branch `feature/v3.8.0-m2b` (`ap_controllers.py`, `drlcw.py`, `drlcw_refs.py`, trainer modes `ucbctx`, `dac`, `drlcw`, cw.cc `--delayWindow`).
Labels: **fact** = read in a source or measured here, **decision** = my choice, **inference** = my reasoning, **unknown** = not checked.

## Sources read (fact)
- **drlCW:** Yan, Du, Zhang, Dong, "Deep Reinforcement Learning based Contention Window Optimization for IEEE 802.11bn" (the mentor's PDF, read in full 2026-11-11).
- **Patras DAC and Eq. 18:** Patras, Banchs, Serrano, Azcorra, IEEE TMC 10(6), 2011 (typeset PDF uploaded by xyz, equations read from the page image 2026-11-11).
- **BLADE (NSDI 2026):** the proceedings PDF with Appendices E and I was uploaded on 2026-11-13 and read in full; built, see the BLADE section below.

## The four rivals
### Model-based static (Patras Eq. 18, local n)
- tau_opt = (1/n) sqrt(2 Te / Tc) (fact, Eq. 18). CW = 2 / tau_opt - 1, clipped to 16..1024 (**decision**, the plan's rev. 10 form; the paper's own mapping, Eq. 26, includes a p-dependent factor and is not used).
- n = the AP's number of STAs (local n, **decision**; no neighbour information). In S5a AP3 is non-saturated (1 Mbps per STA), where the saturated-model n over-counts (**inference**).
- Te = 9 us (HE slot). Tc is an **inference** (below), so Tc in {128, 257, 514} us is the tuning axis.
- Output is a fixed CW per AP run as `--mode static --apCws`; for Tc 257 us: S2 150,301; S4 75,75,75.

### DAC (Patras TMC 2011)
- Error e = 2 p_others - p_own - p_col (Eq. 2); p_own = F/(F+T) (Eq. 4); p_others = R/(R+S) (Eq. 5); p_col = 1 - exp(-sqrt(2 Te / Tc)) (Eq. 20).
- PI: CWmin(k) = Kp e(k) + S(k), S(k+1) = S(k) + Ki e(k) (Eq. 23, 25). Kp = 0.4 Ku, Ku = 2 / (p_col^2 (1 + p_col sum_{k=0..m} (2 p_col)^k)), Ki = Kp / (0.85 Ti), Ti = 2 (Eq. 41, 42, 47-49), m = 6 for CW 16..1024. At Tc 257 us: p_col 0.2325, Kp 10.33, Ki 6.08.
- Update once per beacon interval (0.1 s), deferred while fewer than 20 samples (fact, Section 3). CW clipped to [16, 1024] (fact, Section 3).
- **Deviations (labelled):**
  1. AP level. The paper runs one controller per station on that station's own counters. Here one controller per BSS reads BSS-aggregate counters from `cw.cc --extraTraces` (F = `txfail`, T = `rx`, retry share = `retry` weighted by `rx`). So p_own and p_others are both BSS-wide and the fairness term is about 0. This is the plan's "DAC at AP level".
  2. The integrator is clamped to [16, 1024] (anti-windup); the paper clamps the output only.
  3. Start CW 16 (not stated in the paper).
  4. Te and Tc are ours (HE 20 MHz), not the paper's 802.11g values.
- **Smoke fact (4 s, run 43145852491):** CW climbs 16 -> 113 in S2 and 16 -> 50-71 in S4, and both APs in S2 take the same path. With Kp, Ki from Eq. 47-49 the climb is slow (hundreds of 100 ms updates to reach CW 512), so a 30 s evaluation window may end before convergence. The paper's convergence plots (Fig. 9) are at 100 ms updates too. This is reported, not tuned away.

### Contextual UCB
- UCB1 per (context, arm), arms = CW exponents 4..10, 200 ms pulls, reward = own goodput per STA (as the existing UCB). Context = log2 bucket of the AP's active-STA count (0, 1, 2-3, 4-7, 8-15, 16-31, 32+), from `--extraTraces`.
- Source: the plan, motivated by the Wi-Fi MAB study (context helps). **Our construction, not from a paper.**
- **Fix after batch 1 (fact):** the first version tried every arm once per context before using the bound. The context changes from window to window, so it explored at random for the whole run: ucbctx scored the same for c = 0.1, 0.3 and 1 (S2 GC -0.42 at alpha 1 for all three). Now a context with fewer than 7 pulls backs off to context-free UCB1 (**decision**). The six ucbctx tuning jobs and the cross-check were rerun as `m2b-batch1b.json` (ids end in `-v2`).
- "Active" is the count of distinct STAs whose data frames the AP decoded in a 10 ms step, averaged over the window (fact, cw.cc). It is not the number of backlogged STAs: in the 4 s smoke S2 the means were 5.3 and 9.2 for 20 and 40 STAs. In static cells the context is therefore nearly constant and the controller reduces to plain UCB; its value shows only in the S7/S8 cells (**inference**).

### drlCW
- From the paper (fact): per-AP DDQN, action b in {0..6} (CW = 2^(4+b)), decision every 0.5 s; observation [cw, per, thp, delay, cdf]; state = own last 10 observations plus the same for neighbours heard directly, plus a hidden node's observations one interval late; reward r = alpha - beta d_tail if sum thp >= 0.98 sum thp_CSMA and 0.95 sum per <= sum per_CSMA else -1 (alpha 1.5, beta 10); LSTM(64), FC(64), FC(7); gamma 0.9, lr 5e-4, batch 32, memory 500, soft update 0.004, epsilon 1 -> 0.01 decay 0.99, 300 s training.
- **Decisions** (not in the text; also in the `drlcw.py` docstring): Adam; ReLU after the first FC; one network per AP; epsilon decays per decision; thp feature = interval Mbps / (offered per STA x STAs); delay and cdf features = min(1.5, ln(1+ms)/ln(1001)); per = (PHY tx - rx)/PHY tx; d_tail in seconds; reward clipped to [-1, 1.5]; CSMA references from a BEB run; the neighbour observations come from simulator records (the paper's beacon exchange), which breaks ADR-0002 on purpose, as KW does.
- cw.cc `--delayWindow W` (new, off by default, defaults stay byte-identical): per-packet delay = OnOff send time to the AP sink's receive time, matched by packet uid; mean and nearest-rank p95 (ms) of the window that just ended are appended to each per-AP info record. **Smoke fact (run 43146733153):** the trace's end-of-run per-AP delay (flow monitor) is 2.4-2.8 s and the windowed p95 grows from 0.86 s to 4.6 s over the 4 s run, so the two agree.
- **Open issue, decision card posted to xyz:** in these overloaded cells the queue grows without bound, p95 delay is already 0.86 s in the first window, and beta 10 gives alpha - beta d < -1 in every window. The reward is then a constant -1. Recommended and implemented as `--drlRef`: divide d_tail by the BEB d_tail at the same decision (from one 300 s BEB run per cell) and multiply by 0.1 s (the paper's CSMA value, Table III), so BEB parity gives r = 0.5. Alternatives: the verbatim reward (cannot learn) or dropping the delay term.
- No tuning sweep (paper values), 3 training seeds per cell, as in M2c. This is a stated departure from the shared tuning budget (**decision**).

### Tc for HE 20 MHz MCS 11 (inference, not measured in ns-3)
- cw.cc: 802.11ax 5 GHz, ConstantRate HeMcs11 for data and control, 20 MHz, UDP payload 1464 B, IP + UDP + LLC 36 B, no A-MPDU (`BE_MaxAmpduSize 0`).
- MPDU about 1530 B (MAC header 26 B + FCS 4 B). At MCS 11, 20 MHz: 1950 data bits per 13.6 us symbol (0.8 us GI): 7 symbols = 95 us, plus the HE SU preamble about 40 us = 135 us.
- After a collision the senders wait for the ACK timeout (SIFS 16 + ACK about 54 + slot 9 = 79 us) and then AIFS (43 us): Tc about 257 us. SIFS, ACK length and the timeout rule were **not** checked in the ns-3 source. Hence the {128, 257, 514} us sweep (CW scales with sqrt(Tc), so 2x error = 1.4x CW).

## BLADE (added 2026-11-13, after the full PDF with Appendices E and I was read)
- **Source (fact):** Guo et al., "BLADE: Adaptive Wi-Fi Contention Control for Next-Generation Real-Time Communication", NSDI 2026, 22-page proceedings PDF uploaded by xyz. Read: Sec. 4.2-4.3 (Eq. 1-6), Sec. 5, Appendix E / I (Algorithm 1), F (target MAR), J (observation interval).
- **Algorithm (fact, Algorithm 1):** MAR = N_tx / (N_tx + N_idle) over N_obs = 300 events. If MAR > MAR_tar (0.1): CW = CW + CW max(0, MAR - MAR_max) + M_inc (min(MAR, MAR_max) - MAR_tar) + A_inc. Else CW = min(M_dec - (1 - M_dec)(CW - CWmin)/(CWmax - CWmin), 2 MAR / (MAR_tar + MAR)) CW. Defaults MAR_max 0.35, M_inc 500, M_dec 0.95, A_inc 15, A_fail 5, CWmin 15, CWmax 1023. Fast recovery: after the first failed attempt CW = CW/2 (A_fail added to the stored value), restored on the ACK. Unit test (this repo): CW 100 at MAR 0.5 gives 255 and at MAR 0.02 gives 33.3, as the equations give by hand.
- **Implementation:** `BLADE` in `ap_controllers.py`, trainer `--mode blade` (`--bladeNobs`, `--bladeMarTar`, `--bladeMarMax`, `--bladeMinc`, `--bladeMdec`, `--bladeAinc`), cw.cc `--bladeCounts` (new, off by default) appends the AP radio's per-step idle-slot sum and backoff-gap count (each gap ends at one transmission event, own or heard).
- **Deviations (labelled):** (1) this is the paper's **BLADE SC** variant: the per-packet fast recovery is not modelled (the controller acts on 10 ms steps); (2) the paper updates at each ACK once 300 events are counted, here at the end of the step in which the count reaches 300; (3) CW 16..1024 in our units (paper attribute values 15 / 1023); (4) one controller per AP on the AP radio (the paper's downlink deployment on APs); (5) idle slots are cw.cc's per-gap estimate floor((gap - 43 us) / 9 us); (6) start CW 16; (7) our cells are saturated uplink with hidden pairs in S4 and the paper has all devices in one carrier-sense domain (its Sec. 7 and Appendix H say hidden terminals distort MAR unless RTS/CTS is on; ours has no RTS/CTS), so S4 is outside the paper's validated range (**inference**).
- **Smoke (fact, Actions run 43471908109, 4 s):** both `--check` PASS. S2: both APs take the same path (all APs hear the same medium), CW 1024 at step 50 then 870-920. S4: AP1 and AP3 at 170-220, AP2 pinned at 1024 with a mean idle of 3 slots (AP2 hears both others).
- **Tuning plan:** MAR_tar in {0.05, 0.1, 0.2} on S2 and S4, seeds 0-2, 30 s (`m2b-batch6-blade-tune.json`, 6 jobs, about 1.9 lab-hours); selection rule as for the other rivals. Not launched yet.

## Job plan
Batch generator: `.github/jobs/make_m2b_batch1.py` -> `.github/jobs/m2b-batch1.json` (25 jobs, about 14 lab-hours; format of `run-packs.yml` and `tools/hf`).
1. **Batch 1 (Actions, 23 jobs + 2 on HF):** tuning of ucbctx, dac and model-static (3 settings x S2/S4 x selection seeds 0-2, 30 s; 18 jobs), three 300 s BEB reference runs with the delay trace and `ref.json` for drlCW (the longest job, about 110 min, sets the wall time), and a platform cross-check (dac and ucbctx, same args, one job on Actions and one on HF; compare trace sha256).
2. **Batch 2 (after batch 1):** drlCW training on HF (3 cells x 3 seeds, 300 s each; learner mode, one CPU type) with its references from batch 1, and the final n = 10 runs of the selected setting of each non-learned rival on S2, S4, S5a (seeds 100-109; claims use 103-109). Selected settings come from the batch-1 tuning, so batch 2 cannot be written before them.
3. **Estimate (fact + inference):** M2c timings give a 30 s evaluation of about 11 min (S2), 8 (S4), 11 (S5a) on an Actions lane; a drlCW 300 s training is about 2 h (S2), 1.3 h (S4), 2 h (S5a). Totals: batch 1 about 14 lab-hours; batch 2 about 36 lab-hours; the plan's M2b budget is about 52 h.
4. **Platform rule (fact + decision):** non-learned rivals (ucbctx, dac, model-static, BEB) go to Actions, drlCW to HF. Whether non-learned controllers are byte-identical across vendors is **unknown** for ucbctx and dac (BEB, static and IdleSense are known); the cross-check jobs answer it. If they differ, those rivals stay on one platform inside each comparison.
5. **Caveat:** RAFA and the M2c rivals were trained on Actions CPUs of mixed vendors, while drlCW would train on the HF Intel CPU. Learner results are bit-identical only within a vendor, and the effect on a comparison is **unknown** (it acts like extra seed noise, not a bias, **inference**).
