"""v4.1.0 (max-CW plan, Track A): batch search for the static ceiling families of one cell.

  python cw_search_v4_1_0.py propose --cells ../../../.github/waves/cells.json --cell s4 --family f1 --round 0 \
      --n 96 --wave w1 --out jobs.json                       # round 0: space-filling points + anchors + BEB
  python cw_search_v4_1_0.py propose ... --round 1 --summaries summaries.jsonl --out jobs.json
  python cw_search_v4_1_0.py top --cells ... --cell s4 --family f1 --summaries summaries.jsonl --k 5 --wave w1 \
      --seeds 200-209 --simTime 60 --out jobs.json           # validation jobs for the best k points per alpha
  python cw_search_v4_1_0.py table --cells ... --cell s4 --family f1 --summaries summaries.jsonl

Families (docs/design/measurement-modes-v4.1.0.md): f1 exact static CW per AP; f2 static CWmin with doubling (a grid,
no model); f3 two-phase schedule (cell entry needs "schedA"). A point is a dict {"cws": [...]} plus, for f3,
{"mute": CW, "period": steps, "a": steps}. Jobs are one run each ({"id", "w", "cmds": [{"name", "args"}]}) for
.github/scripts/make_packs.py. Summaries are the JSON lines written by .github/scripts/run_job.py (summary.json).

Score of a point for one alpha, as in gc_analysis.cell_table: U = mean over seeds of utility(per-AP Mbps);
feasible = mean-over-seeds Mbps >= (1 - floorTol) * floor, floors from the BEB runs on the same seeds.

Rounds 1+: per alpha one Gaussian process on U and one on the floor margin m = min_i x_i / floor_i, both over the
point's coordinates scaled to [0, 1] (log2 CW, log2 period, phase-A fraction). Kernel: Matern 5/2, one length scale
chosen from a grid by marginal likelihood, noise from the seed spread. Acquisition: expected improvement over the
best feasible U times P(m >= 1 - floorTol); a batch is filled one point at a time, each time adding the model's own
mean at the chosen point as if it had been observed. DECISIONS: the search is a heuristic for proposing points; the
ceiling is set only by the validation runs on fresh seeds. numpy only.
"""
import argparse
import json
import math
import sys

import numpy as np

from gc_analysis import feasible, floors, parse_seeds, utility

LO, HI = 2.0, 15.0  # log2 CW range: 4 .. 32767
PER_LO, PER_HI = 1.0, math.log2(200)  # schedule period 2 .. 200 steps (20 ms .. 2 s at 10 ms steps)
FRAC_LO, FRAC_HI = 0.1, 0.9


