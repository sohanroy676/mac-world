import numpy as np
from wrappers import EnvWrapper

sim_args = {
    "simTime": 3,
    "envStepTime": 0.1,
    "historyLength": 20,
    "agentType": "continuous",
    "scenario": "basic",
    "nWifi": 5,
}

print("Creating OSCAR environment...")

env = EnvWrapper(1, **sim_args)

print("Environment created.")
print("Observation space:", env.observation_space)
print("Action space:", env.action_space)

obs = env.reset()

print("Initial observation:", obs)

action = np.array([[0.0]], dtype = np.float32)

for step in range(5):
    obs, reward, done, info = env.step(action)

    print(
        "Step:", step,
        "Observation:", obs,
        "Reward:", reward,
        "Done:", done,
        "Info:", info
    )

    if done[0]:
        break

env.close()

print("OSCAR connection test completed successfully.")
