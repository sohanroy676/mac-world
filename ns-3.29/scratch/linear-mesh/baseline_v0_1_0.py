#!/usr/bin/env python
"""v0.1.0 baseline freeze & reproduction runner for OSCAR (single-AP).

Non-behavioral wrapper around the existing OSCAR training path:

  * default mode reproduces OSCAR_train.py exactly (nWifi=40, scenario
    "basic", simTime=15 s, envStepTime=0.01 s, history 300, 3 episodes);
  * --smoke runs a tiny pipeline check (nWifi=5, simTime=3 s,
    envStepTime=0.1 s, history 20, 1 episode, random actions only);
  * W&B logs offline by default so no credentials are needed; pass --online
    to log to the configured W&B entity/project instead;
  * run artifacts (per-step CW trace, W&B run files, headline metrics,
    provenance) are archived under results/baseline-v0.1.0-<label>-<stamp>/.

The training loop, hyperparameters, and ns3-gym call sequence are identical
to OSCAR_train.py. This script intentionally changes no RL or ns-3 behavior
(RL argparse defaults are pinned via parse_args([])).

Run from anywhere with the project venv (paths are resolved relative to this
file):
    ../../venv/bin/python baseline_v0_1_0.py [--smoke] [--online]
"""

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_cli():
    parser = argparse.ArgumentParser(description="v0.1.0 OSCAR baseline freeze runner")
    parser.add_argument("--smoke", action="store_true",
                        help="tiny pipeline check instead of the full baseline config")
    parser.add_argument("--online", action="store_true",
                        help="log to W&B online (requires login) instead of offline mode")
    return parser.parse_args()


CLI = parse_cli()

# W&B mode must be decided before wandb is imported.
if not CLI.online:
    os.environ.setdefault("WANDB_MODE", "offline")

os.chdir(SCRIPT_DIR)

import numpy as np  # noqa: E402
import torch  # noqa: E402
import tqdm  # noqa: E402
import wandb  # noqa: E402

from agents.our_ddpg.utils import ReplayBuffer  # noqa: E402
from agents.our_ddpg.preprocessor import Preprocessor  # noqa: E402
from agents.our_ddpg.Our_DDPG import DDPG  # noqa: E402
from agents.our_ddpg.loggers import Logger  # noqa: E402
from exceptions import AlreadyRunningException  # noqa: E402
from wrappers import EnvWrapper  # noqa: E402
from config import wandb_entity  # noqa: E402


def build_config():
    if CLI.smoke:
        return {
            "label": "smoke",
            "simTime": 3,
            "stepTime": 0.1,
            "history_length": 20,
            "EPISODE_COUNT": 1,
            "nWifi_values": [5],
        }
    return {
        "label": "full",
        "simTime": 15,
        "stepTime": 0.01,
        "history_length": 300,
        "EPISODE_COUNT": 3,
        "nWifi_values": [40],
    }


def build_rl_args():
    # Same arguments and defaults as OSCAR_train.py; pinned to defaults via
    # parse_args([]) so the frozen baseline cannot drift between runs.
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default="OurDDPG")
    parser.add_argument("--env", default="ContentionWindow")
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--start_timesteps", default=300, type=int)
    parser.add_argument("--eval_freq", default=10e10, type=int)
    parser.add_argument("--max_timesteps", default=1e6, type=int)
    parser.add_argument("--expl_noise", default=0.1)
    parser.add_argument("--batch_size", default=32, type=int)
    parser.add_argument("--discount", default=0.7)
    parser.add_argument("--tau", default=1e-3)
    parser.add_argument("--policy_noise", default=0.2)
    parser.add_argument("--noise_clip", default=0.5)
    parser.add_argument("--policy_freq", default=2, type=int)
    parser.add_argument("--save_model", action="store_true")
    parser.add_argument("--load_model", default="")
    return parser.parse_args([])


