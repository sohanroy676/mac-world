"""Split the Actions jobs of a batch file into N disjoint batch files, one per fork/account, balanced by weight.
Usage: split_batch.py <batch.json> <N> <out-prefix>   -> <out-prefix>0.json ... <out-prefix>N-1.json
Each output keeps {"lanes", "packs"} of the input; push file k to `.github/jobs/packs-current.json` of fork k.
Jobs whose target is "hf" are not written (the HF Spaces take them with the shard option k/n of tools/hf/hfjobs.py).
Job ids stay unchanged, so results from all forks can be copied into one results tree."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jobsplit  # noqa: E402

path, n, prefix = sys.argv[1], int(sys.argv[2]), sys.argv[3]
batch = json.load(open(path))
jobs, lanes, packs = (batch, 4, 20) if isinstance(batch, list) else (batch["jobs"], batch.get("lanes", 4), batch.get("packs", 20))
mine = sorted((j for j in jobs if jobsplit.target(j) == "actions"), key=lambda j: (-jobsplit.weight(j), j["id"]))
bins = [[0.0, []] for _ in range(n)]
for j in mine:
    b = min(bins, key=lambda x: x[0])
    b[0] += jobsplit.weight(j)
    b[1].append(j)
for k, b in enumerate(bins):
    json.dump({"lanes": lanes, "packs": packs, "jobs": b[1]}, open("%s%d.json" % (prefix, k), "w"), indent=1)
    print("%s%d.json: %d jobs, weight %.0f" % (prefix, k, len(b[1]), b[0]))
