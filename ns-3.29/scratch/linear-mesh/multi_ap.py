"""Helpers for the v0.6.0 multi-AP ns3-gym interface (cw.cc, apStaCounts with >1 AP).

obs   : flat Box [N*H] from ns-3, row i = AP i (newest loss first) -> reshape_obs
reward: scalar = mean of per-AP rewards (diagnostic); use the per-AP rewards from parse_ap_info
info  : "sentMb|CW|active|jain|cwSet,cwReadbackAp,reward,loss,rxDelta,phyTxDelta;..." (AP order)
"""
import numpy as np


def reshape_obs(obs, n_aps):
    return np.asarray(obs, dtype=np.float32).reshape(n_aps, -1)


def parse_ap_info(info, n_aps):
    fields = str(info).split("|")
    if len(fields) < 5:
        raise ValueError("no per-AP field in info: %r" % (info,))
    records = fields[4].split(";")
    if len(records) != n_aps:
        raise ValueError("expected %d AP records, got %d" % (n_aps, len(records)))
    keys = ("cw_set", "cw_ap", "reward", "loss", "rx", "tx")
    out = []
    for rec in records:
        vals = [float(v) for v in rec.split(",")]
        out.append(dict(zip(keys, vals)))
    return out


PAYLOAD_BITS = (1500 - 20 - 8 - 8) * 8  # UDP payload per packet, same as cw.cc


def jain(values):
    """Jain index over raw values; 0.0 if all zero (mirrors cw.cc jainFromValues)."""
    v = np.asarray(values, dtype=np.float64)
    sq = float((v * v).sum())
    return float(v.sum() ** 2 / (len(v) * sq)) if sq > 0 else 0.0


def step_metrics(recs, states, actor_losses, critic_losses, step_time):
    """W&B metrics for one env step (design section 7 names). recs = parse_ap_info output."""
    out, thr = {}, []
    for i, r in enumerate(recs, 1):
        t = r["rx"] * PAYLOAD_BITS / (step_time * 1e6)  # Mbps
        thr.append(t)
        out.update({"AP%d/CW" % i: r["cw_set"], "AP%d/Reward" % i: r["reward"], "AP%d/Throughput" % i: t,
                    "AP%d/LossRatio" % i: r["loss"], "AP%d/Observation" % i: float(states[i - 1]),
                    "AP%d/ActorLoss" % i: actor_losses[i - 1], "AP%d/CriticLoss" % i: critic_losses[i - 1]})
    tx = sum(r["tx"] for r in recs)
    rx = sum(r["rx"] for r in recs)
    out["Global/Throughput"] = sum(thr)
    out["Global/Fairness"] = jain(thr)
    out["Global/LossRatio"] = (tx - rx) / tx if tx else 0.0
    return out
