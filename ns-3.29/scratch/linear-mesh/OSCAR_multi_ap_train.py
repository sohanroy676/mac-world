"""v0.7.0/v0.8.0/v0.9.0: one independent DDPG agent (actor+critic+replay) per AP in one joint ns-3 simulation.

Each agent sees only its own AP's newest loss and its own reward (from parse_ap_info, not the
scalar gym reward). Local critics only. Differences from OSCAR_train.py (deliberate): warm-up
actions are sampled in [-1,1] and stored as such (the baseline stores U(0,6) in the replay).
v0.8.0: per-AP + global W&B metrics (design section 7 names; offline unless --online).
v0.9.0: --check also recomputes obs (Test A) and reward (Test D) per AP and checks episode resets (Test E).
v1.1.0: --mode independent (default, above) | global (ONE agent, one CW broadcast to every AP; state = network
loss (sum tx - sum rx)/sum tx, reward = network goodput / (offered load x all STAs x step)) | beb (ns-3 --dryRun
through the same stepping loop, no agent: standard 802.11 measured in the same per-step window).
v1.8.0: --mode central (CTDE): N local actors (each sees only its own loss) + ONE shared critic Q(s_joint, a_joint)
trained on the global goodput reward, joint replay, MADDPG-style actor update (agents/our_ddpg/central.py).
Run from this directory: ../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --check
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time


parser = argparse.ArgumentParser()
parser.add_argument("--apStaCounts", default="20,40")
parser.add_argument("--simTime", type=float, default=15)
parser.add_argument("--stepTime", type=float, default=0.01)
parser.add_argument("--historyLength", type=int, default=300)
parser.add_argument("--episodes", type=int, default=1)
parser.add_argument("--start_timesteps", type=int, default=300)
parser.add_argument("--batch_size", type=int, default=32)
parser.add_argument("--expl_noise", type=float, default=0.1)
parser.add_argument("--discount", type=float, default=0.7)
parser.add_argument("--tau", type=float, default=1e-3)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--cwReadbackEvery", type=float, default=0.0, help="diagnostic: log STA CW readback every N sim seconds (0 = off)")
parser.add_argument("--trafficStart", type=float, default=0.0, help="diagnostic: time (s) the data sources start (0 = cw.cc default)")
parser.add_argument("--staMaxMissedBeacons", type=int, default=0, help="diagnostic: StaWifiMac MaxMissedBeacons (0 = ns-3 default 10)")
parser.add_argument("--offeredLoad", type=float, default=150.0, help="per-STA offered load in Mbps (cw.cc offeredLoad)")
parser.add_argument("--apHidden", default="", help="v3.4.0 scenario: 1-based AP pairs whose BSSs cannot hear each other, e.g. 1-3 (cw.cc --apHidden)")
parser.add_argument("--hiddenLoss", type=float, default=0.0, help="path loss in dB between hidden pairs (0 = cw.cc default 200)")
parser.add_argument("--apLoads", default="", help="v3.4.0 scenario: per-STA offered load in Mbps per AP, e.g. 150,150,5 (cw.cc --apLoads; default every AP uses --offeredLoad)")
parser.add_argument("--reward", choices=["local", "pf"], default="local", help="independent/shared replay reward: local = own goodput (alpha mixes in network goodput); pf = proportional fair, 1 + mean_i log(eps + r_i) / -log(eps), same value for every agent")
parser.add_argument("--rewardScale", type=float, default=1.0, help="multiplies the reward stored in replay (central/global/independent/shared; 1 = unchanged)")
parser.add_argument("--alpha", type=float, default=1.0, help="independent/shared: replay reward = alpha*own + (1-alpha)*network goodput reward (1 = strictly local)")
parser.add_argument("--obs", choices=["loss", "hist"], default="loss", help="independent/shared state: loss = newest own loss; hist = [newest, mean, std over --obsWindow own steps, own previous action]")
parser.add_argument("--obsWindow", type=int, default=50, help="steps of the AP's own loss history used by --obs hist")
parser.add_argument("--tag", default="", help="variant label stored in config.json (used by aggregate_bench.py)")
parser.add_argument("--print_every", type=int, default=10)
parser.add_argument("--online", action="store_true", help="sync W&B online (default: offline)")
parser.add_argument("--wandb_project", default="contention_window")
parser.add_argument("--mode", choices=["independent", "global", "beb", "central", "shared", "static"], default="independent")
parser.add_argument("--apCws", default="", help="static mode only: fixed CW per AP, e.g. 64,512 (no agent; cw.cc applies it from t=0)")
parser.add_argument("--check", action="store_true", help="assert per-AP isolation every step")
parser.add_argument("--algo", choices=["ddpg", "td3"], default="ddpg", help="learner for independent/global/shared (td3: twin critics, delayed actor, target smoothing)")
parser.add_argument("--varySeeds", action="store_true", help="episode e uses ns-3 seed (seed+1)+1000*e instead of the same seed every episode")
parser.add_argument("--saveActor", default="", help="after training save every agent to DIR/agent<i>_{actor,critic,...}")
parser.add_argument("--loadActor", default="", help="load agents from DIR/agent<i>_* before the run (use with --eval)")
parser.add_argument("--eval", action="store_true", help="frozen evaluation: needs --loadActor; no exploration noise, no warm-up, no replay, no training")
parser.add_argument("--cwMinOnly", action="store_true", help="agent action sets CWmin only; CWmax stays 1023 so BEB doubling is kept (multi-AP agent modes)")
args = parser.parse_args()

# W&B mode must be decided before wandb is imported.
if not args.online:
    os.environ.setdefault("WANDB_MODE", "offline")

import numpy as np  # noqa: E402
import torch  # noqa: E402
import wandb  # noqa: E402

from agents.our_ddpg.Our_DDPG import DDPG  # noqa: E402
from agents.our_ddpg.TD3 import TD3  # noqa: E402
from agents.our_ddpg.preprocessor import Preprocessor  # noqa: E402
from agents.our_ddpg.central import CentralDDPG  # noqa: E402
from agents.our_ddpg.utils import JointReplayBuffer, ReplayBuffer  # noqa: E402
from config import wandb_entity  # noqa: E402
from exceptions import AlreadyRunningException  # noqa: E402
from multi_ap import PAYLOAD_BITS, jain, parse_ap_info, reshape_obs, step_metrics  # noqa: E402
from wrappers import EnvWrapper  # noqa: E402

counts = [int(c) for c in args.apStaCounts.split(",")]
n = len(counts)
assert n > 1, "multi-AP trainer needs >1 AP (use OSCAR_train.py for one)"
steps_per_ep = int(args.simTime / args.stepTime)
state_dim = action_dim = 1
max_action = 1
real_max_action = 6
OFFERED_MBPS = args.offeredLoad  # per-STA offered load, cw.cc offeredLoad
LOADS = [float(x) for x in args.apLoads.split(",")] if args.apLoads else [OFFERED_MBPS] * len(args.apStaCounts.split(","))  # per-AP, per-STA load
assert len(LOADS) == n and min(LOADS) > 0, "--apLoads: one positive load per AP"
OFFERED_TOTAL = sum(c * l for c, l in zip(counts, LOADS))  # network offered load in Mbps (all STAs)

torch.manual_seed(args.seed)
np.random.seed(args.seed)

sim_args = {"simTime": args.simTime, "envStepTime": args.stepTime, "historyLength": args.historyLength,
            "agentType": "continuous", "scenario": "basic", "apStaCounts": args.apStaCounts,
            "seed": args.seed + 1, "offeredLoad": "%g" % args.offeredLoad}  # ns-3 rejects seed 0, so ns-3 seed = python seed + 1
if args.apHidden:
    sim_args["apHidden"] = args.apHidden
if args.hiddenLoss > 0:
    sim_args["hiddenLoss"] = args.hiddenLoss
if args.apLoads:
    sim_args["apLoads"] = args.apLoads
if args.cwReadbackEvery > 0:
    sim_args["cwReadbackEvery"] = args.cwReadbackEvery
if args.trafficStart > 0:
    sim_args["trafficStart"] = args.trafficStart
if args.staMaxMissedBeacons > 0:
    sim_args["staMaxMissedBeacons"] = args.staMaxMissedBeacons
static_cws = [int(c) for c in args.apCws.split(",")] if args.apCws else []
assert (args.mode == "static") == bool(static_cws), "--mode static needs --apCws (and only static takes it)"
assert not static_cws or (len(static_cws) == n and all(16 <= c <= 1024 for c in static_cws)), "--apCws: one CW in 16..1024 per AP"
if static_cws:
    sim_args["apCws"] = args.apCws
if args.mode == "beb":
    sim_args["dryRun"] = "true"  # cw.cc skips setApCw; every AP keeps BEB CW 16..1024
n_agents = {"independent": n, "global": 1, "beb": 0, "central": 0, "shared": 1, "static": 0}[args.mode]  # central: one CentralDDPG object; shared: one DDPG for all APs
LOCAL_MODES = ("independent", "shared")
assert args.obs == "loss" or args.mode in LOCAL_MODES, "--obs hist only for independent/shared"
assert args.alpha == 1.0 or args.mode in LOCAL_MODES, "--alpha only for independent/shared"
assert args.reward == "local" or (args.mode in LOCAL_MODES and args.alpha == 1.0), "--reward pf only for independent/shared with --alpha 1 (pf replaces the mix)"
assert 0.0 <= args.alpha <= 1.0 and 1 <= args.obsWindow <= args.historyLength
local_dim = 4 if args.obs == "hist" else 1
AGENT_MODES = ("independent", "global", "shared")
assert args.algo == "ddpg" or args.mode in AGENT_MODES, "--algo td3 only for independent/global/shared"
assert not (args.saveActor or args.loadActor or args.eval) or args.mode in AGENT_MODES, "--saveActor/--loadActor/--eval only for independent/global/shared"
assert args.eval == bool(args.loadActor), "--eval needs --loadActor (and --loadActor needs --eval)"
assert not (args.eval and args.saveActor), "--eval does not train, so there is nothing to --saveActor"
assert not args.cwMinOnly or args.mode in AGENT_MODES + ("central",), "--cwMinOnly only for agent modes"
if args.cwMinOnly:
    sim_args["cwMinOnly"] = "true"
learning = not args.eval  # eval: frozen actors, no noise, no warm-up, no replay, no training
expl_noise = 0.0 if args.eval else args.expl_noise
ns3_seeds = [args.seed + 1 + (1000 * e if args.varySeeds else 0) for e in range(args.episodes)]


def local_states(S_rows, prev_acts):
    """Per-AP local state from that AP's OWN history row only (row 0 = newest loss)."""
    if args.obs == "loss":
        return S_rows[:, :1].copy()
    w = S_rows[:, :args.obsWindow]
    return np.stack([S_rows[:, 0], w.mean(1), w.std(1), prev_acts], 1).astype(np.float32)

