"""Fetch job logs of a run with `gh api`, decode BUNDLE blocks into OUT/<id>/..., print each job's result lines.
Usage: fetch_bundles.py <run_id> <out_dir>"""
import base64
import io
import json
import os
import re
import subprocess
import sys
import tarfile

run, out = sys.argv[1:3]
repo = "sohanroy676/mac-world"
jobs = json.loads(subprocess.check_output(["gh", "api", "repos/%s/actions/runs/%s/jobs?per_page=100" % (repo, run)]))["jobs"]
for j in jobs:
    if j["name"] == "prep":
        continue
    if j["status"] != "completed":  # logs of a running job are not available yet
        print("%s [%s, skipped]" % (j["name"], j["status"]))
        continue
    log = subprocess.check_output(["gh", "api", "repos/%s/actions/jobs/%d/logs" % (repo, j["id"])]).decode("utf-8", "replace")
    res = [re.sub(r"^\S+ ", "", l) for l in log.splitlines() if re.match(r"\S+ (\S+/\S+: exit|\s+sha256|\s+check|\s+cmp with)", l)]
    print("%s [%s]" % (j["name"], j["conclusion"]))
    for l in res:
        print("   " + l)
    blocks, cur = [], None  # a pack job's log holds one BUNDLE block per job; a plain job's log holds one
    for l in log.splitlines():
        l = re.sub(r"^\S+ ", "", l)
        if l.startswith("BUNDLE-BEGIN"):
            cur = []
        elif l.startswith("BUNDLE-END"):
            blocks.append(cur)
            cur = None
        elif l.startswith("B64 ") and cur is not None:
            cur.append(l[4:])
    for parts in blocks:
        tarfile.open(fileobj=io.BytesIO(base64.b64decode("".join(parts))), mode="r:gz").extractall(out)
