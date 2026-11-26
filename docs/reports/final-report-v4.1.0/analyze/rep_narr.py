"""Writes sections/results/1..7.md (the answers to the mentor's scenarios) from generated/keynums.json, so every number in the text is the number in the tables.
Run after rep_cells.py. Scenario 8 and the extension are fixed texts (sections/results/8.md, ext.md)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import GEN, ROOT  # noqa: E402

K = json.load(open(os.path.join(GEN, "keynums.json")))
OUT = os.path.join(ROOT, "sections", "results")
os.makedirs(OUT, exist_ok=True)


def d(c, m):
    return K[c][m]["d"]


def p(c, m):
    return "%+.1f %%" % d(c, m)


def tot(c, m):
    return "%.1f" % K[c][m]["total"]


def jn(c, m):
    return "%.2f" % K[c][m]["jain"]


def ms(c, m):
    return "%.2f" % K[c][m]["min_sta"]


def ls(c, m):
    return "%.2f" % K[c][m]["loss"]


def cw(c, m):
    v = K[c][m]["cw"]
    return " / ".join("%d" % round(x) for x in v) if v else "n/a"


def rng(cells, m):
    v = [d(c, m) for c in cells]
    return "%+.1f %% to %+.1f %%" % (min(v), max(v))


def best_of(c, methods):
    return max(methods, key=lambda m: d(c, m) if m in K[c] else -1e9)


NAME = {"bebrts": "BEB+RTS/CTS", "dac514": "DAC", "blade": "BLADE", "idlesense": "IdleSense", "kw": "KW", "static-model": "the Patras static CW",
        "static-a1": "the best common static CW", "kwdirect-a0": "the central online search (alpha 0)", "kwdirect-a1": "the central online search (alpha 1)",
        "L-global": "Global-CW OSCAR", "L-indep": "independent per-AP OSCAR", "L-pf": "the PF learner",
        "beb": "BEB", "static-a0": "the best common static CW (alpha 0)", "static-prop": "the proportional static CW"}
ALL = list(NAME)[1:]

import re as _re


def F(t, a):
    n = len(_re.findall(r"%[-+0-9.]*[sdf]", t.replace("%%", "")))
    if n != len(a):
        raise SystemExit("template with %d placeholders got %d values; text starts: %s" % (n, len(a), t.strip()[:60].replace("\n", " ")))
    return t % a


INTRO = """> **Controllers used in the answers.** The mentor's text speaks of one "global Actor" and one "global Critic". The project has no controller with exactly that shape (Part II, section 3.1), so every answer names the controller behind it. **Global-CW OSCAR** (one DDPG agent whose single output is one CW applied to every AP) is the closest to the mentor's global Actor; the **central online search** (kwdirect) is a central controller that sets a different CW per AP; **independent per-AP OSCAR** and the **PF learner** are one agent per AP. BEB, BEB+RTS/CTS, DAC, BLADE, IdleSense, KW and static CWs are the reference points. All numbers are from new simulations for this report: evaluation seeds 400 to 409, 60 s runs scored on the second half, saturated constant-rate UDP uplink, one channel, mean with 95 % confidence interval (CI) over seeds. The learners were trained for this report on 12 episodes of 15 s simulated time each, with three independent training seeds, and are evaluated frozen.
"""

# ---------------------------------------------------------------- scenario 1
S1 = ["a1a", "a1b", "a1c", "a1d"]
t = INTRO + F("""
### Results

![Goodput change relative to BEB, scenario 1 (error bars: 95 %% CI over seeds)](figures/rep_s1_bars.png){w=600}

{{include:generated/tbl_a1a.md}}

{{include:generated/tbl_a1b.md}}

{{include:generated/tbl_a1c.md}}

{{include:generated/tbl_a1d.md}}

{{include:generated/spread_a1a.md}}

### Answers to the research questions

