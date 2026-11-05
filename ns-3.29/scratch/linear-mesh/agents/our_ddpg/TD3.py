import copy
import torch
import torch.nn as nn
import torch.nn.functional as F

from agents.our_ddpg.Our_DDPG import DDPG, Critic, device

# Twin Delayed DDPG (TD3), same networks, lrs and interface as Our_DDPG.DDPG.
# Paper: https://arxiv.org/abs/1802.09477


class TwinCritic(nn.Module):
	"""Two independent Q heads; forward() returns Q1 so DDPG-style callers keep working."""
	def __init__(self, state_dim, action_dim):
		super(TwinCritic, self).__init__()
		self.q1 = Critic(state_dim, action_dim)
		self.q2 = Critic(state_dim, action_dim)

	def forward(self, state, action):
		return self.q1(state, action)

	def both(self, state, action):
		return self.q1(state, action), self.q2(state, action)


class TD3(DDPG):
	def __init__(self, state_dim, action_dim, max_action, discount=0.7, tau=1e-3, policy_noise=0.2, noise_clip=0.5, policy_freq=2):
		super(TD3, self).__init__(state_dim, action_dim, max_action, discount, tau)
		self.critic = TwinCritic(state_dim, action_dim).to(device)
		self.critic_target = copy.deepcopy(self.critic)
		self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=4e-3)
		self.max_action = max_action
		self.policy_noise = policy_noise * max_action
		self.noise_clip = noise_clip * max_action
		self.policy_freq = policy_freq
		self.total_it = 0

	def train(self, replay_buffer, batch_size=32):
		self.total_it += 1
		state, action, next_state, reward, not_done = replay_buffer.sample(batch_size)

		with torch.no_grad():
			# Target policy smoothing
			noise = (torch.randn_like(action) * self.policy_noise).clamp(-self.noise_clip, self.noise_clip)
			next_action = (self.actor_target(next_state) + noise).clamp(-self.max_action, self.max_action)
			t1, t2 = self.critic_target.both(next_state, next_action)
			target_Q = reward + not_done * self.discount * torch.min(t1, t2)

		c1, c2 = self.critic.both(state, action)
		critic_loss = F.mse_loss(c1, target_Q) + F.mse_loss(c2, target_Q)
		self.critic_loss = critic_loss
		self.critic_optimizer.zero_grad()
		critic_loss.backward()
		self.critic_optimizer.step()

		# Delayed actor and target updates
		if self.total_it % self.policy_freq == 0:
			actor_loss = -self.critic(state, self.actor(state)).mean()
			self.actor_loss = actor_loss
			self.actor_optimizer.zero_grad()
			actor_loss.backward()
			self.actor_optimizer.step()

			for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
				target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
			for param, target_param in zip(self.actor.parameters(), self.actor_target.parameters()):
				target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
