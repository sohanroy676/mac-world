"""v3.8.0 (M2b) drlCW: Yan, Du, Zhang, Dong, "Deep Reinforcement Learning based Contention Window Optimization for IEEE 802.11bn"
(the mentor's PDF; text read in full 2026-11-11). Built from that text only; every choice the text does not fix is labelled DECISION.

From the paper (fact):
  * Per-AP agent, action b in {0..6}, CW = 2^(4+b). Decision every 0.5 s (Table I: interact time 0.5 s).
  * Observation o_t = [cw (last action), per, thp, delay (mean of successful packets), cdf (delay CDF 95 %)] over the last interval.
  * State = own last T = 10 observations, the same for every one-hop neighbour (heard directly), and for every hidden node
    (two hops, learned through a neighbour's beacon) the observations t-T..t-1, i.e. one interval late.
  * Reward (global, training only): r = alpha - beta * d_tail if sum thp >= m * sum thp_CSMA and n * sum per <= sum per_CSMA, else -1,
    with d_tail = mean over APs of cdf_i, alpha 1.5, beta 10, m 0.98, n 0.95; thp_CSMA / per_CSMA come from a pre-simulated BEB run.
  * DDQN (policy net picks the argmax, target net evaluates), soft target update tau 0.004, gamma 0.9, lr 5e-4, batch 32, experience
    memory 500, epsilon 1 -> 0.01 with decay 0.99, 300 s training. Network: LSTM(64) -> FC(64) -> FC(7).
DECISIONS (not in the text): Adam optimiser; ReLU after the first FC; one independent network per AP; epsilon decays per decision;
  thp feature = interval Mbps / (offered Mbps per STA * STAs of that AP) (the trainer's reward scale), delay and cdf features =
  min(1.5, ln(1 + ms) / ln(1001)) (the paper gives no scaling); per = (PHY transmissions - receptions) / PHY transmissions (the repo's
  loss definition), clipped to [0, 1] (rx can exceed tx in a window); d_tail in seconds, and the reward is clipped to [-1, alpha] (the paper says it is normalised to [-1, 1]);
  --drlDelayRef (DECISION, pending the user's choice): in our saturated cells the queue, and so the p95 delay, grows without bound
  (smoke run: 0.86 s in the first 0.5 s window, +0.4 s per window), so beta = 10 gives a constant reward of -1. With a reference,
  d_tail is divided by the BEB d_tail at the same decision index and multiplied by 0.1 s (the paper's CSMA value), so BEB parity gives r = 0.5;
  CSMA references = BEB means on the selection seeds, passed with --drlRefThp / --drlRefPer; delay values are the last completed
  cw.cc --delayWindow 0.5 window (app send to sink receive, matched by packet uid), which includes queueing.
Deviation by design: neighbour observations come from the simulator's per-AP records (the paper's beacon exchange). This breaks ADR-0002
  isolation on purpose; the hearing graph is --apHidden, as for KW.
No ns-3 dependency; torch only.
"""
import math
from collections import deque

import numpy as np
import torch
import torch.nn as nn

PAYLOAD_BITS = (1500 - 20 - 8 - 8) * 8
OBS_DIM = 5
ALPHA, BETA, M_THP, N_PER = 1.5, 10.0, 0.98, 0.95


def delay_feature(ms):
    return min(1.5, math.log1p(max(0.0, ms)) / math.log(1001.0))


class QNet(nn.Module):
    def __init__(self, in_dim, n_actions=7):
        super().__init__()
        self.lstm = nn.LSTM(in_dim, 64, batch_first=True)
        self.fc1 = nn.Linear(64, 64)
        self.fc2 = nn.Linear(64, n_actions)

    def forward(self, x):  # x: (B, T, D)
        out, _ = self.lstm(x)
        return self.fc2(torch.relu(self.fc1(out[:, -1])))