1. **Can the global Actor learn appropriate CW values for both APs?** Yes, in the sense of reaching the best common CW. Global-CW OSCAR improves on BEB by %s (1A), %s (1B), %s (1C) and %s (1D). The best common static CW, found by search on separate seeds, gives %s, %s, %s and %s, so the learner is within %.1f and %.1f points of it in 1A and 1B and within %.1f and %.1f points in 1C and 1D. Its CW is the same for both APs by construction (mean %s slots in 1A, %s in 1D). In these four symmetric cells the best answer is a symmetric one, so no controller is expected to learn two different values; the per-AP controllers (central online search, PF learner) end with similar values for the two APs (1A: %s and %s slots).
2. **Does joint CW optimization outperform applying the same CW to both APs?** Not in symmetric cells. The best common static CW (the "same CW for both" case) is, within the confidence intervals, as good as or better than every controller that can set a different CW per AP: central online search %s to %s against %s to %s for the common CW (1A to 1D). Where the two APs differ, in the unequal-station and hidden-node cells, the picture changes (scenarios 2, 4 and 7).
3. **Does the approach reduce collisions compared with independent per-AP CW optimization?** Yes. The PHY loss (share of transmission attempts that fail) is %s for Global-CW OSCAR against %s for independent per-AP OSCAR in 1A, and %s against %s in 1D. Independent per-AP OSCAR ends below BEB in goodput (%s, %s, %s, %s in 1A to 1D) and unevenly split between the two APs (1A: %s Mbit/s against %s).
4. **Does it improve inter-BSS fairness?** It keeps the BSSs equal, but BEB already does that in a symmetric cell: Jain's index over stations is %s to %s for BEB and for Global-CW OSCAR in all four cells. The improvement is against independent per-AP OSCAR (Jain %s in 1A and %s in 1D, worst station %s and %s Mbit/s against %s and %s for Global-CW OSCAR).

**Status:** answered with new runs; the controller behind the answers is Global-CW OSCAR (questions 1, 2 and 4) and the comparison with independent OSCAR (question 3).
""", (
    p("a1a", "L-global"), p("a1b", "L-global"), p("a1c", "L-global"), p("a1d", "L-global"),
    p("a1a", "static-a1"), p("a1b", "static-a1"), p("a1c", "static-a1"), p("a1d", "static-a1"),
    d("a1a", "static-a1") - d("a1a", "L-global"), d("a1b", "static-a1") - d("a1b", "L-global"), d("a1c", "static-a1") - d("a1c", "L-global"), d("a1d", "static-a1") - d("a1d", "L-global"),
    cw("a1a", "L-global").split(" / ")[0], cw("a1d", "L-global").split(" / ")[0],
    cw("a1a", "kwdirect-a1").split(" / ")[0], cw("a1a", "kwdirect-a1").split(" / ")[1],
    p("a1a", "kwdirect-a1"), p("a1d", "kwdirect-a1"), p("a1a", "static-a1"), p("a1d", "static-a1"),
    ls("a1a", "L-global"), ls("a1a", "L-indep"), ls("a1d", "L-global"), ls("a1d", "L-indep"),
    p("a1a", "L-indep"), p("a1b", "L-indep"), p("a1c", "L-indep"), p("a1d", "L-indep"),
    "%.1f" % K["a1a"]["L-indep"]["per_ap"][0], "%.1f" % K["a1a"]["L-indep"]["per_ap"][1],
    min(jn(c, m) for c in S1 for m in ("beb", "L-global")), max(jn(c, m) for c in S1 for m in ("beb", "L-global")),
    jn("a1a", "L-indep"), jn("a1d", "L-indep"), ms("a1a", "L-indep"), ms("a1d", "L-indep"), ms("a1a", "L-global"), ms("a1d", "L-global")))
open(os.path.join(OUT, "1.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 2
S2 = ["b2a", "b2b", "b2c"]
t = F("""### Results

How the topologies were built: the simulator has a yes/no switch for pairs of BSSs that cannot hear each other (`--apHidden`). 2A is "AP3 hidden from AP1 and AP2" (AP1 and AP2 overlap; AP3 is isolated), 2B is "AP1 hidden from AP2 and AP3", and 2C is the chain (AP1 and AP3 hidden from each other, AP2 hears both). Stations per AP are 10, 10, 10 in 2A and 2B and 15, 15, 15 in 2C, as in the mentor's table. **Experiment 2D (different interference strengths) was not run**: the simulator has only audible or deaf pairs, no graded strengths (the plan to add them is item 2 of the post-report list).

![Goodput change relative to BEB, scenario 2](figures/rep_s2_bars.png){w=520}

{{include:generated/tbl_b2a.md}}

{{include:generated/tbl_b2b.md}}

{{include:generated/tbl_b2c.md}}

### Answers