# --- artifact collection ---
def collect_artifacts(cfg, sim_args, rl_args, run, results_dir, log_file):
    """Archive run artifacts + provenance into results_dir. No behavior change."""
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=SCRIPT_DIR,
                                capture_output=True, text=True).stdout.strip()
    git_dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=SCRIPT_DIR,
                                    capture_output=True, text=True).stdout.strip())

    provenance = {
        "label": cfg["label"],
        "timestamp": datetime.now().isoformat(),
        "git_commit": git_commit,
        "git_dirty": git_dirty,
        "sim_args": sim_args,
        "rl_args": vars(rl_args),
        "wandb_mode": os.environ.get("WANDB_MODE", "online"),
        "wandb_run_id": run.id,
        "wandb_run_dir": run.dir,
    }

    # Per-step CW trace written by the ns-3 side (holds the last episode).
    if os.path.exists("CW_data.csv"):
        shutil.copy2("CW_data.csv", os.path.join(results_dir, "CW_data.csv"))
        log_file.write("archived CW_data.csv\n")

    # Final per-flow FlowMonitor dump the ns-3 side writes to the ns-3 root.
    # Usually absent: the sim blocks in the lock-step exchange after the last
    # Python step, so the dump at the end of main() never runs (known quirk).
    cw_csv = os.path.join("..", "..", "cw.csv")
    if os.path.exists(cw_csv):
        shutil.copy2(cw_csv, os.path.join(results_dir, "cw.csv"))
        provenance["cw_csv"] = "present"
        log_file.write("archived cw.csv\n")
    else:
        provenance["cw_csv"] = ("absent (known baseline quirk: final FlowMonitor "
                                "dump is skipped when the sim blocks after the "
                                "last python step)")

    # W&B run files (metadata, dependency freeze, console log).
    for fname in ("wandb-metadata.json", "requirements.txt", "output.log"):
        src = os.path.join(run.dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(results_dir, fname))

    # Full offline transaction log (contains config + complete metric
    # history; wandb 0.18 offline mode writes no wandb-summary.json file).
    wandb_log = os.path.join(run.dir, "run-%s.wandb" % run.id)
    if os.path.exists(wandb_log):
        shutil.copy2(wandb_log, os.path.join(results_dir, os.path.basename(wandb_log)))
        log_file.write("archived %s\n" % os.path.basename(wandb_log))

    # Headline metrics for quick comparison against future multi-AP runs,
    # read from the finished run object (offline mode writes no summary file).
    try:
        provenance["wandb_summary"] = dict(run.summary)
    except (TypeError, KeyError):
        provenance["wandb_summary"] = run.summary._as_dict()

    with open(os.path.join(results_dir, "summary.json"), "w") as f:
        json.dump(provenance, f, indent=2, default=str)
    log_file.write("wrote summary.json\n")


