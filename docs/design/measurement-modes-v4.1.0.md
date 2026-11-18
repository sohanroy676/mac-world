# Track A: measurement modes and run infrastructure (v4.1.0)

Specification for Track A of the finalized max-CW plan (`docs/planning/max-cw-optimization-plan-2026-11-14.md`).
Labels: **fact** = checked in code or by a run named here, **decision** = our choice, **inference** = not checked.
Validation results are in section 7. Design decisions on the CW range and the static modes are in ADR-0008.

## 1. Static measurement modes (`cw.cc`, `OSCAR_multi_ap_train.py --mode static`)

All options default to the old behaviour.

| Option | Meaning |
|---|---|
| `--cwLo`, `--cwHi` | clamp for `--apCws` (and for multi-AP actions in `cw.cc`), default 16 and 1024, limits 1 and 32767 |
| `--cwHold` | rewrite each AP's CW to its whole BSS at every env step |
| `--cwMinOnly` with `--apCws` | static CWmin, CWmax = max(CWmin, 1023); CWmin must be 2^k - 1 |
| `--schedA 1,3` | APs that use their `--apCws` value in phase A; all others use the mute CW |
| `--schedB 2` | APs active in phase B; default = the APs not in `--schedA` |
| `--schedPeriodSteps P`, `--schedASteps A` | env step k (0-based) is in phase A when k mod P < A |
| `--schedMuteCw` | CW outside the own phase, default 32767 |
| `--phyDurations` (`cw.cc` only) | print a histogram of AP 1's PHY state durations (section 4) |

Ceiling families of the plan:

- **F1 exact static**: `--mode static --apCws c1,..,cn --cwHold --cwLo 4 --cwHi 32767`.
- **F2 static CWmin with doubling**: `--mode static --apCws c1,..,cn --cwMinOnly`, c_i in {15, 31, ..., 1023}
  (with `--cwLo 3`: also 3 and 7).
- **F3 schedule**: F1 options plus the `--sched*` options.

Why `--cwHold` (fact): a STA takes CWmin/CWmax from every beacon as 2^ECW - 1, so without the rewrite a static CW of
75 runs as 63 at the STAs. With `--cwHold` the STAs are rewritten every 10 ms, which is exactly what every adaptive
mode already does. For a CW that is already 2^k - 1 the option changes nothing (section 7, identical trace hash).

Schedule limits (fact, `src/wifi/model/txop.cc`): changing the CW does not redraw a backoff counter that is already
running. A muted node keeps the long counter it drew, and an active node keeps its short one into the mute phase.
The schedule is therefore a CW-only approximation of time sharing; period and mute CW are search parameters.

`--check` in the trainer verifies every step that each AP reports the CW the schedule prescribes.

## 2. Bounds (`bounds_v4_1_0.py`)

Time-sharing linear model over the independent sets of the BSS conflict graph (two BSSs conflict unless the pair is
in `--apHidden`). Maximises the same station-weighted alpha-fair utility as `gc_analysis.py`, optionally under the
fair floor. Two uses, which differ only in the per-BSS capacity c_i:

- **Scheduled-access bound**: c = payload bits / (AIFS + T_data + SIFS + T_ack), from the measured frame times of
  section 4. Valid for every CW policy under two assumptions: two conflicting BSSs never both succeed at the same
  time (no capture), and no frame exchange is shorter than that time.
- **Independent-set reference**: c_i = best measured throughput of BSS i alone. A reference for perfect coordination
  with internal contention; it is not an upper bound.

Self-test (`--selftest`, fact): proportional fairness on the ideal chain gives shares 2:1:2; alpha 0 gives 1:0:1;
alpha 2, a floor, a demand limit and the one-domain 20:40 case match their closed forms.

## 3. Search driver (`cw_search_v4_1_0.py`)

See the module docstring for the commands. Decisions:

- Variables: z_i = log2(CW_i) in [2, 15] per AP for F1; schedule runs add log2(mute CW), log2(period steps) and the
  phase-A fraction. CWs are rounded to integers before a job is written; duplicates are dropped.
