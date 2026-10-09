"""v0.7.0/v0.8.0/v0.9.0: one independent DDPG agent (actor+critic+replay) per AP in one joint ns-3 simulation.

Each agent sees only its own AP's newest loss and its own reward (from parse_ap_info, not the
scalar gym reward). Local critics only. Differences from OSCAR_train.py (deliberate): warm-up
actions are sampled in [-1,1] and stored as such (the baseline stores U(0,6) in the replay).
v0.8.0: per-AP + global W&B metrics (design section 7 names; offline unless --online).
v0.9.0: --check also recomputes obs (Test A) and reward (Test D) per AP and checks episode resets (Test E).
v1.1.0: --mode independent (default, above) | global (ONE agent, one CW broadcast to every AP; state = network
loss (sum tx - sum rx)/sum tx, reward = network goodput / (offered load x all STAs x step)) | beb (ns-3 --dryRun
through the same stepping loop, no agent: standard 802.11 measured in the same per-step window).
Run from this directory: ../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --check
"""
import argparse
import csv
import json
import os
import shutil
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
parser.add_argument("--print_every", type=int, default=10)
parser.add_argument("--online", action="store_true", help="sync W&B online (default: offline)")
parser.add_argument("--wandb_project", default="contention_window")
parser.add_argument("--mode", choices=["independent", "global", "beb"], default="independent")
parser.add_argument("--check", action="store_true", help="assert per-AP isolation every step")
args = parser.parse_args()

# W&B mode must be decided before wandb is imported.
if not args.online:
    os.environ.setdefault("WANDB_MODE", "offline")

import numpy as np  # noqa: E402
import torch  # noqa: E402
import wandb  # noqa: E402

from agents.our_ddpg.Our_DDPG import DDPG  # noqa: E402
from agents.our_ddpg.preprocessor import Preprocessor  # noqa: E402
from agents.our_ddpg.utils import ReplayBuffer  # noqa: E402
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
OFFERED_MBPS = 150.0  # per-STA offered load, cw.cc offeredLoad

torch.manual_seed(args.seed)
np.random.seed(args.seed)

sim_args = {"simTime": args.simTime, "envStepTime": args.stepTime, "historyLength": args.historyLength,
            "agentType": "continuous", "scenario": "basic", "apStaCounts": args.apStaCounts,
            "seed": args.seed + 1}  # ns-3 rejects seed 0, so ns-3 seed = python seed + 1
if args.mode == "beb":
    sim_args["dryRun"] = "true"  # cw.cc skips setApCw; every AP keeps BEB CW 16..1024
n_agents = {"independent": n, "global": 1, "beb": 0}[args.mode]

out_dir = "results/multi-ap-%s" % time.strftime("%Y%m%d-%H%M%S")
os.makedirs(out_dir)
with open(os.path.join(out_dir, "config.json"), "w") as f:
    json.dump(dict(vars(args), ns3_seed=args.seed + 1, counts=counts), f)
trace_f = open(os.path.join(out_dir, "trace.csv"), "w", newline="")
trace = csv.writer(trace_f)
trace.writerow(["episode", "step", "ap", "state", "action", "real_action", "reward", "next_state", "cw_set",
                "cw_ap", "loss", "rx", "tx", "pp_mean", "pp_std", "actor_loss", "critic_loss"])

suffix = "" if args.mode == "independent" else " " + args.mode
run = wandb.init(name="%s multi-AP OurDDPG v1.0.0%s" % (args.apStaCounts, suffix), entity=wandb_entity,
                 project=args.wandb_project, tags=["multi-ap", "v0.9.0", "mode-" + args.mode], reinit=True,
                 config=dict(vars(args), AP_Count=n, Stations_Per_AP=counts))

agents = [DDPG(state_dim, action_dim, max_action, args.discount, args.tau) for _ in range(n_agents)]
replays = [ReplayBuffer(state_dim, action_dim) for _ in range(n_agents)]
preprocess = Preprocessor(False).preprocess


def scalar(x):
    return float(x.detach().cpu().item()) if hasattr(x, "detach") else float(x)


def agent_loss(i, name):
    """Loss of the agent that acts for AP i (independent: own; global: the shared one; beb: none -> 0)."""
    if args.mode == "beb":
        return 0.0
    return scalar(getattr(agents[i if args.mode == "independent" else 0], name))


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

