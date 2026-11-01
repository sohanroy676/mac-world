# Industry relevance of multi-AP Wi-Fi contention and adaptive contention-window optimization (2024 to 2026)

Prepared 2026-11-01 for Review 2 of *Distributed Adaptive Contention Control for Multiple Access Point Wi-Fi Networks using Cooperative Deep Reinforcement Learning* (builds on OSCAR, IEEE ICC 2023).

## How to read this document

**Labels used on every claim**
- **Fact (source)**: stated by the cited source, quoted or closely paraphrased. All quotes are verbatim and short.
- **Vendor claim**: a company describing its own product or a draft feature. Not independent evidence.
- **Interpretation**: my reasoning from the sources. Not stated by them.
- **Our hypothesis**: the project's proposed research direction. Not an industry fact.

**Source confidence**: **High** = official technical documentation, standards material, original reports. **Medium** = reputable news, secondary technical analysis, arXiv preprints, vendor white papers (vendor-authored, so claims are vendor claims). **Low** = forum posts, undated pages, unverified or partly read pages.

**Method and limits (read this first)**
- Pages were fetched and read on 2026-11-01. Where a page was only partly read or a model summary stood in for text, it is flagged. Some pages show no publication date; I say so rather than guess.
- **No independent measurement study with prevalence statistics** (for example "X % of enterprise APs run above Y % channel utilisation") was found in this session. The evidence in §9 is documentation and white-paper statements, not field data. This is a search limitation, not proof that such data does not exist.
- Pages that failed to load and were **not used**: Broadcom's own press release (convergedigest.com page failed), the Wireless Broadband Alliance Wi-Fi 8 article (server error), Qualcomm's OnQ blog (metadata only), the ICT Express 2025 paper. Broadcom claims below come from a secondary news report.
- Statistics from vendor documents are quoted with page or section. None were reproduced.

---

## 1. Executive Summary

1. **The problem is still described as live by the industry in 2025 and 2026.** Qualcomm's August 2025 Wi-Fi 8 white paper says dense networks "can face challenges with overlapping signals and airtime contention" and that these conditions "can lead to latency spikes, degraded throughput" (S1, p.8). Cisco Meraki's documentation, modified September 2026, says "congestion can occur to the point where devices spend more time receiving than sending" (S4). Juniper's Mist documentation says Wi-Fi and non-Wi-Fi interference "causes clients and APs to pause transmissions" (S7). Fact (source), vendor documentation.
2. **The standards body treats it as unfinished.** IEEE 802.11bn (Wi-Fi 8) is still a draft. It has quantified targets for 95th-percentile latency and MPDU loss "particularly during transitions between overlapping networks" (S9, §I-C), and adds multi-AP coordination "to decrease collisions and improve medium usage efficiency" (S9, §I-C). Final approval is expected in 2028 (S1 p.3; S10 §1; S11). Fact (source), draft status.
3. **What commercial enterprise products automate is radio planning, not MAC backoff.** Meraki AutoRF, Aruba AirMatch and ARM, and Juniper Mist RRM are documented as adjusting channel, transmit power, channel width, and band or radio on/off (S4, S5, S6, S7, S8). None of the pages read mentions contention window, EDCA or backoff tuning. Fact (source) for what the pages say. **We did not find public product documentation explicitly advertising learned Contention Window optimization.** That is not a claim that no vendor implements it.
4. **EDCA/CW parameters are configurable, mostly as static profiles.** Cisco small-business APs expose EDCA templates and manual CWmin, CWmax and AIFSN (S12). Huawei's command reference recommends enabling an optional "dynamic EDCA parameter adjustment" for high-density scenarios (S13), so automatic EDCA adaptation exists in at least one vendor's documentation. How it works is not described on the page read. Fact (source).
5. **Wi-Fi 8 changes CW-related behaviour only in narrow, rule-based, draft ways** (P-EDCA / "HIP EDCA" for urgent traffic, with fixed parameters). Fact (source), draft. **Interpretation:** general-purpose adaptive CW selection across multi-AP deployments is not among the features we found.
6. **What this supports for the project:** contention and airtime sharing between co-channel APs are established industry problems. CW adaptation is a plausible MAC-layer lever for part of that problem, not for RF interference or channel planning. Whether a learned decentralised CW controller helps is **our hypothesis**, and our own measured results to date are mixed (§12).

---

## 2. Why Multi-AP Wi-Fi Contention Matters in 2026

### 2.1 Four different things that are easy to confuse

| Term | What it is | Typical remedy | Is CW the lever? |
|---|---|---|---|
| **RF interference** (non-Wi-Fi or non-decodable energy) | Noise, microwave ovens, radar, other protocols, adjacent-channel leakage. Raises noise floor, lowers SNR | Remove source, change channel, spectrum analysis, channel width | No |
| **Co-channel interference (CCI) / overlapping BSS** | APs and clients on the same channel hear each other. Per the 802.11 MAC they **share** airtime rather than corrupt each other | Channel planning, power reduction, narrower channels, 6 GHz, more channels | Not directly |
| **Airtime contention** | Time the channel is busy with other BSSs' transmissions, so a node defers. Appears as high channel utilisation | Fewer co-channel neighbours, rate management, efficient frames (OFDMA, aggregation), coordination | Partly: affects how nodes share, not how much is available |
| **MAC backoff behaviour / collisions** | Random backoff slots; when two nodes pick the same slot they collide and retransmit. Governed by CWmin, CWmax and AIFSN | Contention window selection, EDCA parameters, scheduled or coordinated access | **Yes, this is what CW tuning acts on** |