class DrlCW:
    def __init__(self, counts, norm_loads, hidden_pairs, ref_thp, ref_per, step_time=0.01, interval=0.5, T=10, learning=True, seed=0,
                 lr=5e-4, gamma=0.9, tau=0.004, batch=32, memory=500, eps_decay=0.99, eps_min=0.01, delay_ref=None):
        self.n = len(counts)
        self.counts = np.asarray(counts, dtype=np.float64)
        self.norm = np.asarray(norm_loads, dtype=np.float64)
        self.step_time, self.T, self.learning = step_time, T, learning
        self.delay_ref = delay_ref  # BEB mean-over-APs p95 delay (s) per decision, or None for the paper's raw d_tail
        self.steps = max(1, int(round(interval / step_time)))
        self.interval = self.steps * step_time
        hid = {frozenset((a - 1, b - 1)) for a, b in hidden_pairs}
        self.audible = [[j == i or frozenset((i, j)) not in hid for j in range(self.n)] for i in range(self.n)]
        self.ref_thp, self.ref_per = float(np.sum(ref_thp)), float(np.sum(ref_per))
        self.in_dim = OBS_DIM * self.n
        self.gamma, self.tau, self.batch, self.eps_decay, self.eps_min = gamma, tau, batch, eps_decay, eps_min
        self.rng = np.random.RandomState(seed)
        torch.manual_seed(seed)
        self.q = [QNet(self.in_dim) for _ in range(self.n)]
        self.q_t = [QNet(self.in_dim) for _ in range(self.n)]
        for a, b in zip(self.q, self.q_t):
            b.load_state_dict(a.state_dict())
        self.opt = [torch.optim.Adam(a.parameters(), lr=lr) for a in self.q]
        self.mem = [deque(maxlen=memory) for _ in range(self.n)]
        self.eps = 1.0 if learning else 0.0
        self.b = np.zeros(self.n, dtype=np.int64)  # CW starts at BEB 16 = action 0
        self.hist = [deque([np.zeros(OBS_DIM, dtype=np.float32)] * (T + 1), maxlen=T + 1) for _ in range(self.n)]  # newest last
        self.k = 0
        self.rx, self.tx = np.zeros(self.n), np.zeros(self.n)
        self.prev_state, self.prev_act = None, None
        self.decisions, self.last_reward, self.last_loss = 0, 0.0, 0.0

    def _state(self, i):
        rows = []
        for t in range(1, self.T + 1):  # t-th newest of the T used by the paper: index -t .. newest
            idx = -(self.T - t + 1)
            feat = []
            for j in range(self.n):
                h = self.hist[j]
                feat.append(h[idx] if self.audible[i][j] else h[idx - 1])  # hidden nodes: one interval late
            own = feat.pop(i)
            rows.append(np.concatenate([own] + feat))
        return np.stack(rows).astype(np.float32)

    def observe(self, recs):
        self.rx += np.array([r["rx"] for r in recs], dtype=np.float64)
        self.tx += np.array([r["tx"] for r in recs], dtype=np.float64)
        self.k += 1
        if self.k < self.steps:
            return
        thp = self.rx * PAYLOAD_BITS / (self.interval * 1e6)
        per = np.clip(np.where(self.tx > 0, (self.tx - self.rx) / np.maximum(self.tx, 1.0), 0.0), 0.0, 1.0)  # rx can exceed tx in a window (queued ACKs), clip like the env's obs
        dp95 = np.array([r["dp95"] for r in recs])
        for i in range(self.n):
            o = np.array([self.b[i] / 6.0, per[i], min(1.5, thp[i] / (self.norm[i] * self.counts[i])),
                          delay_feature(recs[i]["dmean"]), delay_feature(dp95[i])], dtype=np.float32)
            self.hist[i].append(o)
        self.k, self.rx, self.tx = 0, np.zeros(self.n), np.zeros(self.n)
        self.decisions += 1
        state = [self._state(i) for i in range(self.n)]
        if self.learning and self.prev_state is not None:
            ok = thp.sum() >= M_THP * self.ref_thp and N_PER * per.sum() <= self.ref_per
            d_tail = float(np.mean(dp95)) / 1000.0
            if self.delay_ref:  # BEB = 0.1 s (paper Table III CSMA), same elapsed time
                d_tail = d_tail / max(1e-6, self.delay_ref[min(self.decisions - 1, len(self.delay_ref) - 1)]) * 0.1
            r = ALPHA - BETA * d_tail if ok else -1.0
            r = float(min(ALPHA, max(-1.0, r)))
            self.last_reward = r
            for i in range(self.n):
                self.mem[i].append((self.prev_state[i], int(self.prev_act[i]), r, state[i]))
            self._update()
            self.eps = max(self.eps_min, self.eps * self.eps_decay)
        for i in range(self.n):
            if self.learning and self.rng.rand() < self.eps:
                self.b[i] = self.rng.randint(7)
            else:
                with torch.no_grad():
                    self.b[i] = int(self.q[i](torch.from_numpy(state[i])[None]).argmax(1).item())
        self.prev_state, self.prev_act = state, self.b.copy()

    def _update(self):
        for i in range(self.n):
            if len(self.mem[i]) < self.batch:
                continue
            idx = self.rng.choice(len(self.mem[i]), self.batch, replace=False)
            s, a, r, s2 = zip(*[self.mem[i][j] for j in idx])
            s, s2 = torch.from_numpy(np.stack(s)), torch.from_numpy(np.stack(s2))
            a, r = torch.tensor(a), torch.tensor(r, dtype=torch.float32)
            with torch.no_grad():  # double DQN: policy net picks, target net evaluates
                a2 = self.q[i](s2).argmax(1, keepdim=True)
                y = r + self.gamma * self.q_t[i](s2).gather(1, a2).squeeze(1)
            loss = nn.functional.mse_loss(self.q[i](s).gather(1, a[:, None]).squeeze(1), y)
            self.opt[i].zero_grad()
            loss.backward()
            self.opt[i].step()
            self.last_loss = float(loss.item())
            for p, pt in zip(self.q[i].parameters(), self.q_t[i].parameters()):
                pt.data.copy_(self.tau * p.data + (1.0 - self.tau) * pt.data)

    def cw_exponents(self):
        return self.b.astype(np.float32)

    def save(self, d):
        import os
        os.makedirs(d, exist_ok=True)
        for i in range(self.n):
            torch.save(self.q[i].state_dict(), os.path.join(d, "drlcw_ap%d.pt" % i))

    def load(self, d):
        import os
        for i in range(self.n):
            self.q[i].load_state_dict(torch.load(os.path.join(d, "drlcw_ap%d.pt" % i), map_location="cpu"))