env = EnvWrapper(1, **sim_args)
print("APs:", counts, "steps/ep:", steps_per_ep, "out:", out_dir)
time_step = 0
reward_cols = [[] for _ in range(n)]
logged = []
try:
    for episode in range(args.episodes):
        try:
            env.run()
        except AlreadyRunningException:
            pass
        S = reshape_obs(env.reset()[0], n)
        S_g = np.zeros(state_dim, dtype=np.float32)  # global mode: network loss; 0 before the first step
        ep_reward = np.zeros(n)
        for step in range(1, steps_per_ep + 1):
            acts = np.zeros(n, dtype=np.float32)
            if args.mode == "independent":
                for i in range(n):
                    if time_step < args.start_timesteps:
                        acts[i] = np.random.uniform(-max_action, max_action)
                    else:
                        a = agents[i].select_action(S[i, :state_dim]) + np.random.normal(0, max_action * args.expl_noise)
                        acts[i] = np.clip(a, -max_action, max_action)[0]
            elif args.mode == "global":
                if time_step < args.start_timesteps:
                    acts[:] = np.random.uniform(-max_action, max_action)
                else:
                    a = agents[0].select_action(S_g) + np.random.normal(0, max_action * args.expl_noise)
                    acts[:] = np.clip(a, -max_action, max_action)[0]
            real = (real_max_action * (acts + 1) / 2).astype(np.float32)  # beb: ignored by cw.cc (dryRun)

            obs, _, done, info = env.step(np.array([real], dtype=np.float32))
            S2 = reshape_obs(obs[0], n)
            recs = parse_ap_info(info[0], n)

            for i in range(n):
                r = recs[i]["reward"]
                s_i, s2_i = S[i, :state_dim], S2[i, :state_dim]
                if args.mode == "independent":
                    replays[i].add(s_i, acts[i], s2_i, r, done[0])
                if args.check:
                    if args.mode == "independent":
                        k = (replays[i].ptr - 1) % replays[i].max_size
                        check(np.allclose(replays[i].state[k], s_i) and np.allclose(replays[i].next_state[k], s2_i)
                              and np.isclose(replays[i].reward[k, 0], r) and np.isclose(replays[i].action[k, 0], acts[i]),
                              "replay %d row mismatch at t=%d" % (i, time_step))
                    want_cw = 16 if args.mode == "beb" else int(min(1024, max(16, 2 ** (float(real[i]) + 4))))
                    check(recs[i]["cw_set"] == want_cw and recs[i]["cw_ap"] == want_cw,
                          "AP%d cw %s/%s != %d at t=%d" % (i + 1, recs[i]["cw_set"], recs[i]["cw_ap"], want_cw, time_step))
                    check(0.0 <= r <= 1.0, "AP%d reward %s out of [0,1]" % (i + 1, r))
                    # Test A: obs is this AP's own loss, recomputed from its own tx/rx counters
                    own_loss = (recs[i]["tx"] - recs[i]["rx"]) / recs[i]["tx"] if recs[i]["tx"] else 0.0
                    check(np.isclose(s2_i[0], own_loss, atol=1e-5) and np.isclose(recs[i]["loss"], own_loss, atol=1e-5),
                          "AP%d obs %s / loss %s != own (tx-rx)/tx %s at t=%d" % (i + 1, s2_i[0], recs[i]["loss"], own_loss, time_step))
                    # Test D: reward = own goodput / (offered load * own STAs * step), clamped to [0,1]
                    want_r = min(1.0, max(0.0, recs[i]["rx"] * PAYLOAD_BITS / 1e6 / (OFFERED_MBPS * counts[i] * args.stepTime)))
                    check(abs(r - want_r) < 1e-4, "AP%d reward %s != recomputed %s at t=%d" % (i + 1, r, want_r, time_step))
                reward_cols[i].append(r)
                ep_reward[i] += r
                pp = preprocess(S2[i].reshape(-1, 1, 1))[0][0]  # this AP's history only; logging only
                trace.writerow([episode, step, i + 1, float(s_i[0]), float(acts[i]), float(real[i]), r, float(s2_i[0]),
                                recs[i]["cw_set"], recs[i]["cw_ap"], recs[i]["loss"], recs[i]["rx"], recs[i]["tx"],
                                float(pp[0]), float(pp[1]), agent_loss(i, "actor_loss"), agent_loss(i, "critic_loss")])
                if args.mode == "independent" and time_step >= args.start_timesteps:
                    agents[i].train(replays[i], args.batch_size)
            if args.mode == "global":
                # one agent: network-wide loss as state, network goodput (normalized by all STAs) as reward
                tx_g = sum(r["tx"] for r in recs)
                rx_g = sum(r["rx"] for r in recs)
                s2_g = np.array([(tx_g - rx_g) / tx_g if tx_g else 0.0], dtype=np.float32)
                r_g = min(1.0, max(0.0, rx_g * PAYLOAD_BITS / 1e6 / (OFFERED_MBPS * sum(counts) * args.stepTime)))
                replays[0].add(S_g, acts[0], s2_g, r_g, done[0])
                if args.check:
                    k = (replays[0].ptr - 1) % replays[0].max_size
                    check(np.allclose(replays[0].state[k], S_g) and np.allclose(replays[0].next_state[k], s2_g)
                          and np.isclose(replays[0].reward[k, 0], r_g) and np.isclose(replays[0].action[k, 0], acts[0]),
                          "global replay row mismatch at t=%d" % time_step)
                    check(len({r["cw_set"] for r in recs}) == 1 and len({r["cw_ap"] for r in recs}) == 1,
                          "global mode: APs got different CWs at t=%d" % time_step)
                S_g = s2_g
                if time_step >= args.start_timesteps:
                    agents[0].train(replays[0], args.batch_size)
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
            time_step += 1
            if done[0]:
                break
        print("episode %d cumulative reward per AP: %s" % (episode, np.round(ep_reward, 3).tolist()))
        env.close()
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
    for i in range(n_agents):
        check(replays[i].size == time_step, "replay %d size %d != steps %d" % (i, replays[i].size, time_step))
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
    if n == 2:
        check(not np.allclose(reward_cols[0], reward_cols[1]), "reward columns identical across APs")
    print("RESULT:", "FAIL (%d)" % len(fails) if fails else "PASS", "| steps:", time_step)
    sys.exit(1 if fails else 0)