def halton(n, dim, seed):
    """Scrambled Halton points in [0, 1)^dim: a random digit permutation per base, fixed by `seed`."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    rng = np.random.RandomState(seed)
    out = np.zeros((n, dim))
    for d in range(dim):
        b = primes[d]
        perm = np.concatenate([[0], rng.permutation(np.arange(1, b))])
        for i in range(n):
            f, x, k = 1.0, 0.0, i + 1
            while k > 0:
                f /= b
                x += f * perm[k % b]
                k //= b
            out[i, d] = x
    return out


def dims(cell, family):
    return len(cell["counts"]) + (3 if family == "f3" else 0)


def decode(u, cell, family):
    """[0,1]^d -> point with integer CWs and steps."""
    n = len(cell["counts"])
    cw = lambda v: int(min(32767, max(4, round(2 ** (LO + v * (HI - LO))))))
    p = {"cws": [cw(v) for v in u[:n]]}
    if family == "f3":
        p["mute"] = cw(u[n])
        p["period"] = int(min(200, max(2, round(2 ** (PER_LO + u[n + 1] * (PER_HI - PER_LO))))))
        p["a"] = int(min(p["period"] - 1, max(1, round((FRAC_LO + u[n + 2] * (FRAC_HI - FRAC_LO)) * p["period"]))))
    return p


def encode(p, family):
    sc = lambda c: (math.log2(c) - LO) / (HI - LO)
    u = [sc(c) for c in p["cws"]]
    if family == "f3":
        u += [sc(p["mute"]), (math.log2(p["period"]) - PER_LO) / (PER_HI - PER_LO), (p["a"] / p["period"] - FRAC_LO) / (FRAC_HI - FRAC_LO)]
    return np.clip(np.array(u, dtype=float), 0.0, 1.0)


def key(p):
    return json.dumps(p, sort_keys=True)


def point_args(p, family):
    a = ["--mode", "static", "--apCws", ",".join(map(str, p["cws"]))]
    if family == "f2":
        return a + ["--cwMinOnly", "--cwLo", "3"]
    a += ["--cwHold", "--cwLo", "4", "--cwHi", "32767"]
    if family == "f3":
        a += ["--schedPeriodSteps", str(p["period"]), "--schedASteps", str(p["a"]), "--schedMuteCw", str(p["mute"])]
    return a


def point_of(cfg, family):
    """The point a finished run belongs to, read back from its config.json (None = not a point of this family)."""
    if cfg.get("mode") != "static":
        return None
    fam = "f2" if cfg.get("cwMinOnly") else "f3" if cfg.get("schedA") else "f1" if cfg.get("cwHold") else None
    if fam != family:
        return None
    p = {"cws": [int(c) for c in cfg["apCws"].split(",")]}
    if family == "f3":
        p.update(mute=cfg["schedMuteCw"], period=cfg["schedPeriodSteps"], a=cfg["schedASteps"])
    return p


def same_cell(cfg, cell):
    base = cell["args"]
    val = lambda flag, default: base[base.index(flag) + 1] if flag in base else default
    return (cfg.get("apStaCounts") == val("--apStaCounts", "20,40") and (cfg.get("apHidden") or "") == val("--apHidden", "")
            and (cfg.get("apLoads") or "") == val("--apLoads", "") and abs(float(cfg.get("offeredLoad", 150)) - float(val("--offeredLoad", 150))) < 1e-9
            and (cfg.get("staSchedule") or "") == val("--staSchedule", "") and (cfg.get("schedA") or "") in ("", cell.get("schedA", "")))


def load(summaries, cell, family, seeds, sim_time, window):
    """-> (points {key: {"p": point, "thr": {seed: [Mbps per AP]}}}, beb {seed: [Mbps per AP]})"""
    pts, beb = {}, {}
    for line in open(summaries):
        r = json.loads(line)
        cfg = r["cfg"]
        if r.get("check") != "PASS" or cfg.get("seed") not in seeds or not same_cell(cfg, cell) or abs(cfg["simTime"] - sim_time) > 1e-9:
            continue
        if cfg["mode"] == "beb":
            beb[cfg["seed"]] = r[window]
            continue
        p = point_of(cfg, family)
        if p is not None:
            pts.setdefault(key(p), {"p": p, "thr": {}})["thr"][cfg["seed"]] = r[window]
    return pts, beb


def score(pts, beb, counts, alpha, floor_tol):
    """Rows for the points that have every BEB seed: U mean, standard error, floor margin, feasibility."""
    seeds = sorted(beb)
    assert seeds, "no BEB runs of this cell in the summaries (round 0 includes them)"
    fl = floors([float(np.mean([beb[s][i] for s in seeds])) for i in range(len(counts))], counts)
    ub = [utility(beb[s], counts, alpha) for s in seeds]
    rows = []
    for k, v in pts.items():
        if any(s not in v["thr"] for s in seeds):
            continue
        us = [utility(v["thr"][s], counts, alpha) for s in seeds]
        mt = [float(np.mean([v["thr"][s][i] for s in seeds])) for i in range(len(counts))]
        rows.append(dict(p=v["p"], u=float(np.mean(us)), se=float(np.std(us, ddof=1) / math.sqrt(len(us))) if len(us) > 1 else 0.0,
                         margin=min(t / f if f > 0 else 9.9 for t, f in zip(mt, fl)), feasible=feasible(mt, fl, floor_tol), thr=mt))
    return rows, dict(floors=fl, u_beb=float(np.mean(ub)), sd_beb=float(np.std(ub, ddof=1)) if len(ub) > 1 else 0.0, seeds=seeds)


# ---- Gaussian process (numpy only) ----
def matern52(A, B, ell):
    d = np.sqrt(np.maximum(0.0, ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))) / ell
    return (1 + math.sqrt(5) * d + 5.0 / 3.0 * d * d) * np.exp(-math.sqrt(5) * d)


class GP:
    """Zero-mean GP on standardised targets; length scale by marginal likelihood over a grid; fixed noise variance."""

    def __init__(self, X, y, noise_var):
        self.X, self.mu, self.sd = X, float(np.mean(y)), float(np.std(y)) or 1.0
        self.z = (np.asarray(y) - self.mu) / self.sd
        self.nv = max(noise_var / self.sd ** 2, 1e-6)
        best = None
        for ell in (0.05, 0.1, 0.2, 0.4, 0.8, 1.6):
            L = np.linalg.cholesky(matern52(X, X, ell) + self.nv * np.eye(len(X)))
            a = np.linalg.solve(L.T, np.linalg.solve(L, self.z))
            ll = -0.5 * float(self.z @ a) - float(np.log(np.diag(L)).sum())
            if best is None or ll > best[0]:
                best = (ll, ell)
        self.ell = best[1]
        self._fit()

    def _fit(self):
        self.L = np.linalg.cholesky(matern52(self.X, self.X, self.ell) + self.nv * np.eye(len(self.X)))
        self.a = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.z))

    def predict(self, Xs):
        Ks = matern52(Xs, self.X, self.ell)
        v = np.linalg.solve(self.L, Ks.T)
        var = np.maximum(1e-12, 1.0 - (v * v).sum(0))
        return self.mu + self.sd * (Ks @ self.a), self.sd * np.sqrt(var)

    def add(self, x, y):
        self.X = np.vstack([self.X, x[None, :]])
        self.z = np.append(self.z, (y - self.mu) / self.sd)
        self._fit()


_cdf = np.vectorize(lambda t: 0.5 * (1 + math.erf(t / math.sqrt(2))))
_pdf = lambda t: np.exp(-0.5 * t * t) / math.sqrt(2 * math.pi)


def propose_gp(rows, cell, family, n_new, floor_tol, rng, taken):
    """n_new new points by constrained expected improvement with a kriging-believer batch."""
    X = np.array([encode(r["p"], family) for r in rows])
    gu = GP(X, [r["u"] for r in rows], float(np.mean([r["se"] ** 2 for r in rows])))
    gm = GP(X, [min(r["margin"], 3.0) for r in rows], 1e-4)
    feas = [r["u"] for r in rows if r["feasible"]]
    best = max(feas) if feas else min(r["u"] for r in rows)
    d, out = X.shape[1], []
    order = np.argsort([-r["u"] if r["feasible"] else np.inf for r in rows])[:5]
    while len(out) < n_new:
        cand = [rng.rand(2048, d)] + [np.clip(X[i] + rng.randn(256, d) * s, 0, 1) for i in order for s in (0.02, 0.08)]
        C = np.vstack(cand)
        mu, sd = gu.predict(C)
        mm, sm = gm.predict(C)
        t = (mu - best) / sd
        acq = (sd * (t * _cdf(t) + _pdf(t))) * _cdf((mm - (1 - floor_tol)) / sm)
        for i in np.argsort(-acq):
            p = decode(C[i], cell, family)
            if key(p) not in taken:
                break
        else:
            break
        taken.add(key(p))
        out.append(p)
        x = encode(p, family)
        gu.add(x, float(gu.predict(x[None, :])[0][0]))
        gm.add(x, float(gm.predict(x[None, :])[0][0]))
    return out


def anchors(cell, family):
    n = len(cell["counts"])
    pts = [{"cws": [c] * n} for c in (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)]
    pts += [{"cws": list(c)} for c in cell.get("anchors", [])]
    if family == "f3":
        a_set = {int(v) - 1 for v in cell["schedA"].split(",")}
        base = []
        for c in (16, 64):
            base += [{"cws": [c] * n, "mute": m, "period": per, "a": max(1, round(per * len(a_set) / n))} for m in (1023, 32767) for per in (10, 40, 160)]
        pts = base
    return pts


def f2_grid(cell):
    n, vals = len(cell["counts"]), [2 ** k - 1 for k in range(2, 11)]  # 3 .. 1023
    if n <= 2:
        return [{"cws": [a, b]} for a in vals for b in vals] if n == 2 else [{"cws": [a]} for a in vals]
    rng = np.random.RandomState(7)
    pts = {key({"cws": [v] * n}): {"cws": [v] * n} for v in vals}
    while len(pts) < 100:
        p = {"cws": [int(vals[i]) for i in rng.randint(len(vals), size=n)]}
        pts[key(p)] = p
    return list(pts.values())


def jobs_for(points, cell, cell_name, family, wave, label, seeds, sim_time, with_beb):
    base = cell["args"] + ["--stepTime", "0.01", "--check", "--simTime", "%g" % sim_time]
    sched = ["--schedA", cell["schedA"]] + (["--schedB", cell["schedB"]] if cell.get("schedB") else []) if family == "f3" else []
    w, jobs = int(round(1.1 * sim_time)), []
    for s in seeds if with_beb else []:
        jid = "%s-%s-beb-t%g-s%d" % (wave, cell_name, sim_time, s)
        jobs.append({"id": jid, "w": w, "timeout": int(70 * w + 300), "cmds": [{"name": "run", "args": base + ["--mode", "beb", "--seed", str(s), "--tag", "%s-%s-beb" % (wave, cell_name)]}]})
    for i, p in enumerate(points):
        for s in seeds:
            jid = "%s-%s-%s-%s-p%03d-s%d" % (wave, cell_name, family, label, i, s)
            jobs.append({"id": jid, "w": w, "timeout": int(70 * w + 300), "point": p, "cmds": [{"name": "run", "args": base + point_args(p, family) + sched + ["--seed", str(s), "--tag", "%s-%s-%s-%s" % (wave, cell_name, family, label)]}]})
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["propose", "top", "table"])
    ap.add_argument("--cells", required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--family", choices=["f1", "f2", "f3"], required=True)
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--n", type=int, default=96, help="propose: number of new points")
    ap.add_argument("--k", type=int, default=5, help="top: points per alpha")
    ap.add_argument("--seeds", default="", help="default: 0-3 for propose/table, 200-209 for top")
    ap.add_argument("--searchSeeds", default="0-3", help="top: seeds the ranking is read from")
    ap.add_argument("--simTime", type=float, default=0, help="default: 30 for propose/table, 60 for top")
    ap.add_argument("--searchSimTime", type=float, default=30)
    ap.add_argument("--window", default="thr_policy", help="summary field scored in the search (thr_policy = after 3 s)")
    ap.add_argument("--alphas", default="0,1,4")
    ap.add_argument("--floorTol", type=float, default=0.05)
    ap.add_argument("--summaries", default="")
    ap.add_argument("--wave", default="w1")
    ap.add_argument("--noBeb", action="store_true", help="do not add the BEB runs (another family's batch of the same cell, seeds and length already has them)")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    cell = json.load(open(args.cells))[args.cell]
    cell["counts"] = [int(c) for c in cell["args"][cell["args"].index("--apStaCounts") + 1].split(",")]
    alphas = [float(a) for a in args.alphas.split(",")]
    assert args.family != "f3" or cell.get("schedA"), "f3 needs \"schedA\" in the cell entry"

    if args.cmd == "propose":
        seeds, sim = parse_seeds(args.seeds or "0-3"), args.simTime or 30
        if args.family == "f2":
            pts = f2_grid(cell)
        elif args.round == 0:
            pts = anchors(cell, args.family)
            seen = {key(p) for p in pts}
            for u in halton(4 * args.n, dims(cell, args.family), seed=1000 + len(cell["counts"])):
                p = decode(u, cell, args.family)
                if key(p) not in seen and len(pts) < args.n:
                    seen.add(key(p))
                    pts.append(p)
        else:
            done, beb = load(args.summaries, cell, args.family, set(seeds), sim, args.window)
            taken, pts = set(done), []
            rng = np.random.RandomState(100 * args.round + len(done))
            for j, a in enumerate(alphas):
                rows, _ = score(done, beb, cell["counts"], a, args.floorTol)
                assert len(rows) >= 8, "round %d needs at least 8 finished points, found %d" % (args.round, len(rows))
                share = args.n // len(alphas) + (1 if j < args.n % len(alphas) else 0)
                pts += propose_gp(rows, cell, args.family, share, args.floorTol, rng, taken)
        jobs = jobs_for(pts, cell, args.cell, args.family, args.wave, "r%d" % args.round, sorted(seeds), sim, with_beb=args.round == 0 and not args.noBeb)
    else:
        s_seeds = parse_seeds(args.searchSeeds if args.cmd == "top" else (args.seeds or "0-3"))
        s_sim = args.searchSimTime if args.cmd == "top" else (args.simTime or 30)
        done, beb = load(args.summaries, cell, args.family, set(s_seeds), s_sim, args.window)
        chosen, lines = {}, []
        for a in alphas:
            rows, info = score(done, beb, cell["counts"], a, args.floorTol)
            ranked = sorted([r for r in rows if r["feasible"]], key=lambda r: -r["u"])
            lines.append("alpha %g: %d points, %d feasible, U_BEB %.4f (SD %.4f), floors %s" % (a, len(rows), len(ranked), info["u_beb"], info["sd_beb"], ["%.2f" % f for f in info["floors"]]))
            for r in ranked[:args.k]:
                chosen[key(r["p"])] = r["p"]
                lines.append("  U %.4f +- %.4f  margin %.2f  thr %s  %s" % (r["u"], r["se"], r["margin"], ["%.2f" % t for t in r["thr"]], key(r["p"])))
        print("\n".join(lines))
        if args.cmd == "table":
            return 0
        v_seeds, v_sim = parse_seeds(args.seeds or "200-209"), args.simTime or 60
        jobs = jobs_for(list(chosen.values()), cell, args.cell, args.family, args.wave, "val", sorted(v_seeds), v_sim, with_beb=not args.noBeb)
    print("%d jobs, %.1f lab-h (a 30 s run counts 0.2)" % (len(jobs), sum(j["w"] for j in jobs) / 1.1 / 30 * 0.2), file=sys.stderr)
    json.dump({"jobs": jobs}, open(args.out, "w") if args.out else sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