Interpretation: carrier sensing makes co-channel APs defer to each other rather than interfere in the corrupting sense. The residual harm that backoff tuning can address is **collisions and wasted slots** between nodes that contend. Hidden-node corruption is a separate case. Meraki's documentation separates the cases the same way: it discusses CCA with random back-off under "Channel utilization" and retransmissions under "Interference" (S4).

### 2.2 What the sources say about the mechanism
- Meraki (S4, "Channel utilization"): "When a device detects another transmission in progress, it will perform a random back-off for a short period of time after which it would perform another check before attempting to transmit again." Fact, High.
- Meraki (S4, "Overlapping Coverage Cells"): "APs with overlapping coverage cells should not be on the same channel, if possible, because this can lead to increased channel utilization." Fact, High.
- Qualcomm (S1, p.8): "Wi-Fi networks can face challenges with overlapping signals and airtime contention." Fact, vendor white paper, Medium.

### 2.3 Why dense deployments make it matter
- Stadiums: Extreme Networks (blog, 2026-02-23): "massive device density, volatile interference, and zero tolerance for downtime push traditional Wi-Fi to its limits" (S14). Vendor claim, Medium.
- Apartments and campuses: Qualcomm (S1, p.8) lists "enterprise campuses, apartment buildings and public venues". Vendor claim, Medium.
- Overlapping homes: MediaTek (S3, p.7): "without effective coordination, these APs may contend and share the common spectrum resources, resulting in often only one AP utilizing the spectrum at any given time." Vendor claim, Medium.

---

## 3. Cisco: Industry Findings and Technical Evidence

**Problem identified**
- Cisco Meraki, *Channel Planning Best Practices* (S4; documentation; published 2020-10-05, modified 2026-09-17 per page metadata). Quotes: "congestion can occur to the point where devices spend more time receiving than sending" (§Channel utilization); "If the sender does not receive an ACK, it must re-transmit the same frame until an ACK is received" and "Re-transmissions result slower speeds" (§Interference); "In certain high density deployments however, these features may not be aggressive enough" (§Introduction). High.
- Cisco, *Wi-Fi 7 and the Growing Future of Wireless Design Guide* (S2; design guide; updated 2025-04-08): 320 MHz channels "in a dense-capacity network, it can lead to high channel reuse rates, co-channel interference, and poor performance" (§320-MHz Channel Width). High.

**Solutions described**
- Meraki AutoRF and TPC: "Meraki's AutoRF algorithm makes this process hands off by using the Meraki cloud to determine the optimal channel configuration" (S5, Introduction; modified 2026-09-18). "Channel spreading selects channels that minimize RF utilization and interference" (S5). TPC: in high density the cloud "may determine that interference could be minimized by a reduction in transmit power" (S5). High.
- Meraki advises manual work for density: "For high-density deployments, manually tune 2.4 & 5 GHz channels and power settings based off of site survey data" (S4, §Site Surveys). High.
- Wi-Fi 7 features in the design guide: MLO ("multiplying airtime opportunities"), multiple resource units, preamble puncturing, R-TWT ("allows APs to use improved channel access and resource reservations to protect such packets") and Cisco Dynamic Bandwidth Selection (S2). High.
- Meraki's 2014 *WiFi Spectrum Analysis* solution guide describes Auto RF as a cost function over neighbour signal strength and "channel utilization estimates", updated "every 10 minutes" on average (S15; Cisco; September 2014). High, but old.

**Out of scope of these documents**
- None of S2, S4, S5 or S15 mentions contention window, EDCA or backoff tuning (checked by reading). Air Time Fairness was also not found in S4 or S5.
- S2 states: "If the network has coverage and capacity issues today, simply replacing the APs with the latest specification is not likely to improve things much." Interpretation: the vendor itself says the new PHY/MAC features do not by themselves remove density problems.

**EDCA in Cisco products**
- Cisco small-business WAP121/WAP321 guide (S12; undated, firmware 1.0.3.4): "Choose the desired template from the EDCA ... Template drop-down list"; Custom sets "Minimum Contention Window" ("the input for the method that determines the initial backoff wait time") and "Maximum Contention Window". This is **manual and static**. Medium (undated, small-business product, old).
- Cisco Community thread (2014 to 2022 posts, forum, **Low**) on WLC 7.6 shows named EDCA profiles ("Voice Optimized", "Custom Voice") chosen from a list. Not vendor documentation.

---

## 4. HPE Aruba Networking: Industry Findings

- *AirMatch*, Aruba Central online help (S6; documentation; no date shown): AirMatch "dynamically adjusts key parameters such as channel selection, channel bandwidth, and Effective Isotropic Radiated Power (EIRP) optimization." Problem named: "interference from nearby APs (Co-channel Interference), coverage gaps, and frequent roaming between APs." Another line: "Automatically assigns optimal channels to APs to minimize interference and improve overall network throughput and stability." High (undated).
- *AirMatch Configuration*, Validated Solution Guide (S8a; shows 13-Nov-25; **page only partly read verbatim, remainder from a model summary**, so its content is Low-Medium): channel and power plans per site, group and device.
- *rf arm-profile*, AOS 8 CLI reference (S8b; © 2026 HPE; no page date): ARM "allows each AP to determine the optimum channel selection and transmit power setting"; `dynamic-bw` can "move the AP radio to another 80MHz channel" when 20 MHz interferers affect an 80 MHz channel. Searched the page for EDCA, contention window, CWmin, CWmax, AIFSN, airtime fairness, CAC: **none found**. High.
- *RF Planning and Channel Management*, ArubaOS 8.6 (S8c; archived; © 2024): AirMatch "can react to detrimental RF events, such as radar and high noise levels"; plan changes applied "in the early morning to minimize client disruption". No contention-parameter content. High.