- Round 0: scrambled Halton points plus anchors (all-equal CW at every octave, the M1 octave oracle of the cell).
- Rounds 1 and 2: a Gaussian-process model per alpha on the mean utility over the search seeds, and one on the floor
  margin min_i x_i / floor_i. New points maximise expected improvement times the probability that the margin is
  at least 1 - floorTol; a batch is filled by conditioning on the model's own prediction for the points already
  chosen ("kriging believer").
- The search only proposes candidates. The ceiling is whatever the top 5 per cell and alpha score on the fresh
  validation seeds 200-209, so a weak search can make the ceiling too low but cannot make a result look better
  than it is. The gate rules in the plan do not depend on the search heuristics.

## 4. Frame times and Tc (`--phyDurations`, `phy_times_v4_1_0.py`)

`cw.cc --phyDurations` prints `PHYDUR <key> <microseconds> <count>` for AP 1's radio. Keys: `TX`, `RX_OK`, `RX_ERR`,
`CCA_BUSY`, `IDLE_AFTER_<previous key>`. `phy_times_v4_1_0.py` reads the log and reports the data-frame time
(mode of `RX_OK`), the ACK time (mode of `TX`), SIFS (mode of `IDLE_AFTER_RX_OK`), and the shortest idle gap after
a failed reception, from which Tc = failed-reception time + that gap.

## 5. Run image (`.github/image/Dockerfile`, `.github/workflows/build-image.yml`)

One image per commit: Ubuntu 22.04 by digest, apt from a dated snapshot, micromamba by checksum, Python 3.7.12 by
build string, pip packages from `.github/image/requirements-lock.txt`, and the built simulator in
`/opt/mac-world`. Tag `ghcr.io/<owner>/mac-world-run:<commit>`; packs use the digest.

## 6. Waves: packs, dispatch, collection

See `docs/reference/wave-runbook-v4.1.0.md`.

## 7. Validation runs

All runs: 2026-11-14, local container (Ubuntu 22.04, GCC 11.4.0, Python 3.7.12, torch 1.13.1), through
`run_pack.py`. Cell S4 = `10,10,10 --apHidden 1-3`, 10 Mbps, 5 s, seed 0 unless stated. A piece without a row has
not been validated.

| Check | Result |
|---|---|
| Old static run unchanged: S4 `75,75,75`, seed 103, 30 s against `docs/figures/v4.0.0-m2b/finals/m2b-final-s4-ms-p0/eval-103` | trace byte-identical (final binary) |
| Old BEB run unchanged: S2, seed 108, 30 s against `docs/figures/v4.0.0-m2b/refs-103-109/m2b-ref-s2-p1/beb-108` | trace byte-identical (final binary) |
| `--cwHold` is a no-op for 2^k - 1: `63,63,63` with and without it | same trace hash `6d850994...` |
| `--cwHold` keeps the exact CW: `75,75,75`, STA readback each second | without: 0 of 10 STAs exact (all 63); with: 10 of 10 exact, every AP; traces differ |
| Wide range: `4,2000,32767 --cwHold --cwLo 4 --cwHi 32767` | readback exact at all STAs, `--check` PASS |
| Schedule: `16,16,16 --schedA 1,3`, period 20 steps, A 10 steps, mute 1023 | `--check` PASS (per-step CW equals the schedule); AP1 16 in steps 301-310, 1023 in 311-320; AP2 the opposite |
| Static CWmin: tiny cell `2,3`, first 3 points of the f2 grid (CWmin from 3, 7, 15) with `--cwMinOnly --cwLo 3`, 4 s | 3 runs, `--check` PASS |
| Static CWmin below `--cwLo` (`15,63,15` with the default 16) | rejected with a clear message |
| Bounds self-test | PASS |
| Search driver end to end on `t222` (f1, f3) and `t23` (f2): round 0, GP round 1, `top` | 85 runs, all jobs PASS; pipeline only, the numbers are not results |

Frame times (S2 topology, BEB, 5 s, seed 1, `phy_times_v4_1_0.py`, fact for this ns-3 configuration):

| Quantity | us | Count |
|---|---|---|
| T_data | 139 | 18200 |
| T_ack | 28 | 4850 |
| SIFS | 16 | 14973 |
| AIFS | 43 | 3421 |
| idle gap after a collision | 103 | 6403 |

