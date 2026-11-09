"""Probe which torch/numpy float32 ops differ between CPU vendors (hex of results) for a fixed input."""
import numpy as np
import torch

torch.set_num_threads(1)
torch.manual_seed(100)
np.random.seed(100)
x = torch.randn(1, 5)
lin = torch.nn.Linear(5, 400)
lin2 = torch.nn.Linear(400, 300)
lin3 = torch.nn.Linear(300, 1)
h = lin(x)
h2 = torch.relu(h)
g = lin2(h2)
o = lin3(torch.relu(g))


def hx(t):
    return np.asarray(t.detach().numpy(), dtype=np.float32).tobytes().hex()[:64] + "..." + str(hash(np.asarray(t.detach().numpy(), dtype=np.float32).tobytes()) % 10**9)


import hashlib


def hh(t):
    return hashlib.sha256(np.asarray(t.detach().numpy(), dtype=np.float32).tobytes()).hexdigest()[:12]


print("linear1", hh(h))
print("linear2", hh(g))
print("linear3", hh(o))
print("tanh", hh(torch.tanh(o * 3)))
print("tanh_big", hh(torch.tanh(torch.randn(1000))))
print("exp", hh(torch.exp(torch.randn(1000))))
print("log", hh(torch.log(torch.rand(1000) + 0.1)))
print("sigmoid", hh(torch.sigmoid(torch.randn(1000))))
a = torch.randn(8, 400)
b = torch.randn(400, 300)
print("matmul_b8", hh(a @ b))
print("addmm_b1", hh(torch.addmm(torch.zeros(300), torch.randn(1, 400), b)))
print("np_exp", hashlib.sha256(np.exp(np.random.randn(1000).astype(np.float32)).tobytes()).hexdigest()[:12])
print("np_tanh64", hashlib.sha256(np.tanh(np.random.randn(1000)).tobytes()).hexdigest()[:12])
print("np_pow", hashlib.sha256(np.power(2.0, np.random.randn(1000)).tobytes()).hexdigest()[:12])
print("mkldnn", torch.backends.mkldnn.is_available(), "mkl", torch.backends.mkl.is_available())
print(torch.__config__.show().splitlines()[:6])
