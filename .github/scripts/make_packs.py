"""v4.1.0 short packs: cut a batch into packs of about --minutes each and deal them to shards (forks).

  make_packs.py batch.json --shards 7 --lanes 4 --minutes 40 [--rate 1.0] --out packs.json
  make_packs.py packs.json --matrix SHARD          # GitHub matrix for one shard: {"include": [{"pack": i}, ...]}
  make_packs.py packs.json --pack SHARD INDEX      # the jobs of one pack as a JSON list (env PACK of run_pack.py)

batch.json = {"jobs": [{"id", "w", "cmds"}, ...]}; w = relative cost (the search driver writes 1.1 x simulated
seconds, the convention of the earlier batches). --rate = wall seconds per unit of w on one lane; a pack holds about
lanes x minutes x 60 / rate of w, so it takes about --minutes on a reference runner. Jobs are sorted by id and dealt round-robin, pack k goes to
shard k mod shards: the cut is a pure function of the batch, so any shard can be recomputed anywhere.
packs.json = {"lanes", "shards": [[pack, ...], ...]} with pack = {"id", "jobs": [...]}. GitHub allows 256 matrix
entries per run; more packs per shard than that is an error (dispatch the wave in parts).
"""
import argparse
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--shards", type=int, default=1)
ap.add_argument("--lanes", type=int, default=4)
ap.add_argument("--minutes", type=float, default=40)
ap.add_argument("--rate", type=float, default=14.0, help="wall seconds per unit of w on one lane with 4 lanes busy (measured 2026-11-14: 11 to 17 for 30 s S2/S4 runs with w 33)")
ap.add_argument("--out", default="")
ap.add_argument("--matrix", type=int, default=None)
ap.add_argument("--pack", type=int, nargs=2, default=None)
args = ap.parse_args()
data = json.load(open(args.file))
if args.matrix is not None:
    print(json.dumps({"include": [{"pack": i} for i in range(len(data["shards"][args.matrix]))]}))
    sys.exit(0)
if args.pack is not None:
    print(json.dumps(data["shards"][args.pack[0]][args.pack[1]]["jobs"]))
    sys.exit(0)
jobs = sorted(data["jobs"], key=lambda j: j["id"])
assert len({j["id"] for j in jobs}) == len(jobs), "duplicate job ids"
budget = args.lanes * args.minutes * 60.0 / args.rate
n_packs = max(1, int(round(sum(j["w"] for j in jobs) / budget)))
packs = [[] for _ in range(n_packs)]
for i, j in enumerate(sorted(jobs, key=lambda j: (-j["w"], j["id"]))):  # heavy first, round-robin: packs end up equal in w
    packs[i % n_packs].append({k: v for k, v in j.items() if k != "point"})
shards = [[] for _ in range(args.shards)]
for k, p in enumerate(packs):
    shards[k % args.shards].append({"id": "p%04d" % k, "jobs": p})
assert max(len(s) for s in shards) <= 256, "more than 256 packs in one shard: split the batch"
json.dump({"lanes": args.lanes, "shards": shards}, open(args.out, "w") if args.out else sys.stdout)
print("%d jobs, %d packs of about %.0f min, %d shards (%s packs each)" % (len(jobs), n_packs, args.minutes, args.shards, [len(s) for s in shards]), file=sys.stderr)
