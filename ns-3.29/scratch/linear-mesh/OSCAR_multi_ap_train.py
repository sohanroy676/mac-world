"""v0.7.0: one independent DDPG agent (actor+critic+replay) per AP in one joint ns-3 simulation.

Each agent sees only its own AP's newest loss and its own reward (from parse_ap_info, not the
scalar gym reward). Local critics only. Differences from OSCAR_train.py (deliberate): warm-up
actions are sampled in [-1,1] and stored as such (the baseline stores U(0,6) in the replay).
Run from this directory: ../../venv/bin/python OSCAR_multi_ap_train.py --apStaCounts 2,3 --check
"""
import argparse
import csv
import os
import sys
import time

import numpy as np
import torch

from agents.our_ddpg.Our_DDPG import DDPG
from agents.our_ddpg.preprocessor import Preprocessor
from agents.our_ddpg.utils import ReplayBuffer
from exceptions import AlreadyRunningException
from multi_ap import parse_ap_info, reshape_obs
from wrappers import EnvWrapper

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
parser.add_argument("--check", action="store_true", help="assert per-AP isolation every step")
args = parser.parse_args()

counts = [int(c) for c in args.apStaCounts.split(",")]
n = len(counts)
assert n > 1, "multi-AP trainer needs >1 AP (use OSCAR_train.py for one)"
steps_per_ep = int(args.simTime / args.stepTime)
state_dim = action_dim = 1
max_action = 1
real_max_action = 6

torch.manual_seed(args.seed)
np.random.seed(args.seed)

sim_args = {"simTime": args.simTime, "envStepTime": args.stepTime, "historyLength": args.historyLength,
            "agentType": "continuous", "scenario": "basic", "apStaCounts": args.apStaCounts}

out_dir = "results/v0.7.0-%s" % time.strftime("%Y%m%d-%H%M%S")
os.makedirs(out_dir)
trace_f = open(os.path.join(out_dir, "trace.csv"), "w", newline="")
trace = csv.writer(trace_f)
trace.writerow(["episode", "step", "ap", "state", "action", "real_action", "reward", "next_state", "cw_set",
                "cw_ap", "loss", "rx", "tx", "pp_mean", "pp_std", "actor_loss", "critic_loss"])

agents = [DDPG(state_dim, action_dim, max_action, args.discount, args.tau) for _ in range(n)]
replays = [ReplayBuffer(state_dim, action_dim) for _ in range(n)]
preprocess = Preprocessor(False).preprocess


def scalar(x):
    return float(x.detach().cpu().item()) if hasattr(x, "detach") else float(x)


fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("CHECK FAIL:", msg)


if args.check:
    param_ids = [{p.data_ptr() for net in (a.actor, a.actor_target, a.critic, a.critic_target)
                  for p in net.parameters()} for a in agents]
    for i in range(n):
        for j in range(i + 1, n):
            check(not (param_ids[i] & param_ids[j]), "agents %d,%d share parameters" % (i, j))
    check(len({id(r) for r in replays}) == n, "replay buffers are not distinct")

env = EnvWrapper(1, **sim_args)
print("APs:", counts, "steps/ep:", steps_per_ep, "out:", out_dir)
time_step = 0
reward_cols = [[] for _ in range(n)]
try:
    for episode in range(args.episodes):
        try:
            env.run()
        except AlreadyRunningException:
            pass
        S = reshape_obs(env.reset()[0], n)
        ep_reward = np.zeros(n)
        for step in range(1, steps_per_ep + 1):
            acts = np.zeros(n, dtype=np.float32)
            for i in range(n):
                if time_step < args.start_timesteps:
                    acts[i] = np.random.uniform(-max_action, max_action)
                else:
                    a = agents[i].select_action(S[i, :state_dim]) + np.random.normal(0, max_action * args.expl_noise)
                    acts[i] = np.clip(a, -max_action, max_action)[0]
            real = (real_max_action * (acts + 1) / 2).astype(np.float32)

            obs, _, done, info = env.step(np.array([real], dtype=np.float32))
            S2 = reshape_obs(obs[0], n)
            recs = parse_ap_info(info[0], n)

            for i in range(n):
                r = recs[i]["reward"]
                s_i, s2_i = S[i, :state_dim], S2[i, :state_dim]
                replays[i].add(s_i, acts[i], s2_i, r, done[0])
                if args.check:
                    k = (replays[i].ptr - 1) % replays[i].max_size
                    want_cw = int(min(1024, max(16, 2 ** (float(real[i]) + 4))))
                    check(np.allclose(replays[i].state[k], s_i) and np.allclose(replays[i].next_state[k], s2_i)
                          and np.isclose(replays[i].reward[k, 0], r) and np.isclose(replays[i].action[k, 0], acts[i]),
                          "replay %d row mismatch at t=%d" % (i, time_step))
                    check(recs[i]["cw_set"] == want_cw and recs[i]["cw_ap"] == want_cw,
                          "AP%d cw %s/%s != %d at t=%d" % (i + 1, recs[i]["cw_set"], recs[i]["cw_ap"], want_cw, time_step))
                    check(0.0 <= r <= 1.0, "AP%d reward %s out of [0,1]" % (i + 1, r))
                reward_cols[i].append(r)
                ep_reward[i] += r
                pp = preprocess(S2[i].reshape(-1, 1, 1))[0][0]  # this AP's history only; logging only
                trace.writerow([episode, step, i + 1, float(s_i[0]), float(acts[i]), float(real[i]), r, float(s2_i[0]),
                                recs[i]["cw_set"], recs[i]["cw_ap"], recs[i]["loss"], recs[i]["rx"], recs[i]["tx"],
                                float(pp[0]), float(pp[1]), scalar(agents[i].actor_loss), scalar(agents[i].critic_loss)])
                if time_step >= args.start_timesteps:
                    agents[i].train(replays[i], args.batch_size)
            trace_f.flush()

            if step % args.print_every == 0 or step == 1:
                print("ep%d step %4d | " % (episode, step) + " | ".join(
                    "AP%d cw=%4d r=%.3f loss=%.3f aL=%.3f cL=%.4f" % (
                        i + 1, recs[i]["cw_set"], recs[i]["reward"], recs[i]["loss"],
                        scalar(agents[i].actor_loss), scalar(agents[i].critic_loss)) for i in range(n)), flush=True)
            S = S2
            time_step += 1
            if done[0]:
                break
        print("episode %d cumulative reward per AP: %s" % (episode, np.round(ep_reward, 3).tolist()))
        env.close()
finally:
    trace_f.close()

if args.check:
    for i in range(n):
        check(replays[i].size == time_step, "replay %d size %d != steps %d" % (i, replays[i].size, time_step))
        check(all(np.isfinite([scalar(agents[i].actor_loss), scalar(agents[i].critic_loss)])), "AP%d non-finite loss" % (i + 1))
    if n == 2:
        check(not np.allclose(reward_cols[0], reward_cols[1]), "reward columns identical across APs")
    print("RESULT:", "FAIL (%d)" % len(fails) if fails else "PASS", "| steps:", time_step)
    sys.exit(1 if fails else 0)