**Scope gap (Interpretation):** the Aruba pages read automate channel, power and bandwidth. They do not describe MAC contention parameters. ClientMatch was not fetched, so nothing is claimed about it.

---

## 5. Juniper Networks / Mist: Industry Findings

- *Radio Resource Management (RRM)*, Juniper Mist documentation (S7; no date on page): "It uses reinforcement learning to dynamically adjust radio settings including:" channel selection, transmit power levels, channel width, band steering between 2.4 and 5 GHz, and disabling or converting radios. "RRM can control the network band by turning off unneeded 2.4 GHz radios to reduce co-channel interference." Without RRM: "Wi-Fi and non-Wi-Fi interference (radio signal interference) causes clients and APs to pause transmissions for indefinite periods of time." High.
- *Radio Management* (S7b; no date): administrators choose "power range, your list of channels"; decisions "based on current channel and spectrum utilization". High.
- **Important for this project:** Mist RRM is documented as using reinforcement learning, but for the radio settings listed above. **No contention window, EDCA or backoff parameter appears** on either page. Fact (source). So "AI/RL-based RRM" in the market is evidence for RL in enterprise Wi-Fi operations, not for learned CW control.

---

## 6. Qualcomm and Broadcom: Wi-Fi 7/8 Developments

### 6.1 Qualcomm
- *Wi-Fi 8: Advancing wireless through ultra-high reliability, Part 1* (S1; white paper; August 2025; Rolf De Vegt). Page numbers as printed.
  - p.3: "Expected to be finalized in 2028, IEEE802.11bn will serve as the foundation for Wi-Fi 8".
  - p.5: enhancements "designed to support both isolated and overlapping network deployments, with a focus on environments characterized by congestion, interference, user mobility and coverage boundaries"; targets "Up to 25% lower latency at the 95th percentile" and "Up to 25% fewer dropped packets during transitions between access points".
  - p.8, "Smarter coordination for dense deployments": "In high-density environments, such as enterprise campuses, apartment buildings and public venues, Wi-Fi networks can face challenges with overlapping signals and airtime contention." and "By enabling APs to operate collaboratively rather than independently, Wi-Fi 8 introduces a smarter, more efficient way to access the medium and share resources between access points".
  - p.11: "Steady progress is being made with highlevel consensus already achieved on a significant portion of the new standard, while other elements remain under discussion."
  - Not mentioned: P-EDCA, NPCA, specific coordination schemes, contention window or backoff tuning. Medium (vendor white paper), key quotes High-quality.

### 6.2 Broadcom (secondary source only)
- Neowin, "Broadcom unveils its new Wi-Fi 8 silicon to meet AI edge demand" (S16; news; date not shown in extracted text; credits Broadcom). Names chips BCM6718, BCM43840, BCM43820, BCM43109 and lists UHR features "Inter-AP Coordination (Co-SR, Co-BF), Congestion Avoidance (DSO, NPCA, DBE), Range Enhancements (ELR, dRu), and Seamless Roaming". It also reports "All of the chips are fully compliant with IEEE 802.11bn and WFA Wi-Fi 8 specifications." Medium-Low.
- **Caution:** that compliance wording is Broadcom's claim about a draft specification (S10 says draft 1.0 was finalised July 2025 with publication targeted March 2028). Do not cite it as evidence of an approved standard. Broadcom's own press release could not be fetched.
- No CW/backoff tuning content in the page read.

### 6.3 MediaTek (other chip vendor, directly relevant)
- *Pioneering the Future with Wi-Fi 8, Part two: Reliable Communication* (S3; vendor white paper; release date 15 Feb 2025). Relevant, with page numbers:
  - p.7: multi-AP coordination "introduced in Wi-Fi 7, was deferred to Wi-Fi 8 due to its complexity."
  - p.12 (NPCA): "In the case of an 80 MHz CCI within a 160 MHz BSS, our study demonstrates a 37.5% increase in throughput." Vendor's own simulation study.
  - p.16 (HIP EDCA): "The existing ... EDCA mechanism provides a smaller backoff contention window for STAs transmitting AC3 (or AC-VO) data traffic ... However, the reduced contention window significantly increases the likelihood of collisions in environments where multiple STAs simultaneously generate AC3 data traffic."
  - p.17: HIP EDCA reconfigures EDCA parameters "to AIFSN = 2, CWmin = 0, and CWmax = 7 for transmitting the High Priority RTS"; in a setup with eight AC3 and eight AC1 STAs, long-tail AC3 latency falls "from >30 ms to <10 ms". Vendor study.
  - This is the only page read in this task that discusses contention window values explicitly; the values are **fixed rules for urgent traffic in a draft feature**, not adaptive selection.

---

## 7. Wi-Fi Alliance and IEEE: Standardization Developments

### 7.1 Status (what is standardised, what is not)

| Item | Status | Source |
|---|---|---|
| Wi-Fi 7 (IEEE 802.11be) | Certified: Wi-Fi Alliance "kicking off 2024 with a shiny new certification program for Wi-Fi 7"; MLO called its "marquee feature" | S17 (Wi-Fi Alliance; date not printed on the extracted page, about January 2024 by inference) |
| 802.11bn (UHR, Wi-Fi 8) | **Draft.** "as of July 2025, IEEE 802.11bn has finalized draft version 1.0"; "slated for publication in March 2028"; WFA test plan June 2027 and certification December 2027 | S10 (Samsung Research blog, undated) |
| Same, timing | "final approvals of IEEE 802.11bn to happen in May of 2028"; WFA certification "at CES 2028" | S11 (Wi-Fi NOW, 2026-06-16, news, Medium) |
| Same | Task group formed November 2023 with a cycle to 2028 | S18 (Galati-Giordano et al., arXiv 2303.10442v3, 21 Nov 2023) |