try:
    git_rev = subprocess.check_output(["git", "describe", "--tags", "--always", "--dirty"], stderr=subprocess.DEVNULL,
                                      cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
except (OSError, subprocess.CalledProcessError):
    git_rev = "unknown"

out_dir = "results/multi-ap-%s" % time.strftime("%Y%m%d-%H%M%S")
os.makedirs(out_dir)
with open(os.path.join(out_dir, "config.json"), "w") as f:
    json.dump(dict(vars(args), ns3_seed=args.seed + 1, ns3_seeds=ns3_seeds, counts=counts, git_rev=git_rev), f)
trace_f = open(os.path.join(out_dir, "trace.csv"), "w", newline="")
trace = csv.writer(trace_f)
trace.writerow(["episode", "step", "ap", "state", "action", "real_action", "reward", "next_state", "cw_set",
                "cw_ap", "loss", "rx", "tx", "pp_mean", "pp_std", "actor_loss", "critic_loss"])

run = wandb.init(name="%s %s s%d" % (args.apStaCounts, args.mode, args.seed), entity=os.environ.get("WANDB_ENTITY", wandb_entity),
                 project=args.wandb_project, tags=["multi-ap", "mode-" + args.mode, git_rev], reinit=True,
                 config=dict(vars(args), AP_Count=n, Stations_Per_AP=counts))

Learner = TD3 if args.algo == "td3" else DDPG
agents = [Learner(local_dim, action_dim, max_action, args.discount, args.tau) for _ in range(n_agents)]
if args.loadActor:
    for i, a in enumerate(agents):
        a.load(os.path.join(args.loadActor, "agent%d" % i))
replays = [ReplayBuffer(local_dim, action_dim) for _ in range(n_agents)]
central = CentralDDPG(n, max_action, args.discount, args.tau) if args.mode == "central" else None
joint = JointReplayBuffer(n) if args.mode == "central" else None
preprocess = Preprocessor(False).preprocess


def scalar(x):
    return float(x.detach().cpu().item()) if hasattr(x, "detach") else float(x)


def agent_loss(i, name):
    """Loss of the agent that acts for AP i (independent: own; global: the shared one; beb: none -> 0)."""
    if args.mode in ("beb", "static"):
        return 0.0
    if args.mode == "central":
        return scalar(central.actor_losses[i] if name == "actor_loss" else central.critic_loss)
    return scalar(getattr(agents[i if args.mode == "independent" else 0], name))


def global_reward(recs):
    """Network goodput normalized by offered load of all STAs (global and central modes)."""
    rx_g = sum(r["rx"] for r in recs)
    return min(1.0, max(0.0, rx_g * PAYLOAD_BITS / 1e6 / (OFFERED_TOTAL * args.stepTime)))


PF_EPS = 1e-3


def pf_reward(r_own):
    """Proportional-fair team reward from the per-AP normalized goodputs: 0 at zero goodput, about 1 at full load."""
    r_own = np.asarray(r_own, dtype=np.float64)
    return float(min(1.0, max(0.0, 1.0 + np.log(PF_EPS + r_own).mean() / -np.log(PF_EPS))))


fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("CHECK FAIL:", msg)


if args.check:
    param_ids = [{p.data_ptr() for net in (a.actor, a.actor_target, a.critic, a.critic_target)
                  for p in net.parameters()} for a in agents]
    for i in range(n_agents):
        for j in range(i + 1, n_agents):
            check(not (param_ids[i] & param_ids[j]), "agents %d,%d share parameters" % (i, j))
    check(len({id(r) for r in replays}) == n_agents, "replay buffers are not distinct")

if args.mode == "central" and args.check:
    # Execution isolation: an actor only ever receives a [B, 1] tensor; during execution B == 1 and the value is s_i.
    exec_probe = {"expect": None}

    def make_hook(i):
        def hook(module, inp):
            x = inp[0]
            check(x.dim() == 2 and x.shape[1] == 1, "actor %d input shape %s is not [B,1]" % (i, tuple(x.shape)))
            if exec_probe["expect"] is not None:
                check(x.shape[0] == 1 and abs(float(x[0, 0]) - float(exec_probe["expect"][i])) < 1e-6,
                      "actor %d execution input is not its own s_i" % i)
        return hook
    for i, a in enumerate(central.actors):
        a.register_forward_pre_hook(make_hook(i))
    ids = [{p.data_ptr() for net in (a, t) for p in net.parameters()}
           for a, t in zip(central.actors, central.actor_targets)]
    for i in range(n):
        for j in range(i + 1, n):
            check(not (ids[i] & ids[j]), "central actors %d,%d share parameters" % (i, j))
        check(not (ids[i] & {p.data_ptr() for p in central.critic.parameters()}), "actor %d shares critic parameters" % i)

env = EnvWrapper(1, **sim_args)
print("APs:", counts, "steps/ep:", steps_per_ep, "out:", out_dir)
time_step = 0
reward_cols = [[] for _ in range(n)]
logged = []
try:
    for episode in range(args.episodes):
        if args.varySeeds and episode > 0:
            env.commands = env._craft_commands(dict(sim_args, seed=ns3_seeds[episode]))
        print("episode %d ns-3 seed %d" % (episode, ns3_seeds[episode]), flush=True)
        try:
            env.run()
        except AlreadyRunningException:
            pass
        S = reshape_obs(env.reset()[0], n)
        prev_acts = np.full(n, -1.0, dtype=np.float32)  # CW starts at BEB 16 = real action 0 = act -1
        L = local_states(S, prev_acts)
        S_g = np.zeros(state_dim, dtype=np.float32)  # global mode: network loss; 0 before the first step
        ep_reward = np.zeros(n)
        for step in range(1, steps_per_ep + 1):
            acts = np.zeros(n, dtype=np.float32)
            if args.mode in ("independent", "central", "shared"):
                if args.mode == "central" and args.check:
                    exec_probe["expect"] = S[:, 0]
                for i in range(n):
                    if learning and time_step < args.start_timesteps:
                        acts[i] = np.random.uniform(-max_action, max_action)
                    else:
                        sel = agents[i] if args.mode == "independent" else agents[0] if args.mode == "shared" else None
                        a = (sel.select_action(L[i]) if sel else central.select_action(i, S[i, :state_dim])) \
                            + np.random.normal(0, max_action * expl_noise)
                        acts[i] = np.clip(a, -max_action, max_action)[0]
                if args.mode == "central" and args.check:
                    exec_probe["expect"] = None
            elif args.mode == "global":
                if learning and time_step < args.start_timesteps:
                    acts[:] = np.random.uniform(-max_action, max_action)
                else:
                    a = agents[0].select_action(S_g) + np.random.normal(0, max_action * expl_noise)
                    acts[:] = np.clip(a, -max_action, max_action)[0]
            real = (real_max_action * (acts + 1) / 2).astype(np.float32)  # beb: ignored by cw.cc (dryRun)

            obs, _, done, info = env.step(np.array([real], dtype=np.float32))
            S2 = reshape_obs(obs[0], n)
            recs = parse_ap_info(info[0], n)
            L2 = local_states(S2, acts)
            r_net = global_reward(recs) if args.mode in LOCAL_MODES and args.alpha < 1.0 else 0.0
            r_pf = pf_reward([x["reward"] for x in recs]) if args.reward == "pf" else 0.0

            for i in range(n):
                r = recs[i]["reward"]
                s_i, s2_i = L[i], L2[i]
                if args.mode in LOCAL_MODES and learning:
                    ri = i if args.mode == "independent" else 0
                    r_rep = args.rewardScale * (r_pf if args.reward == "pf" else args.alpha * r + (1.0 - args.alpha) * r_net)
                    replays[ri].add(s_i, acts[i], s2_i, r_rep, done[0])
                if args.check:
                    if args.mode in LOCAL_MODES and learning:
                        k = (replays[ri].ptr - 1) % replays[ri].max_size
                        check(np.allclose(replays[ri].state[k], s_i) and np.allclose(replays[ri].next_state[k], s2_i)
                              and np.isclose(replays[ri].reward[k, 0], r_rep) and np.isclose(replays[ri].action[k, 0], acts[i]),
                              "replay %d row mismatch at t=%d" % (i, time_step))
                    # cw.cc computes pow(2, 4 + a) with a float, so 4 + a is rounded to float32 before pow.
                    want_cw = static_cws[i] if args.mode == "static" else 16 if args.mode == "beb" else int(min(1024, max(
                        16, 2 ** float(np.float32(4) + np.float32(real[i])))))
                    check(recs[i]["cw_set"] == want_cw and recs[i]["cw_ap"] == want_cw,
                          "AP%d cw %s/%s != %d at t=%d" % (i + 1, recs[i]["cw_set"], recs[i]["cw_ap"], want_cw, time_step))
                    check(0.0 <= r <= 1.0, "AP%d reward %s out of [0,1]" % (i + 1, r))
                    # Test A: obs is this AP's own loss, recomputed from its own tx/rx counters
                    own_loss = (recs[i]["tx"] - recs[i]["rx"]) / recs[i]["tx"] if recs[i]["tx"] else 0.0
                    if args.obs == "hist":  # state recomputed from this AP's own row and own previous action only
                        w = S2[i, :args.obsWindow]
                        check(np.allclose(s2_i, [S2[i, 0], w.mean(), w.std(), acts[i]], atol=1e-5), "AP%d hist state mismatch at t=%d" % (i + 1, time_step))
                    check(np.isclose(s2_i[0], own_loss, atol=1e-5) and np.isclose(recs[i]["loss"], own_loss, atol=1e-5),
                          "AP%d obs %s / loss %s != own (tx-rx)/tx %s at t=%d" % (i + 1, s2_i[0], recs[i]["loss"], own_loss, time_step))
                    # Test D: reward = own goodput / (offered load * own STAs * step), clamped to [0,1]
                    want_r = min(1.0, max(0.0, recs[i]["rx"] * PAYLOAD_BITS / 1e6 / (LOADS[i] * counts[i] * args.stepTime)))
                    check(abs(r - want_r) < 1e-4, "AP%d reward %s != recomputed %s at t=%d" % (i + 1, r, want_r, time_step))
                    if args.reward == "pf" and i == 0:  # Test D2: pf reward recomputed from every AP's own rx counter
                        want_pf = pf_reward([min(1.0, max(0.0, q["rx"] * PAYLOAD_BITS / 1e6 / (LOADS[j] * counts[j] * args.stepTime))) for j, q in enumerate(recs)])
                        check(abs(r_pf - want_pf) < 1e-4 and 0.0 <= r_pf <= 1.0, "pf reward %s != recomputed %s at t=%d" % (r_pf, want_pf, time_step))
                reward_cols[i].append(r)
                ep_reward[i] += r
                pp = preprocess(S2[i].reshape(-1, 1, 1))[0][0]  # this AP's history only; logging only
                trace.writerow([episode, step, i + 1, float(s_i[0]), float(acts[i]), float(real[i]), r, float(s2_i[0]),
                                recs[i]["cw_set"], recs[i]["cw_ap"], recs[i]["loss"], recs[i]["rx"], recs[i]["tx"],
                                float(pp[0]), float(pp[1]), agent_loss(i, "actor_loss"), agent_loss(i, "critic_loss")])
                if args.mode == "independent" and learning and time_step >= args.start_timesteps:
                    agents[i].train(replays[i], args.batch_size)
            if args.mode == "shared" and learning and time_step >= args.start_timesteps:
                agents[0].train(replays[0], args.batch_size)  # one update per env step, same count as global
            if args.mode == "global":
                # one agent: network-wide loss as state, network goodput (normalized by all STAs) as reward
                tx_g = sum(r["tx"] for r in recs)
                rx_g = sum(r["rx"] for r in recs)
                s2_g = np.array([(tx_g - rx_g) / tx_g if tx_g else 0.0], dtype=np.float32)
                r_g = global_reward(recs) * args.rewardScale
                if learning:
                    replays[0].add(S_g, acts[0], s2_g, r_g, done[0])
                if args.check:
                    if learning:
                        k = (replays[0].ptr - 1) % replays[0].max_size
                        check(np.allclose(replays[0].state[k], S_g) and np.allclose(replays[0].next_state[k], s2_g)
                              and np.isclose(replays[0].reward[k, 0], r_g) and np.isclose(replays[0].action[k, 0], acts[0]),
                              "global replay row mismatch at t=%d" % time_step)
                    check(len({r["cw_set"] for r in recs}) == 1 and len({r["cw_ap"] for r in recs}) == 1,
                          "global mode: APs got different CWs at t=%d" % time_step)
                S_g = s2_g
                if learning and time_step >= args.start_timesteps:
                    agents[0].train(replays[0], args.batch_size)
            if args.mode == "central":
                # joint row: (s, a, r_g, r_local, s'); one critic update then N actor updates
                r_g = global_reward(recs)
                r_loc = [recs[i]["reward"] for i in range(n)]
                joint.add(S[:, 0], acts, S2[:, 0], r_g * args.rewardScale, r_loc, done[0])
                if args.check:
                    k = (joint.ptr - 1) % joint.max_size
                    check(np.allclose(joint.state[k], S[:, 0]) and np.allclose(joint.next_state[k], S2[:, 0])
                          and np.allclose(joint.action[k], acts) and np.isclose(joint.reward_g[k, 0], r_g * args.rewardScale)
                          and np.allclose(joint.reward_local[k], r_loc), "joint replay row mismatch at t=%d" % time_step)
                    check(0.0 <= r_g <= 1.0, "r_g %s out of [0,1]" % r_g)
                if time_step >= args.start_timesteps:
                    central.train(joint, args.batch_size)
                    if args.check:
                        vals = [scalar(central.critic_loss), scalar(central.q_mean)] + [scalar(x) for x in central.actor_losses]
                        check(all(np.isfinite(vals)), "non-finite central loss/Q at t=%d: %s" % (time_step, vals))
            trace_f.flush()

            obs_logged = [float(S_g[0])] * n if args.mode == "global" else [S2[i, 0] for i in range(n)]
            m = step_metrics(recs, obs_logged, [agent_loss(i, "actor_loss") for i in range(n)],
                             [agent_loss(i, "critic_loss") for i in range(n)], args.stepTime)
            m.update({"Episode": episode, "Step": step})
            logged.append(m)
            if done[0] or step == steps_per_ep:
                m.update({"AP%d/CumulativeReward" % (i + 1): ep_reward[i] for i in range(n)})
                m["Global/CumulativeReward"] = float(ep_reward.sum())
            wandb.log(m, step=time_step)

            if step % args.print_every == 0 or step == 1:
                print("ep%d step %4d | " % (episode, step) + " | ".join(
                    "AP%d cw=%4d r=%.3f loss=%.3f aL=%.3f cL=%.4f" % (
                        i + 1, recs[i]["cw_set"], recs[i]["reward"], recs[i]["loss"],
                        agent_loss(i, "actor_loss"), agent_loss(i, "critic_loss")) for i in range(n)), flush=True)
            S = S2
            L = L2
            prev_acts = acts.copy()
            time_step += 1
            if done[0]:
                break
        print("episode %d cumulative reward per AP: %s" % (episode, np.round(ep_reward, 3).tolist()))
        env.close()
    if args.saveActor:
        os.makedirs(args.saveActor, exist_ok=True)
        for i, a in enumerate(agents):
            a.save(os.path.join(args.saveActor, "agent%d" % i))
        print("saved %d agent(s) to %s" % (len(agents), args.saveActor))
finally:
    trace_f.close()
    wandb.finish()
    wlog = os.path.join(os.path.dirname(run.dir), "run-%s.wandb" % run.id)
    if os.path.exists(wlog):
        # wandb.finish() can return before the writer has flushed: wait for the size to settle (max ~15 s)
        prev, stable = -1, 0
        for _ in range(30):
            size = os.path.getsize(wlog)
            stable = stable + 1 if size == prev else 0
            if stable >= 3:
                break
            prev = size
            time.sleep(0.5)
        shutil.copy2(wlog, out_dir)

if args.check:
    if args.mode == "central":
        check(joint.size == time_step, "joint replay size %d != steps %d" % (joint.size, time_step))
        check(all(np.isfinite([scalar(central.critic_loss), scalar(central.q_mean)] + [scalar(x) for x in central.actor_losses])),
              "non-finite central loss/Q at end")
        print("central: critic_loss %.5f  Q_mean %.4f  actor_losses %s" % (
            scalar(central.critic_loss), scalar(central.q_mean), [round(scalar(x), 4) for x in central.actor_losses]))
    for i in range(n_agents):
        check(replays[i].size == (time_step * (n if args.mode == "shared" else 1) if learning else 0), "replay %d size %d != steps %d" % (i, replays[i].size, time_step))
        check(all(np.isfinite([scalar(agents[i].actor_loss), scalar(agents[i].critic_loss)])), "agent %d non-finite loss" % (i + 1))
    # v0.8.0: read the logged history back from the run's .wandb file
    from wandb.proto import wandb_internal_pb2 as pb
    from wandb.sdk.internal import datastore
    ds = datastore.DataStore()
    ds.open_for_scan(os.path.join(out_dir, "run-%s.wandb" % run.id))
    hist = []
    while True:
        data = ds.scan_data()
        if data is None:
            break
        rec = pb.Record()
        rec.ParseFromString(data)
        if rec.WhichOneof("record_type") == "history":
            hist.append({"/".join(it.nested_key) or it.key: json.loads(it.value_json)
                         for it in rec.history.item})
    check(len(hist) == time_step, "W&B history rows %d != steps %d" % (len(hist), time_step))
    keys = ["AP%d/%s" % (i + 1, k) for i in range(n) for k in
            ("CW", "Reward", "Throughput", "LossRatio", "Observation", "ActorLoss", "CriticLoss")]
    keys += ["Global/Throughput", "Global/Fairness", "Global/LossRatio", "Episode", "Step"]
    for h in hist:
        miss = [k for k in keys if k not in h]
        check(not miss, "W&B row missing keys %s" % miss)
        if miss:
            break
        thr = [h["AP%d/Throughput" % (i + 1)] for i in range(n)]
        check(np.isclose(h["Global/Throughput"], sum(thr)), "Global/Throughput != sum of APs")
        check(np.isclose(h["Global/Fairness"], jain(thr)), "Global/Fairness mismatch")
    last = hist[-1] if hist else {}
    check(all(k in last for k in ["Global/CumulativeReward"] + ["AP%d/CumulativeReward" % (i + 1) for i in range(n)]),
          "cumulative keys missing on last row")
    for h, m in zip(hist, logged):  # logged values == what the trainer computed this step
        if not all(np.isclose(h[k], m[k]) for k in keys):
            check(False, "W&B history differs from logged metrics")
            break
    # Test E: each episode restarts (Step 1 present per episode, cumulative reward = that episode only)
    for ep in range(args.episodes):
        rows = [h for h in hist if h["Episode"] == ep]
        check(bool(rows) and rows[0]["Step"] == 1, "episode %d does not start at Step 1" % ep)
        if rows and "Global/CumulativeReward" in rows[-1]:
            check(np.isclose(rows[-1]["Global/CumulativeReward"], sum(sum(h["AP%d/Reward" % (i + 1)] for i in range(n)) for h in rows)),
                  "episode %d cumulative reward != sum of that episode's rewards" % ep)
        else:
            check(False, "episode %d has no cumulative reward row" % ep)
    left = os.popen("pgrep -x linear-mesh || true").read().split()
    check(not left, "leftover ns-3 process(es): %s" % left)
    print("W&B check: %d rows, %d keys each" % (len(hist), len(keys)))
    for i in range(n):
        for j in range(i + 1, n):
            check(not np.allclose(reward_cols[i], reward_cols[j]), "reward columns identical for AP%d and AP%d" % (i + 1, j + 1))
    print("RESULT:", "FAIL (%d)" % len(fails) if fails else "PASS", "| steps:", time_step)
    sys.exit(1 if fails else 0)