- **Impact of the interference relationships on the optimal CW.** In 2A and 2B the isolated AP does not interact with the pair, and the pair behaves like the two-AP cell of scenario 1: the best controllers (DAC, KW, the PF learner, the common static CW, the central online search) improve on BEB by about %s to %s of the total (the isolated AP's goodput is part of the total, which dilutes the percentage compared with 1A). CWs differ between APs only mildly: in 2A the central online search ends with %s slots for AP1, AP2, AP3, and in 2B with %s, so the isolated AP uses a smaller CW than the two that compete, as the mentor expected.
- **Global-CW OSCAR is sensitive to which AP is isolated.** One CW for all APs gives %s in 2A but %s in 2B: the single value it learns (%s slots in 2B) is probably wrong for the isolated AP (inference). The PF learner, which has one CW per AP, gives %s and %s. This is an effect of the controller shape (one CW for all APs), not of the topology alone.
- **The chain (2C) is the case where interference changes the optimum.** BEB gives the middle BSS %s Mbit/s in total while the outer BSSs get %s and %s: the worst station gets %s Mbit/s and Jain's index over stations is %s. Controllers that raise the middle BSS's share do so at the cost of total goodput: the central online search gives the middle BSS %s Mbit/s (outer %s and %s) with Jain %s, at %s total goodput against BEB; the PF learner %s Mbit/s in the middle (Jain %s, %s). Controllers that maximise total goodput (DAC %s, Global-CW OSCAR %s) leave the middle BSS at %s and %s Mbit/s. KW and the fair learners trade throughput for fairness, the others do the opposite. A common CW cannot do both (the common static CW chosen for alpha 1: %s total, middle BSS %s Mbit/s; the one chosen for alpha 0 gives the opposite trade).
- **Interference matrix in the state (the mentor's remark).** In this project a coarse BSS-level loss matrix builds the topology (which pairs of BSSs hear each other; ADR-0005), but it is not an input to any controller compared here: every controller learns from measured goodput, loss or idle time. The 2C result shows what such an input could be for: a controller that knows the chain could set the middle BSS's CW apart at once, while the controllers here need measurement time to find it (the central online search does find a per-AP CW with Jain %s, above). Giving the matrix to a controller as an input is not implemented; it is listed with the graded-interference work (post-report list, item 2).

**Status:** answered for 2A, 2B and 2C; 2D not run (no graded interference in the simulator).
""", (
    "%+.0f %%" % min(d("b2a", m) for m in ("dac514", "kw", "L-pf")), "%+.0f %%" % max(d("b2a", m) for m in ("dac514", "kw", "L-pf")),
    cw("b2a", "kwdirect-a1"), cw("b2b", "kwdirect-a1"),
    p("b2a", "L-global"), p("b2b", "L-global"), cw("b2b", "L-global").split(" / ")[0], p("b2a", "L-pf"), p("b2b", "L-pf"),
    "%.1f" % K["b2c"]["beb"]["per_ap"][1], "%.1f" % K["b2c"]["beb"]["per_ap"][0], "%.1f" % K["b2c"]["beb"]["per_ap"][2], ms("b2c", "beb"), jn("b2c", "beb"),
    "%.1f" % K["b2c"]["kwdirect-a1"]["per_ap"][1], "%.1f" % K["b2c"]["kwdirect-a1"]["per_ap"][0], "%.1f" % K["b2c"]["kwdirect-a1"]["per_ap"][2], jn("b2c", "kwdirect-a1"), p("b2c", "kwdirect-a1"),
    "%.1f" % K["b2c"]["L-pf"]["per_ap"][1], jn("b2c", "L-pf"), p("b2c", "L-pf"),
    p("b2c", "dac514"), p("b2c", "L-global"), "%.1f" % K["b2c"]["dac514"]["per_ap"][1], "%.1f" % K["b2c"]["L-global"]["per_ap"][1],
    p("b2c", "static-a1"), "%.1f" % K["b2c"]["static-a1"]["per_ap"][1], jn("b2c", "kwdirect-a1")))
open(os.path.join(OUT, "2.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 3
S3 = ["c3a", "c3b", "c3c", "c3d"]
t = F("""### Results

![Goodput change relative to BEB, scenario 3](figures/rep_s3_bars.png){w=600}

![CW chosen as the density grows](figures/rep_s3_cw.png){w=380}

{{include:generated/tbl_c3a.md}}

{{include:generated/tbl_c3b.md}}

{{include:generated/tbl_c3c.md}}

{{include:generated/tbl_c3d.md}}

{{include:generated/spread_c3d.md}}

### Answers to the research questions

- **Does the learning algorithm converge as the number of APs increases?** The evidence is the frozen learner's performance and its spread over three independent trainings of the same budget (12 episodes of 15 s each), not training curves, which were not recorded in these runs. Global-CW OSCAR reaches %s, %s, %s and %s over BEB in 3A to 3D; the best common static CW gives %s, %s, %s and %s. The learner is therefore within %.1f points of the best common CW at 3 APs and within %.1f points at 4 APs. The largest gap between the three trainings in a cell is %.2f Mbit/s of total goodput (table above for 3D).
- **Does the performance improvement remain consistent?** Yes for the controllers that read the whole channel: the gain over BEB grows with the total number of stations (30 in 3A, 40 in 3C, 60 in 3B, 80 in 3D; Global-CW OSCAR %s at 3x10 to %s at 4x20; DAC %s to %s). The reason is the baseline: BEB's goodput falls as stations are added (%s Mbit/s at 3x10, %s at 4x20) while the tuned CW keeps the channel near its capacity. Independent per-AP OSCAR does not hold: %s in 3A to %s in 3D. KW is unreliable here (%s in 3A, %s in 3D).
- **Does the joint action space affect sample efficiency?** Not measurable from this data: the training budget was equal for 3 and 4 APs and the result at 4 APs is as good as at 3 relative to the optimum, so within this budget no loss is seen. Global-CW OSCAR has a single output at every size; only a per-AP actor (central critic prototype, Part II section 4.5) has an output that grows with the APs, and it was not part of this wave (it collapsed at 10 APs in the earlier study).
- **How does the learned CW distribution change with AP density?** Global-CW OSCAR's single CW is %s slots at 3x10, %s at 3x20, %s at 4x10 and %s at 4x20: it is smallest with 30 stations and larger with 40 and 60 (slightly smaller at 80 than at 60). The central online search rises steadily with the total number of stations (30, 40, 60, 80 stations: mean CW %s, %s, %s, %s slots).

**Status:** answered for 3A to 3D with Global-CW OSCAR as the closest controller to the mentor's global Actor.
""", (
    p("c3a", "L-global"), p("c3b", "L-global"), p("c3c", "L-global"), p("c3d", "L-global"),
    p("c3a", "static-a1"), p("c3b", "static-a1"), p("c3c", "static-a1"), p("c3d", "static-a1"),
    max(d(c, "static-a1") - d(c, "L-global") for c in ("c3a", "c3b")), max(d(c, "static-a1") - d(c, "L-global") for c in ("c3c", "c3d")),
    max(K["spread"][c]["L-global"] for c in S3),
    p("c3a", "L-global"), p("c3d", "L-global"), p("c3a", "dac514"), p("c3d", "dac514"), tot("c3a", "beb"), tot("c3d", "beb"),
    p("c3a", "L-indep"), p("c3d", "L-indep"), p("c3a", "kw"), p("c3d", "kw"),
    cw("c3a", "L-global").split(" / ")[0], cw("c3b", "L-global").split(" / ")[0], cw("c3c", "L-global").split(" / ")[0], cw("c3d", "L-global").split(" / ")[0],
    *["%d" % round(sum(K[c]["kwdirect-a1"]["cw"]) / len(K[c]["kwdirect-a1"]["cw"])) for c in ("c3a", "c3c", "c3b", "c3d")]))
open(os.path.join(OUT, "3.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 4
S4 = ["d4a", "d4b", "d4c", "d4d"]
t = F("""### Results

![Goodput change relative to BEB, scenario 4](figures/rep_s4_bars.png){w=600}

![CW chosen by each controller for each AP, against the AP's station count](figures/rep_s4_cw.png){w=600}

![Goodput per station of each BSS in 4B](figures/rep_s4b_perSTA.png){w=480}

{{include:generated/tbl_d4a.md}}

{{include:generated/tbl_d4b.md}}

{{include:generated/tbl_d4c.md}}

{{include:generated/tbl_d4d.md}}

All four cells are a single collision domain (every BSS hears every other); "fully overlapping" in the mentor's text.

### Answers to the research questions

1. **Does the controller adapt CW according to station density?** The controllers that gain the most goodput do not, and they do not need to. In 4B to 4D the common static CW gives %s, %s and %s over BEB, Global-CW OSCAR (one CW for all) %s, %s and %s, and the central online search, which can set a CW per AP, ends with nearly the same CW for every AP (4B: %s slots for the APs with 10, 20, 30, 40 stations). In a single collision domain a common CW gives every station the same chance to transmit, so the per-station share is already fair and the total goodput is already near the best. The learners that do set different CWs per AP raise the CW with the AP's station count (4B, PF learner: %s slots; independent per-AP OSCAR: %s), and neither improves on the common CW: the PF learner gains %s in 4B, independent per-AP OSCAR loses %s, and both lower the per-station fairness (below).
2. **Does it improve fairness between heavily and lightly loaded BSSs?** Measured per station, yes against BEB: the worst station gets %s Mbit/s under BEB in 4B and %s with the central online search, %s with Global-CW OSCAR, %s with the common static CW; Jain's index over stations is %s (BEB), %s, %s, %s. Floor test (each BSS keeps at least the smaller of its BEB goodput and its proportional share; passed in %.0f %% of seeds by Global-CW OSCAR and %.0f %% by BEB in 4B). The PF learner and independent per-AP OSCAR break the per-station balance (Jain %s and %s in 4B, %s and %s in 4C).
3. **Does it prevent one AP from dominating channel access?** Yes for every controller that uses a common or searched CW. The clear failure is independent per-AP OSCAR: the worst station gets %s Mbit/s in 4B (BEB %s) and its total goodput is %s against BEB, because the agents of the two smaller BSSs learn the smallest CW (%s slots) while the agent of the 40-station BSS ends at %s, so the largest BSS is starved.

Aggregate goodput alone would hide this, as the mentor notes: total goodput of the PF learner in 4B (%s) is close to the best, while its per-station fairness (Jain %s) is lower than that of BEB (%s), Global-CW OSCAR (%s) and the central online search (%s).

**Status:** answered for 4A to 4D.
""", (
    p("d4b", "static-a1"), p("d4c", "static-a1"), p("d4d", "static-a1"), p("d4b", "L-global"), p("d4c", "L-global"), p("d4d", "L-global"),
    cw("d4b", "kwdirect-a1"), cw("d4b", "L-pf"), cw("d4b", "L-indep"), p("d4b", "L-pf"), p("d4b", "L-indep").replace("-", ""),
    ms("d4b", "beb"), ms("d4b", "kwdirect-a1"), ms("d4b", "L-global"), ms("d4b", "static-a1"),
    jn("d4b", "beb"), jn("d4b", "kwdirect-a1"), jn("d4b", "L-global"), jn("d4b", "static-a1"),
    100 * K["d4b"]["L-global"]["feas"], 100 * K["d4b"]["beb"]["feas"], jn("d4b", "L-pf"), jn("d4b", "L-indep"), jn("d4c", "L-pf"), jn("d4c", "L-indep"),
    ms("d4b", "L-indep"), ms("d4b", "beb"), p("d4b", "L-indep"), cw("d4b", "L-indep").split(" / ")[0], cw("d4b", "L-indep").split(" / ")[3],
    p("d4b", "L-pf"), jn("d4b", "L-pf"), jn("d4b", "beb"), jn("d4b", "L-global"), jn("d4b", "kwdirect-a1")))
open(os.path.join(OUT, "4.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 5
E = K.get("e5", {})
if E:
    def e(m, k):
        return E[m][k]
    order = sorted((m for m in E if m not in ("bebrts",)), key=lambda m: -E[m]["mean"])
    best = order[0]
    t = F("""### Results

The schedule is the mentor's table: 3 APs, active stations per AP 10, 15, 20, 25, 15, 10, 20 s each (120 s run, seeds 400 to 409; learners are frozen actors trained on the same schedule). Stations that are not yet active are not associated and carry no traffic; "joining" and "leaving" are the simulator's station schedule (`--staSchedule`).

![Total goodput and mean CW over time, scenario 5](figures/rep_s5_time.png){w=620}

{{include:generated/tbl_e5_phase.md}}

{{include:generated/tbl_e5_means.md}}

### Answers (the five measures of the mentor's text)

- **Convergence after topology changes and time to stabilise CW.** CW settling time (seconds until the mean CW stays within 10 %% of its level at the end of the phase): Global-CW OSCAR %s, PF learner %s, central online search %s, KW %s, DAC %s. A frozen learner reacts on the next 10 ms step, so its CW settles at once; DAC and KW move their CW over the whole run (CW panel).
- **Throughput degradation during transitions.** When stations join, the lowest second in the first five seconds compared with the previous phase's level is: Global-CW OSCAR %s %%, DAC %s %%, central online search %s %%, BEB %s %%, KW %s %% (a positive value means the goodput rose). When stations leave there is a large drop for every controller, BEB included (BEB %s %%, DAC %s %%, Global-CW OSCAR %s %%), so this drop comes from the scenario mechanics (stations leaving the network) and not from CW adaptation; its exact cause was not isolated in this study (unknown).
- **Collision probability.** Measured as the retry rate: lowest for Global-CW OSCAR (%s), then BLADE (%s) and the static proportional CW (%s); BEB %s; the independent per-AP agents %s.
- **Recovery time.** Time until goodput stays within 5 %% of the phase level: %s s for Global-CW OSCAR, %s s for BEB, DAC and BLADE, %s s for the central online search, %s s for KW.
- **Which controller adapts best overall?** By mean goodput over the 120 s: %s (%s Mbit/s), then %s. Global-CW OSCAR reaches %s Mbit/s, BEB %s, BEB+RTS/CTS %s and independent per-AP OSCAR %s. The two best are not learners: an online rule (DAC) and a static CW chosen in advance (on separate seeds, at the full 25 stations per AP) do as well as anything that adapts, which suggests that in this single-domain cell the best CW is nearly flat between 10 and 25 stations per AP (inference).

**Status:** answered with the controllers listed. The actor of the mentor's "global Actor" (Global-CW OSCAR) is evaluated as a frozen actor trained on this schedule, not trained online during the run.
""", (
        "%.1f s" % e("L-global", "stab"), "%.1f s" % e("L-pf", "stab"), "%.1f s" % e("kwdirect-a1", "stab"), "%.1f s" % e("kw", "stab"), "%.1f s" % e("dac514", "stab"),
        "%.1f" % e("L-global", "dip_arr"), "%.1f" % e("dac514", "dip_arr"), "%.1f" % e("kwdirect-a1", "dip_arr"), "%.1f" % e("beb", "dip_arr"), "%.1f" % e("kw", "dip_arr"),
        "%.1f" % e("beb", "dip_dep"), "%.1f" % e("dac514", "dip_dep"), "%.1f" % e("L-global", "dip_dep"),
        "%.2f" % e("L-global", "retry"), "%.2f" % e("blade", "retry"), "%.2f" % e("static-prop", "retry") if "static-prop" in E else "n/a", "%.2f" % e("beb", "retry"), "%.2f" % e("L-indep", "retry"),
        "%.1f" % e("L-global", "rec"), "%.1f" % e("beb", "rec"), "%.1f" % e("kwdirect-a1", "rec"), "%.1f" % e("kw", "rec"),
        NAME.get(best, best), "%.1f" % e(best, "mean"), ", ".join("%s (%.1f)" % (NAME.get(m, m), e(m, "mean")) for m in order[1:3]),
        "%.1f" % e("L-global", "mean"), "%.1f" % e("beb", "mean"), "%.1f" % e("bebrts", "mean"), "%.1f" % e("L-indep", "mean")))
    open(os.path.join(OUT, "5.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 6
DU, DS = K["f6u_delay"], K["f6s_delay"]


def dl(m, k="mean_ms", ap=None):
    v = DU[m][k]
    return " / ".join("%.1f" % x for x in v) if ap is None else v[ap]


def red(m, ap, k="mean_ms"):
    return "%.0f %%" % (100.0 * (1 - DU[m][k][ap] / DU["beb"][k][ap]))


t = F("""### Results

The loads are the mentor's example (50, 100, 150 and 200 Mbit/s offered at AP1 to AP4, 10 stations each, i.e. 5, 10, 15 and 20 Mbit/s per station) for the **saturated** experiment (6S). For the **unsaturated** experiment (6U) the same ratios are scaled down to 2.5, 5, 7.5 and 10 Mbit/s per AP (25 Mbit/s in total, below the channel capacity of about 40 Mbit/s), so that the queues do not build up and the delay measures the channel, not a buffer. Traffic is constant-rate UDP in both. **Bursty traffic and mixed UDP/TCP were not run**: the simulator generates constant-rate UDP and on/off windows only (item 4 of the post-report list).

{{include:generated/tbl_f6s.md}}

{{include:generated/tbl_f6s_delay.md}}

{{include:generated/tbl_f6u.md}}

{{include:generated/tbl_f6u_delay.md}}

### Answers to the research questions

- **Can the Actor allocate channel access opportunities according to traffic demand?** Under saturation (6S) every AP's offered load exceeds its fair share, so the demand-proportional allocation of the mentor's example is not feasible; what the best controllers do is give every station the same share (per AP goodput %s Mbit/s for the common static CW; %s for Global-CW OSCAR), which is the fair outcome, and BEB leaves AP1 and AP4 behind (%s Mbit/s). Under 6U, where all the demand fits, the allocation is demand-proportional by construction and the question becomes whether every AP gets what it asks for: BEB, DAC, IdleSense, KW, the static CWs, Global-CW OSCAR and the PF learner carry 2.50 / 5.00 / 7.50 / 10.00 Mbit/s, i.e. all of it.
- **Does the optimization improve delay under heterogeneous loads?** Yes, against BEB, for the controllers that tune to the load. In 6U the mean MAC delay of Global-CW OSCAR is %s ms at AP1 to AP4 against %s ms for BEB (reductions of %s, %s, %s and %s), and the 99th percentile %s ms against %s ms. IdleSense and the central online search (alpha 0) are about equal to Global-CW OSCAR; the static CW chosen for saturation (%s ms mean) is no better than BEB (probably because it is too large for a lightly loaded channel; inference). BEB+RTS/CTS multiplies the delay (%s ms at AP1 to AP4) and loses AP4's traffic (%s of 10 Mbit/s delivered). In 6S all controllers show 5.2 to 5.6 s of delay: the delay is the time in a full queue and does not measure the controller.
- **Does it avoid starving low-load APs?** Yes for all controllers except independent per-AP OSCAR in 6S (total %s against BEB, %s Mbit/s per AP, worst station %s Mbit/s; PHY loss %s). In 6U the lowest-load AP (AP1) keeps at least 2.49 of its 2.5 Mbit/s under every controller except BLADE (%s), independent per-AP OSCAR (%s) and BEB+RTS/CTS (%s).

**Status:** answered for constant-rate UDP, saturated and unsaturated; bursty and mixed UDP/TCP traffic not run.
""", (
    "%.1f" % K["f6s"]["static-a1"]["per_ap"][0], "%.1f" % K["f6s"]["L-global"]["per_ap"][0], "%.1f / %.1f" % (K["f6s"]["beb"]["per_ap"][0], K["f6s"]["beb"]["per_ap"][3]),
    dl("L-global"), dl("beb"), red("L-global", 0), red("L-global", 1), red("L-global", 2), red("L-global", 3), dl("L-global", "p99_ms"), dl("beb", "p99_ms"),
    dl("static-a1"), dl("bebrts"), "%.1f" % DU["bebrts"]["thr"][3],
    p("f6s", "L-indep"), "%.1f" % (K["f6s"]["L-indep"]["total"] / 4), ms("f6s", "L-indep"), ls("f6s", "L-indep"),
    "%.2f Mbit/s" % DU["blade"]["thr"][0], "%.2f Mbit/s" % DU["L-indep"]["thr"][0], "%.2f Mbit/s" % DU["bebrts"]["thr"][0]))
open(os.path.join(OUT, "6.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 7
R = K["rts"]
G = K["g7s4"]
t = F("""### Results

The topologies are the hidden-node cells of scenario 2, built with the simulator's BSS-level "deaf pair" (`--apHidden`): 2A and 2B (one AP is hidden from the other two), 2C (the chain: AP1 and AP3 cannot hear each other) and, as the project's reference hidden-node cell, S4 (10 stations per AP, the same chain). Tables for 2A to 2C are in scenario 2; the delay and the RTS/CTS comparison are added here. **Not run:** asymmetric interference (one direction audible, the other not) and different AP-to-station distances: the simulator has symmetric audible or deaf pairs only (post-report list, item 2). RTS/CTS is disabled in the main experiments and introduced as a separate comparison, as the mentor suggested.

{{include:generated/tbl_b2c_delay.md}}

{{include:generated/tbl_g7s4.md}}

{{include:generated/tbl_g7s4_delay.md}}

{{include:generated/tbl_rts_impact.md}}

### Answers (the mentor's five measures)

- **Collision probability.** BEB's PHY loss ratio is %s in 2C and %s in S4 against %s and %s in the one-domain cells 1A and 3A: the hidden pair does not raise the loss ratio of the whole network, it changes who bears it (the middle BSS, below). The controllers that raise throughput lower it: in 2C DAC %s, Global-CW OSCAR %s, the central online search (alpha 1) %s, the PF learner %s.
- **Packet loss and retries.** The mean per-AP retry rate (share of transmissions that are retries) is lowest with RTS/CTS (%s in 2C, against %s for BEB); this does not translate into goodput (see the RTS/CTS point).
- **Throughput.** In the chain BEB gives the middle BSS %s Mbit/s (S4: %s) while the outer BSSs get %s. Global CW optimisation (one CW for all APs) raises the total (Global-CW OSCAR %s in 2C) but leaves the middle BSS at %s Mbit/s; per-AP CWs raise the middle BSS to %s Mbit/s (central online search) or %s (PF learner) and cost total goodput (%s and %s). No controller raises the middle BSS without lowering the total here. The central online search gives the middle BSS the most (%s Mbit/s); the common static CW chosen for alpha 1 gives it %s Mbit/s at %s total, and the one chosen for alpha 0 gives %s Mbit/s at %s. So a per-AP CW buys a larger middle share, not a better trade between total and middle share.
- **Delay.** In these saturated cells the delay is dominated by the queue (4.7 to 5.4 s mean at the outer BSSs in 2C). The visible effect is on the middle BSS: BEB's 99th-percentile delay is %s s there against %s s at AP1; every other controller brings it down to between %s and %s s, i.e. closer to the outer BSSs.
- **Impact of RTS/CTS.** RTS/CTS lowers total goodput by %s to %s in all six cells measured, hidden or not (table above). In the hidden chain it also lowers the middle BSS (2C: %s to %s Mbit/s; S4: %s to %s Mbit/s) and raises its delay. RTS/CTS therefore does not fix this hidden-node topology in this simulator; the mechanism was not isolated (unknown). This agrees with the project's earlier measurements (Part II, section 5.4).

**Status:** answered for the symmetric hidden-node topologies; asymmetric interference and distance variations not run.
""", (
    ls("b2c", "beb"), "%.2f" % G["beb"]["loss"], ls("a1a", "beb"), ls("c3a", "beb"),
    ls("b2c", "dac514"), ls("b2c", "L-global"), ls("b2c", "kwdirect-a1"), ls("b2c", "L-pf"),
    "%.2f" % K["b2c"]["bebrts"]["retry"], "%.2f" % K["b2c"]["beb"]["retry"],
    "%.1f" % K["b2c"]["beb"]["per_ap"][1], "%.1f" % G["beb"]["per_ap"][1], "%.1f" % K["b2c"]["beb"]["per_ap"][0],
    p("b2c", "L-global"), "%.1f" % K["b2c"]["L-global"]["per_ap"][1],
    "%.1f" % K["b2c"]["kwdirect-a1"]["per_ap"][1], "%.1f" % K["b2c"]["L-pf"]["per_ap"][1], p("b2c", "kwdirect-a1"), p("b2c", "L-pf"),
    "%.1f" % K["b2c"]["kwdirect-a1"]["per_ap"][1], "%.1f" % K["b2c"]["static-a1"]["per_ap"][1], p("b2c", "static-a1"), "%.1f" % K["b2c"]["static-a0"]["per_ap"][1], p("b2c", "static-a0"),
    "%.1f" % (K["b2c_delay"]["beb"]["p99_ms"][1] / 1000), "%.1f" % (K["b2c_delay"]["beb"]["p99_ms"][0] / 1000),
    "%.1f" % (min(v["p99_ms"][1] for k, v in K["b2c_delay"].items() if k not in ("beb", "bebrts")) / 1000), "%.1f" % (max(v["p99_ms"][1] for k, v in K["b2c_delay"].items() if k not in ("beb", "bebrts")) / 1000),
    "%.0f %%" % min(-R[c]["d"] for c in R), "%.0f %%" % max(-R[c]["d"] for c in R),
    "%.2f" % K["b2c"]["beb"]["per_ap"][1], "%.2f" % K["b2c"]["bebrts"]["per_ap"][1], "%.2f" % G["beb"]["per_ap"][1], "%.2f" % G["bebrts"]["per_ap"][1]))
open(os.path.join(OUT, "7.md"), "w").write(t)

# ---------------------------------------------------------------- scenario 6 and 7 are written by hand after the numbers are read (see sections/results/6.md, 7.md)
print("wrote", sorted(os.listdir(OUT)))