The three sources give different completion dates (March 2028, May 2028, "2028"). Say "expected in 2028". A Wikipedia page also lists September 2028 and was judged too weak to use.

### 7.2 What 802.11bn is reported to add (all draft)
- **Goals:** "25% lower latency at the 95th percentile of the latency distribution" and "25% fewer dropped packets especially when roaming between access points" (S10, §1); PAR described in S9 §I-C as requiring a 25 % reduction in the 95th-percentile latency and MPDU loss rate "particularly during transitions between overlapping networks".
- **Multi-AP coordination (MAPC):** "MAPC facilitates coordination among neighboring access points (APs) to decrease collisions and improve medium usage efficiency" (S9, §I-C; arXiv preprint, 22 Jul 2026, authors from CUHK, Huawei, Tsinghua; **peer review not stated**). The earlier primer states MAPC is meant "to prevent channel access contentions, especially in dense and heavily loaded environments" but "it is still to be decided what aspects of the coordination mechanism will be specified by the standard and what will be left for implementation" (S18, §V, 2023).
- **P-EDCA:** triggered "when the retransmission counter for an AC_VO frame reaches a predefined threshold"; other STAs' "ongoing backoff processes are instantly interrupted and suspended"; contenders then "randomly initialize a smaller backoff counter" (S9, §III-A). Designed "to truncate the tail of the access delay distribution for highly urgent traffic". Samsung: "APs enable or tune P-EDCA parameters using dedicated operation elements" and the result "is not necessarily higher average throughput, but a tighter distribution of delay for urgent packets" (S10, §3.1).
- **NPCA** (switch to a non-primary channel; "the STA must execute the standard backoff procedure on the new channel", S9 §III-B) and **DSO** (AP-controlled sub-band hopping, S10 §3.2).
- **Shift away from pure contention:** "This approach shifts Wi-Fi away from its historical reliance on purely nondeterministic contention mechanisms" (S9, §I-C).
- The earlier primer lists, as an opportunity, "extending enhanced distributed channel access (EDCA) with additional priority classes and associated channel access parameters, e.g., for backoff" (S18, §IV).

### 7.3 Do MAC contention and CW selection remain relevant?
- **Fact (source):** 802.11bn keeps EDCA backoff as the base access method and changes it only in special cases (P-EDCA for urgent traffic, backoff on a new channel under NPCA) (S9, S10). Multi-AP coordination is a new, draft, optional layer.
- **Interpretation:** because deployed clients and APs of earlier generations still use standard EDCA, and coordination needs capable APs and clients, standard contention will remain the dominant access method for years. This is an inference; none of the sources states it.
- Wi-Fi 7 (S2, S17) does not change CW selection either; its density features are MLO, MRU, puncturing and R-TWT.

---

## 8. Industry Comparison Table

| Organisation | Problem they name | Mechanism they document | Touches CW / EDCA / backoff? | Outside their stated scope | Source (confidence) |
|---|---|---|---|---|---|
| Cisco / Meraki | Congestion, retransmissions, co-channel overlap, "high density deployments ... features may not be aggressive enough" | AutoRF (channel), TPC (power), channel spreading; Wi-Fi 7 MLO, puncturing, R-TWT, dynamic bandwidth | **No** in pages read. Small-business APs: static EDCA templates | Backoff behaviour between co-channel BSSs | S2, S4, S5, S12 (High / Medium) |
| HPE Aruba | Co-channel interference, coverage gaps, roaming | AirMatch and ARM: channel, bandwidth, EIRP/power | **No** (CLI page searched) | MAC-layer contention | S6, S8a-c (High; S8a partly read) |
| Juniper / Mist | Interference makes "clients and APs ... pause transmissions"; capacity | RRM using reinforcement learning on channel, power, width, band, radio on/off | **No** | MAC-layer contention | S7 (High) |
| Qualcomm | Overlapping signals, airtime contention, latency spikes | Wi-Fi 8: multi-AP coordination, 25 % p95 latency target (draft) | Not mentioned | Specific mechanisms not named in Part 1 | S1 (Medium) |
| Broadcom | AI-edge demand; congestion avoidance | Wi-Fi 8 silicon: Co-SR, Co-BF, DSO, NPCA, DBE (as relayed by news) | Not mentioned | Primary source not read | S16 (Medium-Low) |
| MediaTek | Narrow-band CCI, legacy-device CCI, collisions of AC_VO traffic | NPCA, TXOP preemption, HIP EDCA (fixed CWmin 0, CWmax 7 for the high-priority RTS) | **Yes**, fixed rule for urgent traffic only | Adaptive CW for general traffic | S3 (Medium) |
| Extreme Networks | Density, interference, congested 2.4/5 GHz | 6 GHz-first, 4096-QAM, software-defined radios, sensor radio | **No** | MAC-layer contention | S14, S19 (Medium) |
| Huawei (other vendor) | High-density WLAN | Manual EDCA per AC, plus optional dynamic EDCA adjustment | **Yes**, optional automatic adjustment (algorithm not documented on the page) | Not stated | S13 (Medium) |
| IEEE / Wi-Fi Alliance | Reliability, tail latency, overlapping networks | 802.11bn draft: MAPC, P-EDCA, NPCA, DSO | P-EDCA changes backoff for urgent traffic (draft) | Final form of multi-AP coordination undecided as of 2023 sources | S9, S10, S18 (Medium) |

