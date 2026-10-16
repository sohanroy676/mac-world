"""v1.8.0: CTDE central critic. N local actors mu_i(s_i), ONE shared critic Q(s_joint, a_joint) on the global reward.
Spec: docs/central-critic-v1.7.0.md. Actor/Critic classes are reused unchanged from Our_DDPG.py.
"""
import copy

import torch
import torch.nn.functional as F

from agents.our_ddpg.Our_DDPG import Actor, Critic, device


class CentralDDPG(object):
	def __init__(self, n, max_action, discount=0.7, tau=1e-3):
		self.n = n
		self.actors = [Actor(1, 1, max_action).to(device) for _ in range(n)]
		self.actor_targets = [copy.deepcopy(a) for a in self.actors]
		self.actor_optimizers = [torch.optim.Adam(a.parameters(), lr=4e-4) for a in self.actors]

		self.critic = Critic(n, n).to(device)
		self.critic_target = copy.deepcopy(self.critic)
		self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=4e-3)
		self.critic_loss = 0
		self.actor_losses = [0] * n
		self.q_mean = 0
		self.discount = discount
		self.tau = tau


	def select_action(self, i, s_i):
		"""Execution: actor i sees only AP i's own state."""
		s_i = torch.FloatTensor(s_i.reshape(1, -1)).to(device)
		return self.actors[i](s_i).cpu().data.numpy().flatten()


	def train(self, replay_buffer, batch_size=32):
		state, action, next_state, reward_g, not_done = replay_buffer.sample(batch_size)

		# Critic: y = r_g + gamma * Q'(s', [mu'_1(s'_1) .. mu'_N(s'_N)])
		with torch.no_grad():
			next_action = torch.cat([self.actor_targets[i](next_state[:, i:i + 1]) for i in range(self.n)], 1)
			target_Q = reward_g + not_done * self.discount * self.critic_target(next_state, next_action)
		current_Q = self.critic(state, action)
		critic_loss = F.mse_loss(current_Q, target_Q)
		self.critic_loss = critic_loss
		self.q_mean = current_Q.mean().detach()
		self.critic_optimizer.zero_grad()
		critic_loss.backward()
		self.critic_optimizer.step()

		# Actors (MADDPG): slot i replaced by mu_i(s_i), other slots stay as replayed
		for i in range(self.n):
			parts = [action[:, j:j + 1] for j in range(self.n)]
			parts[i] = self.actors[i](state[:, i:i + 1])
			actor_loss = -self.critic(state, torch.cat(parts, 1)).mean()
			self.actor_losses[i] = actor_loss
			self.actor_optimizers[i].zero_grad()
			self.critic_optimizer.zero_grad()
			actor_loss.backward()
			self.actor_optimizers[i].step()  # critic grads from this backward are never applied

		# Soft updates of the frozen targets
		for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
			target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
		for actor, target in zip(self.actors, self.actor_targets):
			for param, target_param in zip(actor.parameters(), target.parameters()):
				target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
