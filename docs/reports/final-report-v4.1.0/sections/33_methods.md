## 3. Controllers compared

### 3.1 Families
| Family | Controllers | Information used | Per-AP isolation |
|---|---|---|---|
| Standard | BEB; BEB with RTS/CTS | none | yes |
| Published rules | IdleSense, DAC (Patras), BLADE, KW (Gawłowicz) | idle slots, failure rates, delay, or neighbour goodput (KW) | yes, except KW |
| Bandit | UCB per AP; contextual UCB | own goodput, active stations | yes |
| OSCAR family | **Global-CW OSCAR** (one DDPG agent, one CW broadcast to all APs); **independent per-AP OSCAR** (one DDPG agent per AP, own loss, own goodput reward); PF learner (independent agents with a proportional-fair reward); CCOD (global form) | loss history; network goodput (global forms) | independent and PF: yes; global forms: no |
| Shared actor | RAFA: one DDPG actor shared by the APs of a scenario with each AP's own idle-slot, retry, goodput and active-station inputs, an alpha-fair reward and a fair-floor penalty | own radio only | yes (shared weights) |
| Central critic | Actors per AP, one shared critic (CTDE), v1.7 to v1.9 | joint critic | partly |
| Central online control | **kwdirect** (SPSA-style search on log2 CW of every AP with a floor penalty and an accept/revert guard); coord (kwdirect plus a max-weight muting schedule); cascade (DAC loop plus KW search) | goodput of all APs | no, by design |
| Static references | F1: best exact static CW per AP; F2: best static CWmin (with doubling); F3: two-phase CW schedule (S4 only); common static CW (the same value for all APs); model-based static CW from Patras et al.'s formula | validated offline on separate seeds | n/a |

Neither "centralized Actor" nor "global Critic" in the mentor's scenarios corresponds to one single controller of the project. The closest ones are used in Part I: Global-CW OSCAR (one agent, one CW for all APs), RAFA and the central-critic prototype (one actor, a CW per AP) and kwdirect/coord (one central controller, a CW per AP). Part I always names the controller behind an answer.

### 3.2 The OSCAR-style learners in detail
- **Observation and action.** Independent per-AP agents observe the loss ratio of their own BSS in the last step; the actor outputs a in [-1, 1] that is mapped to a CW exponent. A 300-step history exists but only the newest value is used, as in the original code.
- **Reward.** Own goodput divided by the load the BSS offers (independent); network goodput divided by the total offered load (global forms).
- **DDPG.** Actor and critic with two hidden layers of 128 units, batch 32, discount 0.7, soft update 1e-3, exploration noise 0.1, 300 random warm-up steps, learning rates 4e-4 (actor) and 4e-3 (critic).
- **Training protocol used in the max-CW study and in the report cells.** 12 episodes of 15 s per training run (RAFA: 6), three training seeds, frozen noise-free evaluation on separate seeds. Learned controllers are evaluated after training; the online adaptation of the learner during the measurement is not used.
- **CW 0/0 start bug (fixed in v2.0.0).** Until v1.9.0 the agent modes started with CW 0 and starved stations during warm-up. Agent results from v1.1.0 to v1.9.0 are therefore treated as pre-fix and are not used for conclusions; only runs of v2.0.0 and later are.

### 3.3 kwdirect and its relatives
`kwdirect` (project code, file `ap_layered_v4_1_0.py`) works in layers. Layer L2 probes the CW of each AP up and down by a factor (delta) in the log domain, estimates the gradient of the station-weighted alpha-fair utility over a probe window of 0.6 s, takes a step (eta), applies a penalty when an AP falls below its floor, and reverts a step that makes the utility worse (accept/revert guard). It needs the goodput of all APs, so it is a central controller. `coord` adds layer L3, a max-weight muting schedule for the hidden chain, and is used only where the schedule helps (S4 at alpha 1). Layer L1 is the DAC loop. These controllers were tuned on seeds 0 to 3 and then evaluated on fresh seeds (tournament seeds 300 to 309; confirmation seeds 103 to 122).