---

## 9. Evidence of Continuing Contention and Airtime Challenges

| # | Evidence (source, date, location) | Type | Confidence |
|---|---|---|---|
| 1 | Qualcomm, Aug 2025, p.8: dense networks "can face challenges with overlapping signals and airtime contention"; "These conditions can lead to latency spikes, degraded throughput" (S1) | Vendor white paper | Medium |
| 2 | Meraki docs, modified 2026-09-17: "congestion can occur to the point where devices spend more time receiving than sending"; overlapping co-channel APs "can lead to increased channel utilization" (S4) | Vendor technical documentation | High |
| 3 | Mist RRM docs: interference "causes clients and APs to pause transmissions for indefinite periods of time" (S7) | Vendor technical documentation | High |
| 4 | Cisco Wi-Fi 7 design guide, 2025-04-08: wide channels in dense networks "can lead to high channel reuse rates, co-channel interference, and poor performance" (S2) | Vendor design guide | High |
| 5 | IEEE 802.11bn PAR targets as described by arXiv 2607.19931 (22 Jul 2026) §I-C and Samsung §1: 25 % reductions in 95th-percentile latency and MPDU loss, "particularly during transitions between overlapping networks" (S9, S10) | Preprint; vendor research blog | Medium |
| 6 | Extreme Networks, 2026-02-23: "massive device density, volatile interference, and zero tolerance for downtime push traditional Wi-Fi to its limits"; AP5060 moves clients to 6 GHz "freeing valuable airtime for legacy clients" (S14) | Vendor blog | Medium |
| 7 | IEEE ComSoc Technology Blog, 2026-05-06, reprinting an Extreme press release: deployment "engineered to support peak densities approaching 90,000 concurrent users" (S19) | News reprint of a vendor release | Medium |
| 8 | MediaTek, Feb 2025, p.16: collisions of AC_VO traffic: "Even though retransmission mechanisms are in place to handle these collisions, their frequency remains high" (S3) | Vendor white paper | Medium |
| 9 | Cisco small-business and WLC EDCA templates (S12) show that CW parameters have long been a tunable lever in products | Documentation | Medium |

**Exact statistics about the prevalence of the problem.** None of the sources above gives a field-measured prevalence figure. The numeric statements found are design guidance or vendor studies: Meraki's "RSSI reported should be <10dB" for identifying a neighbouring AP (S4); Cisco's "Design limits of 50 ms or less latency and less than 30 ms jitter" (S2, §Switch Port Speed); MediaTek's 37.5 % NPCA throughput gain and ">30 ms to <10 ms" AC3 tail latency (S3, pp.12, 17; vendor simulations); IEEE targets of 25 % (S9, S10). **No exact industry-wide statistic of the form "% of dense deployments with high channel utilisation" was verified.** If the presentation needs one, it should come from a measurement study, which we did not find here.

Also relevant from this project's own earlier survey (not re-verified here): FC-MAPPO (arXiv 2509.23154) reports about 40 % collision rate for BEB at 10 saturated stations in ns-3, and Casasnovas et al. (arXiv 2511.10143) report that in a multi-player case greedy learners gained +30 % while legacy BSSs lost 59 %. Both are simulation results in preprints.

---

## 10. Current Commercial Solutions and Their Scope

| Layer | What products automate | Evidence |
|---|---|---|
| Channel plan | Meraki AutoRF, Aruba AirMatch/ARM, Mist RRM | S5, S6, S8b, S7 |
| Transmit power | Meraki TPC, AirMatch EIRP, ARM, RRM | S5, S6, S8b, S7 |
| Channel width | AirMatch, ARM `dynamic-bw`, RRM, Cisco Dynamic Bandwidth Selection | S6, S8b, S7, S2 |
| Band and radios | Mist band steering and radio disabling; Extreme 6 GHz-first, software-defined radios | S7, S14 |
| Wi-Fi 7 PHY/MAC | MLO, MRU, puncturing, R-TWT | S2, S17 |
| EDCA / CW parameters | Static profiles or manual values (Cisco small business); optional "dynamic-edca" (Huawei) | S12, S13 |
| Learned CW optimisation | **We did not find public product documentation explicitly advertising learned Contention Window optimization.** This does not mean no vendor implements it; vendor internals and unpublished firmware are outside what public documentation shows | pages read: S2, S4-S8, S14 |

Notes on S13 (Huawei WLAN AC V200R019C00 Command Reference, `wmm edca-client`; no date): the page lists manual per-AC settings (AIFSN 1 to 15, ECWmin/ECWmax 0 to 15, TXOP limit) and states "In high-density scenarios, it is recommended that you run the dynamic-edca enable command to enable dynamic EDCA parameter adjustment." The command's own page was not fetched, so what it adjusts and by what algorithm is **unknown**.