def run_baseline(cfg, args):
    scenario = "basic"
    agent_being_trained = "OurDDPG"

    simTime = cfg["simTime"]
    stepTime = cfg["stepTime"]
    history_length = cfg["history_length"]
    steps_per_ep = int(simTime / stepTime)
    EPISODE_COUNT = cfg["EPISODE_COUNT"]

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = os.path.join("results", f"baseline-v0.1.0-{cfg['label']}-{stamp}")
    os.makedirs(results_dir, exist_ok=True)
    log_file = open(os.path.join(results_dir, "runner.log"), "w")

    def tee(msg):
        print(msg)
        log_file.write(msg + "\n")
        log_file.flush()

    for nWifi in cfg["nWifi_values"]:
        sim_args = {
            "simTime": simTime,
            "envStepTime": stepTime,
            "historyLength": history_length,
            "agentType": "continuous",
            "scenario": scenario,
            "nWifi": nWifi,
        }
        tags = ["Rew: normalized speed",
                "OurDDPG",
                sim_args['scenario'],
                "Actor: UNDEFINED",
                "Critic: UNDEFINED",
                "Instances: 1",
                f"Station count: {sim_args['nWifi']}",
                *[f"{key}: {sim_args[key]}" for key in list(sim_args)[:3]]]

        wtags = [f"{EPISODE_COUNT}ep training", f"{simTime}s", f"{nWifi} nWifi",
                 f"envStep {stepTime}", agent_being_trained, "train",
                 "v0.1.0-baseline-freeze"]
        if cfg["label"] == "smoke":
            wtags.append("smoke")

        run = wandb.init(name=f"{nWifi} OurDDPG v0.1.0 baseline freeze ({cfg['label']})",
                         entity=wandb_entity, project="contention_window",
                         tags=wtags, reinit=True)

        logger = Logger(False, tags, None, experiment=None)
        logger.begin_logging(EPISODE_COUNT, steps_per_ep, None, None, stepTime)
        preprocess = Preprocessor(False).preprocess

        tee("Steps per episode: %d" % steps_per_ep)

        threads_no = 1
        env = EnvWrapper(threads_no, **sim_args)
        env.reset()

        file_name = f"{args.policy}_{args.env}_{args.seed}"
        tee("---------------------------------------")
        tee(f"Policy: {args.policy}, Env: {args.env}, Seed: {args.seed}")
        tee("---------------------------------------")

        if not os.path.exists("./results"):
            os.makedirs("./results")

        if args.save_model and not os.path.exists("./models"):
            os.makedirs("./models")

        torch.manual_seed(args.seed)
        np.random.seed(args.seed)

        state_dim = 1
        action_dim = 1
        max_action = 1  # DDPG outputs action from -1 to 1
        real_max_action = 6  # action is scaled to be in range from 0 to 6
        stateSize = state_dim

        kwargs = {
            "state_dim": state_dim,
            "action_dim": action_dim,
            "max_action": max_action,
            "discount": args.discount,
            "tau": args.tau,
        }

        # Initialize policy
        if args.policy == "OurDDPG":
            policy = DDPG(**kwargs)
        else:
            print("Policy not available")

        if args.load_model != "":
            policy_file = file_name if args.load_model == "default" else args.load_model
            policy.load(f"./models/{policy_file}")

        replay_buffer = ReplayBuffer(state_dim, action_dim)

        # Loop identical to OSCAR_train.py (minus its dead locals).
        state, done = env.reset(), False
        episode_reward = 0
        time_step = 0
        for episode in range(EPISODE_COUNT):
            episode_reward = 0

            try:
                env.run()
            except AlreadyRunningException:
                pass

            obs_dim = 1
            state = env.reset()
            state = state[0][:stateSize]
            state = np.reshape(state, stateSize)
            with tqdm.trange(1, steps_per_ep + 1) as t:
                for step in t:
                    # Select action randomly or according to policy
                    if time_step < args.start_timesteps:
                        action = np.array([[np.random.uniform(0, 6)]])
                        real_action = action
                    else:
                        action = (
                            policy.select_action(np.array(state))
                            + np.random.normal(0, max_action * args.expl_noise, size=action_dim)
                        ).clip(-max_action, max_action)
                        real_action = real_max_action * (action + 1) / 2  # scale it from -1,1 to 0,6
                        real_action = np.array([real_action])

                    # Perform action
                    next_state, reward, done, info = env.step(real_action)
                    not_processed_state = preprocess(np.reshape(next_state, (-1, len(env.envs), obs_dim)))

                    next_state = next_state[0][:stateSize]
                    next_state = np.reshape(next_state, stateSize)

                    # Store data in replay buffer
                    replay_buffer.add(state, action, next_state, reward, done)

                    state = next_state
                    episode_reward += reward
                    if step > 300:
                        loss = {"actor_loss": policy.actor_loss, "critic_loss": policy.critic_loss}
                        logger.log_round(state, reward, episode_reward, info, loss,
                                         np.mean(not_processed_state, axis=0)[0],
                                         episode * steps_per_ep + step)

                    t.set_postfix(mb_sent=f"{logger.sent_mb:.2f} Mb",
                                  curr_speed=f"{logger.current_speed:.2f} Mbps")

                    # Train agent after collecting sufficient data
                    if time_step >= args.start_timesteps:
                        policy.train(replay_buffer, args.batch_size)

                    time_step += 1

                    if done:
                        tee(f"Total T: {t+1} Episode Num: {episode} Episode T: {t} Reward: {episode_reward:.3f}")
                        break
            logger.log_episode(episode_reward, logger.sent_mb / (simTime), episode)
            env.close()
        run.finish()

        collect_artifacts(cfg, sim_args, args, run, results_dir, log_file)
        tee(f"Artifacts archived in {results_dir}")

    log_file.close()


if __name__ == "__main__":
    run_baseline(build_config(), build_rl_args())

