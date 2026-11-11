"""Turn a job-list JSON into a GitHub matrix (JSON on stdout, key "include").
Old form (a list of {id, args|cmds, ref?, pin?}): one matrix entry per job.
Pack form ({"lanes": 4, "packs": 20, "jobs": [...]}): the jobs with target "actions" (see jobsplit.py) are balanced
(longest first) into `packs` matrix entries; each entry runs its jobs `lanes` at a time on one runner (run_pack.py)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jobsplit  # noqa: E402

batch = json.load(open(sys.argv[1]))
if isinstance(batch, list):
    jobs = batch
    ids = [j["id"] for j in jobs]
    assert len(ids) == len(set(ids)), "duplicate job ids"
    inc = [{"id": j["id"], "args": json.dumps(j["cmds"] if "cmds" in j else j["args"]), "ref": j.get("ref", ""), "pin": "1" if j.get("pin") else ""} for j in jobs]
else:
    jobs = batch["jobs"]
    ids = [j["id"] for j in jobs]
    assert len(ids) == len(set(ids)), "duplicate job ids"
    mine = [j for j in jobs if jobsplit.target(j) == "actions"]
    n = max(1, min(int(batch.get("packs", 20)), len(mine)))
    bins = [[0.0, []] for _ in range(n)]
    for j in sorted(mine, key=jobsplit.weight, reverse=True):
        b = min(bins, key=lambda x: x[0])
        b[0] += jobsplit.weight(j)
        b[1].append(j)
    inc = [{"id": "pack-%02d" % i, "pack": json.dumps(b[1]), "lanes": str(int(batch.get("lanes", 4))),
            "args": "[]", "ref": "", "pin": ""} for i, b in enumerate(bins) if b[1]]
print(json.dumps({"include": inc}))
