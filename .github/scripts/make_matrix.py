"""Turn a job-list JSON ([{id, args, ref?}]) into a GitHub matrix (JSON on stdout, key "include")."""
import json
import sys

jobs = json.load(open(sys.argv[1]))
ids = [j["id"] for j in jobs]
assert len(ids) == len(set(ids)), "duplicate job ids"
inc = [{"id": j["id"], "args": json.dumps(j["cmds"] if "cmds" in j else j["args"]), "ref": j.get("ref", ""), "pin": "1" if j.get("pin") else ""} for j in jobs]
print(json.dumps({"include": inc}))
