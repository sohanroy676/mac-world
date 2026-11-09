"""Run one job on the runner. A job is a list of commands [{name, args}], run in order (e.g. train, then evaluate the
saved actor). Each command's run dir (config.json, trace.csv) is copied to OUT/<id>/<name>/, the trainer log too, and
everything is printed as one base64 tar.gz in the job log (artifact blobs are not reachable from the agent container).
Placeholder {ACT} in args = actor dir shared by the commands of the job.
Usage: run_job.py <python> <id> <cmds-json> <ref-dir-or-empty> <out-dir>   (cwd = ns-3.29/scratch/linear-mesh)"""
import base64
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time

py, jid, spec, ref, out = sys.argv[1:6]
cmds = json.loads(spec)
if cmds and isinstance(cmds[0], str):  # old form: one list of args
    cmds = [{"name": "run", "args": cmds}]
env = dict(os.environ)
if os.environ.get("PIN") == "1":  # same float results on every CPU model: no ISA-specific torch/MKL kernels, one thread
    env.update(ATEN_CPU_CAPABILITY="default", MKL_CBWR="COMPATIBLE", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
act_dir = os.path.abspath(os.path.join("results", "actors-" + jid))
dst_root = os.path.join(out, jid)
os.makedirs(dst_root, exist_ok=True)
lines, ok = [], True
for c in cmds:
    name, args = c["name"], [a.replace("{ACT}", act_dir) for a in c["args"]]
    script = "OSCAR_multi_ap_train.py"
    if args and args[0].endswith(".py"):  # probe jobs: first arg is a script in scratch/linear-mesh
        script, args = args[0], args[1:]
    t0 = time.time()
    marker = t0 - 1
    log = os.path.join(dst_root, name + ".log")
    with open(log, "w") as lf:
        rc = subprocess.call([py, script] + args, stdout=lf, stderr=subprocess.STDOUT, env=env)
    runs = sorted((d for d in glob.glob("results/multi-ap-*") if os.path.getmtime(d) >= marker), key=os.path.getmtime)
    res = "FAIL"
    msg = "%s/%s: exit %d, %d s, pin=%s, run dirs %s" % (jid, name, rc, int(time.time() - t0), env.get("PIN") == "1", runs)
    if rc == 0 and script != "OSCAR_multi_ap_train.py":
        res = "PASS"
    elif rc == 0 and len(runs) == 1:
        d = runs[0]
        dst = os.path.join(dst_root, name)
        os.makedirs(dst)
        for f in ("config.json", "trace.csv"):
            shutil.copy2(os.path.join(d, f), dst)
        res = "PASS" if "RESULT: PASS" in open(log).read() else "CHECK-NOT-PASS"
        msg += "\n  sha256 trace.csv: " + hashlib.sha256(open(os.path.join(d, "trace.csv"), "rb").read()).hexdigest()
        if ref and len(cmds) == 1:
            same = subprocess.call(["cmp", os.path.join(d, "trace.csv"), os.path.join("../../..", ref, "trace.csv")]) == 0
            msg += "\n  cmp with %s: %s" % (ref, "IDENTICAL" if same else "DIFFERENT")
            if not same:
                res = "DIFFERENT"
    msg += "\n  check: " + res
    print(msg, flush=True)
    lines.append(msg)
    ok = ok and res == "PASS"
    if not ok:
        break
if os.path.isdir(act_dir):
    shutil.copytree(act_dir, os.path.join(dst_root, "actors"))
text = "\n".join(lines)
open(os.path.join(dst_root, "result.txt"), "w").write(text + "\n")
with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a") as s:
    s.write("### %s\n```\n%s\n```\n" % (jid, text))
bio = io.BytesIO()
with tarfile.open(fileobj=bio, mode="w:gz") as tf:
    tf.add(dst_root, arcname=jid)
b64 = base64.b64encode(bio.getvalue()).decode()
print("BUNDLE-BEGIN %s %d" % (jid, len(b64)))
for i in range(0, len(b64), 4000):
    print("B64 " + b64[i:i + 4000])
print("BUNDLE-END %s" % jid)
sys.exit(0 if ok else 1)