Ts = 226 us, **Tc = 242 us**, scheduled-access capacity C = 11712 bit / 226 us = 51.82 Mbps. The gaps after a
collision rise in 9 us steps from 103 us (103, 112, 121, 130). The earlier inference was Tc about 257 us
(`docs/results/m2b-specs-v4.0.0.md`: frame 135 us, ACK about 54 us); the measured frame is 139 us and the ACK 28 us.
DAC's tuned Tc of 514 us was a tuning result and is not changed by this measurement.

Space worker (2026-11-16, local, `tools/hf/wave_worker.py`): 12 jobs in 3 packs, 2 packs at once, all PASS, resume skipped
finished packs, collector read the results; GitHub push path tested against a mock API only. Found and fixed a race between
packs (`waf --run` calls overlapping, trainer hung): cross-process start lock in `run_pack.py`, `JOB_TIMEOUT` in `run_job.py`.

Run image (fact, Actions run 43649676348, 2026-11-14): `build-image` passed for commit 7763b40e; the 2,3 BEB check
inside the image gave RESULT: PASS (trace sha256 `52f8b816...`). Image:
`ghcr.io/sohanroy676/mac-world-run@sha256:aaa8e45ea8b23d90512d561ddc03a2730df8e7c79f71c0827bb9b96140d2f6d1`.
The first attempt (run 43645465115) failed because ns3gym was installed before `waf configure` generated its
protobuf file; the Dockerfile now installs it after the build.

Wave 0 rehearsal (fact, 2026-11-16, dispatch commit 65253917, image
`ghcr.io/sohanroy676/mac-world-run@sha256:63c00ce6fb7ce484b4bde4e8b4f1b5c41d6a0fdc6d2a3f652b545898d96a8c28` of commit 3049dc37,
batch `.github/waves/w0-packs.json` from `.github/scripts/w0_batch.py`, results on branch `wave-collected`, `w0/`):

- `wave-dispatch` started all 6 forks; `wave-run` finished on forks 0, 2, 3, 5 in about 25 min (11 of 11 runs PASS each).
  Forks 1 and 4 waited about 50 min in GitHub's queue before they started.
- The 10 non-learned run types (BEB, F1, F2, F3, DAC, KW, S8 schedule, 60 s) have one trace SHA-256 each across the 4 forks
  and across 4 CPU models (Xeon 6975P-C, Xeon 8573C, EPYC 9V74, EPYC 7763). Gate 0 (identical results from at least
  4 accounts) is met for non-learned runs.
- The learner run (`t23`, `pin`) has two hashes: one on both Intel models, one on both AMD models. Learned runs are
  therefore not hash-comparable across CPU vendors with the current pin settings.
- Wall time per 30 s run with 4 lanes: 395 to 731 s; the 60 s run 584 to 1062 s.
- Hugging Face: all 5 accounts were locked by Hugging Face for a terms-of-service violation about one hour after the 10
  Spaces started the batch; no Space delivered a result. Spaces are not used any more (decision, 2026-11-16);
  `tools/hf/wave_worker.py` stays in the repository unused and has never been validated on a Space.

Not validated yet: S7/S8 cells in the search driver
(the delay objective and the S8 load schedule are Track B), any ceiling number.

## Layered controllers (Track B, 2026-11-18)

- `ap_layered_v4_1_0.py`: L1 DACw (per-AP PI loop to a target collision signal), L2 KWPlus (SPSA on the target with shrinkage and an accept/revert guard), L3 max-weight muting (`Coordinated`, only after Gate S).
- Trainer modes `--mode cascade` (L1+L2) and `--mode coord` (L1+L2+L3); tunables `--ly*`, `--dacTc 242e-6`, `--dacCw0 64`.
- `--cwExpLo/--cwExpHi` (default 0 and 6) set the controller exponent range; wide runs use `--cwLo 4 --cwHi 32767 --cwExpLo -2 --cwExpHi 11`. Defaults keep old runs unchanged (DAC 5 s run: same per-AP rewards before and after).
- Smoke (S4, 20 s, `--check`): both modes PASS, 2000 steps. Not tuned yet.
- Information level: L2 sees every BSS goodput, L3 the hearing graph (class A online, breaks ADR-0002 isolation by design).