**What remains outside every solution above (Interpretation):** the RRM products tune the *medium* (channels, power, width) once per interval of minutes (Meraki's cost function updates "every 10 minutes" on average, S15), not the *per-slot access behaviour* of the nodes sharing it. 

---

## 11. Research Opportunity for Adaptive CW Optimization

### 11.1 Established industry problems (facts above)
- Co-channel APs share airtime and show high utilisation, latency spikes and retransmissions in dense sites (§9).
- Radio planning tools reduce overlap but are documented as not always sufficient in high density (S4: "may not be aggressive enough").
- 802.11bn is working on coordination and tail latency but is a 2028 standard (§7).

### 11.2 What adaptive CW could and could not address (Interpretation)
| Can plausibly help | Cannot help |
|---|---|
| Wasted slots and collisions among saturated contenders in one collision domain when the standard backoff is far from the best fixed CW (this project's `20,40` results: best static 39.62 Mbps vs BEB 27.66 Mbps, `docs/results/` and memory-bank) | RF interference from non-Wi-Fi sources |
| Fairness between BSSs that contend (a CW change shifts airtime shares) | Poor channel plans, insufficient channels, bad coverage |
| Adapting to load and station-count changes without manual EDCA profiles | Hidden-node corruption beyond what backoff can reduce |
| Complementing RRM's slow loop with a fast per-AP MAC loop | Low SNR, rate adaptation errors |

### 11.3 Where a decentralised AP-level controller could fit (Our hypothesis)
- **Dynamic contention adaptation:** AP-local CW chosen from local feedback in 10 ms steps, versus static profiles (S12) or minute-scale RRM (S15).
- **Shared-channel airtime efficiency:** AP agents sharing a channel without a controller, consistent with the industry's stated aim of APs operating "collaboratively rather than independently" (S1 p.8) but using no new signalling.
- **Network-level feedback:** team-level reward terms (fairness or aggregate) rather than only local throughput. **Our current evidence is mixed:** strictly local reward agents did not beat BEB or a global CW in our benchmark; a shared team reward helped the starved AP in a hidden-node chain at the cost of aggregate throughput (`REVIEW2_IMPLEMENTATION_STATE.md` §1, §10).
- **Robustness across traffic and network conditions:** no source found shows learned CW control tested across many scenarios without retraining. Wi-Fi 8 sources list only fixed-parameter special cases. This is our proposed research gap (see `recent-work-beyond-oscar-2026-11-01.md`), a hypothesis rather than a result.

### 11.4 Honest limits
- Non-learning rules (IdleSense) matched our learned global agent at 20 and 40 stations (38.77 vs 38.65 Mbps, p=0.31), so the case for *learning* must be made against such baselines, not against BEB alone.
- Standards-track mechanisms (P-EDCA, MAPC) are draft and rule-based; a learned controller would sit beside, not instead of, them. Compatibility with 802.11bn was not studied.

---

## 12. Relevance to the OSCAR Research Foundation

- OSCAR (Grasso, Raftopoulos, Schembra, IEEE ICC 2023, doi 10.1109/ICC45041.2023.10279663) sets one contention window at the AP with DDPG for a single BSS. Its premise (that the standard backoff is a poor fixed choice under load) is consistent with: Meraki's description of congestion (S4), MediaTek's statement that the AC_VO small window causes frequent collisions (S3 p.16), and the existence of tunable CWmin/CWmax/AIFSN in vendor products (S12, S13).
- The multi-AP extension is relevant because the industry statements concern **overlapping BSSs** (S1 p.5, p.8; S9 §I-C; S3 p.7). OSCAR itself addresses one BSS.
- None of the industry pages read cites OSCAR or learned CW control. Absence from these pages is not evidence about the research literature.
- The project's own record: independent per-AP agents were not better than BEB at `20,40` (−5.6 ± 76 %, n=3); this must be presented alongside any industry-relevance argument.

---

## 13. Key Findings Suitable for an Academic Presentation

1. Qualcomm (Aug 2025) names "overlapping signals and airtime contention" as a dense-deployment problem and lists multi-AP coordination as the Wi-Fi 8 response (S1, p.8).
2. IEEE 802.11bn's targets are measured as 25 % lower 95th-percentile latency and 25 % lower MPDU loss in overlapping-network scenarios; the standard is expected in 2028 (S9, S10, S11).
3. Enterprise RRM (Meraki, Aruba, Mist) automates channel, power and width. The pages read do not mention CW or backoff tuning (S4-S8). Mist's RRM uses reinforcement learning, but for radio settings (S7).
4. CW and EDCA parameters are tunable in products, mainly statically (S12); one vendor documents optional dynamic EDCA for high density (S13).
5. Wi-Fi 8's CW-related changes are rule-based special cases (P-EDCA, HIP EDCA with CWmax = 7 for urgent traffic) in draft (S3, S9, S10).

---

## 14. Complete References and Source Links

Format: ID. Title. Publisher. Date. Type. URL. Confidence. Where used.

- **S1.** *Wi-Fi 8: Advancing wireless through ultra-high reliability, Part 1*. Qualcomm Technologies, Inc. (Rolf De Vegt). August 2025. White paper. https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Qualcomm-Wi-Fi-8-Advancing-wireless-through-ultra-high-reliability-Part-1-white-paper.pdf . Medium. Pages 3, 5, 7, 8, 11.
- **S2.** *Wi-Fi 7 and the Growing Future of Wireless Design Guide*. Cisco. Updated 2025-04-08. Design guide. https://www.cisco.com/c/en/us/products/collateral/networking/wireless/wifi7-future-of-wireless-dg.html . High.
- **S3.** *Pioneering the Future with Wi-Fi 8, Part two: Reliable Communication* (MediaTek Filogic White Paper). MediaTek Inc. Release date 15 Feb 2025. Vendor white paper. https://728015.fs1.hubspotusercontent-na1.net/hubfs/728015/MediaTek%20Wi-Fi%208%20WhitePaper%20-%20Part%202.pdf . Medium (page numbers inferred from PDF footers).
- **S4.** *Channel Planning Best Practices*. Cisco Meraki Documentation. Published 2020-10-05, modified 2026-09-17 (page metadata). Technical documentation. https://documentation.meraki.com/Wireless/Design_and_Configure/Architecture_and_Best_Practices/Channel_Planning_Best_Practices . High.
- **S5.** *Channel Planning Overview*. Cisco Meraki Documentation. Published 2020-10-05, modified 2026-09-18 (metadata). Technical documentation. https://documentation.meraki.com/Wireless/Operate_and_Maintain/User_Guides/Radio_Settings/Channel_Planning_Overview . High.
- **S6.** *AirMatch*. HPE Aruba Networking Central Online Help. No date shown. Technical documentation. https://arubanetworking.hpe.com/techdocs/new-central/content/cfg/services/airmatch/airmatch.htm . High (undated).
- **S7.** *Radio Resource Management (RRM)* and *Radio Management*. Juniper Networks (Mist) documentation. No date shown. Technical documentation. https://www.juniper.net/documentation/us/en/software/mist/mist-wireless/topics/concept/mist-radio-resource-management.html ; https://www.juniper.net/documentation/us/en/software/mist/mist-wireless/topics/concept/wireless-rrm.html . High (undated).
- **S8a.** *AirMatch Configuration*, Validated Solution Guide. HPE Aruba Networking. Shows 13-Nov-25. https://arubanetworking.hpe.com/techdocs/VSG/docs/020-campus-deploy/campus-large-deploy-140-configuring-airmatch/ . Low-Medium (partly read).
- **S8b.** *rf arm-profile*, AOS 8 CLI reference. HPE Aruba Networking, © 2026. https://arubanetworking.hpe.com/techdocs/CLI-Bank/Content/aos8/rf-arm-pro.htm . High.
- **S8c.** *RF Planning and Channel Management*, ArubaOS 8.6 Help (archived). HPE, © 2024. https://arubanetworking.hpe.com/techdocs/Archived/AOS-8/ArubaOS_86_Web_Help/Content/arubaos-solutions/arm/rf-plan-chan-mgmt.htm . High.
- **S9.** Liu, Gan, Dai, Dong, Chan, Song. *Towards Ultra-High Reliability in Wi-Fi 8: IEEE 802.11bn Core Mechanisms, mmWave Integration, and Performance Verification*. arXiv:2607.19931v1 [cs.NI], 22 Jul 2026. Research preprint (peer review not stated). https://arxiv.org/abs/2607.19931 . Medium. Only the first ~40 % of the text was read verbatim; later sections (including performance numbers) were not verified and are not used.
- **S10.** *IEEE 802.11bn (Ultra-High Reliability (UHR), Wi-Fi 8)*. Samsung Research blog (Ha, Shafin, et al.). Undated; content as of July 2025 and later. Vendor research blog. https://research.samsung.com/blog/IEEE-802-11bn-Ultra-High-Reliability-UHR-Wi-Fi-8 . Medium.
- **S11.** *Wi-Fi 8 standard on track for completion in 1H2028 with certification scheduled for January 2028*. Wi-Fi NOW (Claus Hetting). 2026-06-16 (modified 2026-07-14). News. https://wifinowglobal.com/news-blog/wi-fi-8-standard-on-track-for-completion-in-1h2028-with-certification-scheduled-for-january-2028/ . Medium.
- **S12.** *Wireless Quality of Service (QoS) Configuration on WAP121 and WAP321*. Cisco Small Business support document. Undated (firmware 1.0.3.4). Technical documentation. https://www.cisco.com/c/en/us/support/docs/smb/wireless/cisco-small-business-100-series-wireless-access-points/smb2141-wireless-quality-of-service-qos-configuration-on-wap121-and.pdf . Medium.
- **S13.** *wmm edca-client (SSID profile view)*, WLAN AC V200R019C00 Command Reference. Huawei. Undated. Technical documentation. https://support.huawei.com/enterprise/en/doc/EDOC1100096312/6fc599ca/wmm-edca-client-ssid-profile-view . Medium (other vendor; undated).
- **S14.** David Coleman. *Stadium Wi-Fi 7: Redefining High-Density Connectivity with the AP5060*. Extreme Networks blog. 2026-02-23. Vendor blog. https://www.extremenetworks.com/resources/blogs/stadium-wi-fi-7-redefining-high-density-connectivity-with-AP5060 . Medium.
- **S15.** *WiFi Spectrum Analysis* (solution guide). Cisco Systems / Meraki. September 2014. Vendor solution guide. https://meraki.cisco.com/lib/pdf/meraki_whitepaper_spectrum_analysis.pdf . High (old).
- **S16.** *Broadcom unveils its new Wi-Fi 8 silicon to meet AI edge demand*. Neowin (source: Broadcom). Date not shown. News relaying a vendor release. https://www.neowin.net/amp/broadcom-unveils-its-new-wi-fi-8-silicon-to-meet-ai-edge-demand/ . Medium-Low.
- **S17.** *Wi-Fi Alliance's official certification program for Wi-Fi 7 has begun*. Wi-Fi Alliance. Date not printed (about January 2024 by inference). Announcement. https://www.wi-fi.org/media-content/wi-fi-7-certification-is-here . Medium.
- **S18.** Galati-Giordano, Geraci, Carrascosa, Bellalta. *What Will Wi-Fi 8 Be? A Primer on IEEE 802.11bn Ultra High Reliability*. arXiv:2303.10442v3, 21 Nov 2023. Research preprint. https://arxiv.org/abs/2303.10442 . Medium (2023; predates the draft).
- **S19.** Alan Weissberger. *Extreme Networks deploys Wi-Fi 7 (IEEE 802.11be) at University of Florida's "Swamp"*. IEEE ComSoc Technology Blog. 2026-05-06. News reprint of a vendor release. https://techblog.comsoc.org/2026/05/06/extreme-networks-deploys-wi-fi-7-ieee-802-11be-at-university-of-floridas-swamp-stadium/ . Medium.
- **S20.** Grasso, Raftopoulos, Schembra. *OSCAR: A Contention Window Optimization Approach Using Deep Reinforcement Learning*. IEEE ICC 2023, pp. 459-465, doi:10.1109/ICC45041.2023.10279663. Conference paper.
- **S21.** Cisco Community thread *Can somebody clarify EDCA parameters WLC 7.6*. Posts 2014 to 2022. Forum. https://community.cisco.com/t5/wireless/can-somebody-clarify-edca-parameters-wlc-7-6/m-p/4603041/highlight/true . Low. Used only as background.

**Searched but not used (reasons):** Qualcomm OnQ blog (metadata only), convergedigest Broadcom page (fetch failed), Wireless Broadband Alliance Wi-Fi 8 article (server error), Purple.ai guides (marketing), Ofinno 2023 white paper (dated January 2023, superseded), Wikipedia (weak and conflicting dates). **Not investigated:** Aruba ClientMatch documentation, Cisco CleanAir/RRM configuration guides, Extreme's ExtremeCloud IQ AI documentation, Wi-Fi Alliance Wi-Fi 8 materials, Ekahau or WBA field-measurement reports.

---

## 15. Presentation-Oriented Section

### A. Best 5 industry findings (strongest and most verifiable)
1. **Qualcomm, Aug 2025 (S1, p.8):** dense networks "can face challenges with overlapping signals and airtime contention", leading to "latency spikes, degraded throughput".
2. **Cisco Meraki documentation, modified Sept 2026 (S4):** congestion reaches the point where "devices spend more time receiving than sending"; overlapping co-channel APs "can lead to increased channel utilization"; and the vendor's own RRM "may not be aggressive enough" in high density.
3. **IEEE 802.11bn (S9, S10, S11):** a draft standard whose targets are 25 % lower 95th-percentile latency and MPDU loss in overlapping networks, with multi-AP coordination "to decrease collisions"; final approval expected 2028.
4. **Enterprise RRM scope (S4-S8):** Meraki, Aruba and Mist automate channel, power and width; the pages read do not mention contention-window or backoff tuning. Mist's RRM uses reinforcement learning for radio settings (S7).
5. **Wi-Fi 8 CW changes are narrow and rule-based (S3, S9):** P-EDCA / HIP EDCA modify backoff only for urgent traffic, with fixed parameters (e.g., CWmin = 0, CWmax = 7 for the high-priority RTS), in a draft.

### B. Best 3 sources before the project guide
1. **S1 Qualcomm Part 1 white paper**: explicit dense-deployment problem statement with page numbers, and the 2028 timeline.
2. **S4 Cisco Meraki "Channel Planning Best Practices"**: official documentation that separates channel utilisation, backoff and retransmissions, and states the limits of automation in high density.
3. **S9 arXiv 2607.19931 (with S10 Samsung for the timeline)**: the most recent technical description of 802.11bn mechanisms, with the caveats that it is a preprint and only part was verified.

### C. Suggested slide: INDUSTRY RELEVANCE: CURRENT CHALLENGES IN DENSE WI-FI NETWORKS
- **Problem still named by vendors:** overlapping BSSs cause "airtime contention", "latency spikes, degraded throughput" (Qualcomm, 2025, S1 p.8).
- **Congestion mechanics:** devices defer with random back-off and retransmit; co-channel APs raise channel utilisation (Cisco Meraki docs, 2026, S4).
- **Automation today:** AutoRF, AirMatch/ARM, Mist RRM tune channel, power and width. No CW tuning in the pages we read (Cisco, HPE Aruba, Juniper; S4-S8).
- **Standards are still moving:** Wi-Fi 8 (802.11bn) draft targets 25 % lower p95 latency; multi-AP coordination; expected 2028 (IEEE/Samsung/Wi-Fi NOW; S9-S11).
- **Gap we study (hypothesis):** decentralised, adaptive AP-level CW control; "We did not find public product documentation explicitly advertising learned Contention Window optimization."
- Short citations: Qualcomm WP Aug 2025 p.8; Meraki docs (mod. 2026-09-17); arXiv 2607.19931 §I-C; Samsung Research blog §1.

### D. Suggested visuals (cite; figures were **not** visually inspected in this session, so confirm figure numbers before use)
- **Qualcomm white paper (S1), p.8 "Smarter coordination for dense deployments"** and p.5 (the three IEEE targets): check the page for the diagram or table before citing the figure number. URL in S1.
- **MediaTek white paper (S3), p.11 (overlapping-home CCI scenario, referred to in the text as Figure 5) and p.12 (NPCA scenario)**: official-style illustrations of co-channel overlap; vendor-authored.
- **Galati-Giordano primer (S18), "Fig. 1" summarising the 802.11bn standardisation effort (§II.B)**: for a timeline visual; 2023, so show with the 2028 update from S10/S11.
- **Meraki channel-planning page (S4), "Overlapping Coverage Cells" and "2.4 GHz Channel Plan" sections**: documentation diagrams that show overlapping cells and non-overlapping channels 1, 6, 11.
- If the guide wants a project-specific visual: the hidden-chain table and `docs/figures/v2.2.0/main-20-40/` plots in this repo (our own results, not industry sources).
