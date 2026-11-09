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
    log = subprocess.check_output(["gh", "api", "repos/%s/actions/jobs/%d/logs" % (repo, j["id"])]).decode("utf-8", "replace")
    res = [re.sub(r"^\S+ ", "", l) for l in log.splitlines() if re.match(r"\S+ (job |sha256|check|cmp with)", l)]
    print("%s [%s]" % (j["name"], j["conclusion"]))
    for l in res:
        print("   " + l)
    parts = [re.sub(r"^\S+ B64 ", "", l) for l in log.splitlines() if re.match(r"\S+ B64 ", l)]
    if parts:
        tarfile.open(fileobj=io.BytesIO(base64.b64decode("".join(parts))), mode="r:gz").extractall(out)
