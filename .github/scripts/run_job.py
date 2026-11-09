"""Run one trainer job on the runner, copy the run dir to OUT/<id>/, and compare its trace.csv with a committed reference.
Usage: run_job.py <python> <id> <args-json> <ref-dir-or-empty> <out-dir>   (cwd = ns-3.29/scratch/linear-mesh)"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time

py, jid, args_json, ref, out = sys.argv[1:6]
args = json.loads(args_json)
t0 = time.time()
start_marker = time.time() - 1
log = os.path.join(out, jid + ".log")
os.makedirs(out, exist_ok=True)
with open(log, "w") as lf:
    rc = subprocess.call([py, "OSCAR_multi_ap_train.py"] + args, stdout=lf, stderr=subprocess.STDOUT)
secs = int(time.time() - t0)
runs = [d for d in glob.glob("results/multi-ap-*") if os.path.getmtime(d) >= start_marker]
runs.sort(key=os.path.getmtime)
lines = ["job %s: exit %d, %d s, run dirs %s" % (jid, rc, secs, runs)]
res = "FAIL"
if rc == 0 and len(runs) == 1:
    d = runs[0]
    dst = os.path.join(out, jid)
    os.makedirs(dst)
    for f in ("config.json", "trace.csv"):
        shutil.copy2(os.path.join(d, f), dst)
    import hashlib
    lines.append("sha256 trace.csv: " + hashlib.sha256(open(os.path.join(d, "trace.csv"), "rb").read()).hexdigest())
    txt = open(log).read()
    res = "PASS" if "RESULT: PASS" in txt else "CHECK-NOT-PASS"
    lines.append("check: " + res)
    if ref:
        a, b = os.path.join(d, "trace.csv"), os.path.join("../../..", ref, "trace.csv")
        same = subprocess.call(["cmp", a, b]) == 0
        lines.append("cmp with %s: %s" % (ref, "IDENTICAL" if same else "DIFFERENT"))
        if not same:
            lines.append(subprocess.run(["diff", a, b], stdout=subprocess.PIPE, universal_newlines=True).stdout[:3000])
else:
    lines.append("run dirs found: %d" % len(runs))
text = "\n".join(lines)
print(text)
# Transport: the agent cannot download artifact blobs, so print a base64 tar.gz of the run dir + trainer log in the job log.
import base64
import io
import tarfile
bio = io.BytesIO()
with tarfile.open(fileobj=bio, mode="w:gz") as tf:
    if len(runs) == 1:
        for root, _, files in os.walk(runs[0]):
            for fn in files:
                if fn.endswith(".wandb"):
                    continue
                full = os.path.join(root, fn)
                tf.add(full, arcname=os.path.join(jid, os.path.relpath(full, runs[0])))
    tf.add(log, arcname=os.path.join(jid, "trainer.log"))
b64 = base64.b64encode(bio.getvalue()).decode()
print("BUNDLE-BEGIN %s %d" % (jid, len(b64)))
for i in range(0, len(b64), 4000):
    print("B64 " + b64[i:i + 4000])
print("BUNDLE-END %s" % jid)
open(os.path.join(out, jid + ".result.txt"), "w").write(text + "\n")
with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a") as s:
    s.write("### %s\n```\n%s\n```\n" % (jid, text))
sys.exit(0 if res == "PASS" and "DIFFERENT" not in text else 1)
