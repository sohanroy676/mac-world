"""Run one job on the runner. A job is a list of commands [{name, args}], run in order (e.g. train, then evaluate the
saved actor). Each command's run dir (config.json, trace.csv) is copied to OUT/<id>/<name>/, the trainer log too, and
everything is printed as one base64 tar.gz in the job log (artifact blobs are not reachable from the agent container).
Placeholder {ACT} in args = actor dir shared by the commands of the job; {LAST} = absolute path of the previous command's trainer run dir (v3.8.0).
v4.1.0: each passing trainer command also gets OUT/<id>/<name>/summary.json (per-AP Mbps in three windows, trace
sha256, config, CPU model, commit) for the wave collector; NO_BUNDLE=1 skips the base64 block in the log.
Usage: run_job.py <python> <id> <cmds-json> <ref-dir-or-empty> <out-dir>   (cwd = ns-3.29/scratch/linear-mesh)"""
import base64
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time

sys.path.insert(0, os.getcwd())  # summarize_run.py lives in scratch/linear-mesh


def write_summary(dst, jid, name, sha, res, secs, log=""):
    """Small per-run record: everything the search driver and the collector need without the trace."""
    import numpy as np
    from summarize_run import summarize
    cfg = json.load(open(os.path.join(dst, "config.json")))
    s = summarize(dst, cfg["stepTime"], 300)
    steps = len(s["tot"])
    mean = lambda a, b: [float(np.mean(s["thr"][ap][a:b])) for ap in s["aps"]]
    cpu = [l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][:1]
    rec = {"job": jid, "name": name, "check": res, "sha256": sha, "secs": secs, "cfg": cfg,
           "thr_all": mean(0, steps), "thr_policy": mean(300, steps), "thr_half2": mean(steps // 2, steps),
           "cw_mean": [float(np.mean(s["cw"][ap][300:])) for ap in s["aps"]], "loss_policy": float(s["loss_policy"]),
           "delay": [[int(a), int(n), float(m), float(p50), float(p99)] for a, n, m, p50, p99 in re.findall(r"DELAY AP(\d+) n=(\d+) mean_ms=([\d.]+) p50_ms=([\d.]+) p99_ms=([\d.]+)", open(log).read())] if log else [],
           "cpu": cpu[0] if cpu else "", "commit": os.environ.get("MACWORLD_COMMIT", ""), "image": os.environ.get("MACWORLD_IMAGE", "")}
    json.dump(rec, open(os.path.join(dst, "summary.json"), "w"))


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
lines, ok, last_run = [], True, ""
fetched = False
for c in cmds:
    if "fetch" in c:  # v4.1.0 stage 2: download trained actors from branch wave-actors into {ACT} (public repo)
        import urllib.request
        os.makedirs(act_dir, exist_ok=True)
        for f in c["fetch"]["files"]:
            url = "https://raw.githubusercontent.com/%s/wave-actors/%s/%s" % (os.environ.get("GITHUB_REPOSITORY", "sohanroy676/mac-world"), c["fetch"]["src"], f)
            for k in range(4):
                try:
                    data = urllib.request.urlopen(url, timeout=60).read()
                    break
                except Exception as e:
                    if k == 3:
                        raise
                    time.sleep(5 * (k + 1))
            open(os.path.join(act_dir, f), "wb").write(data)
        fetched = True
        lines.append("%s/fetch: %d files from %s" % (jid, len(c["fetch"]["files"]), c["fetch"]["src"]))
        print(lines[-1], flush=True)
        continue
    name, args = c["name"], [a.replace("{ACT}", act_dir).replace("{LAST}", last_run) for a in c["args"]]
    script = "OSCAR_multi_ap_train.py"
    if args and args[0].endswith(".py"):  # probe jobs: first arg is a script in scratch/linear-mesh
        script, args = args[0], args[1:]
    t0 = time.time()
    before = set(glob.glob("results/multi-ap-*"))
    log = os.path.join(dst_root, name + ".log")
    with open(log, "w") as lf:
        proc = subprocess.Popen([py, script] + args, stdout=lf, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        try:
            rc = proc.wait(timeout=float(os.environ.get("JOB_TIMEOUT") or 0) or None)
        except subprocess.TimeoutExpired:  # v4.1.0: kill the whole process group (trainer, waf, simulator) and fail the command
            os.killpg(proc.pid, 9)
            proc.wait()
            rc = 124
            lf.write("\nJOB TIMEOUT after %s s\n" % os.environ.get("JOB_TIMEOUT"))
    named = re.findall(r"^APs:.* out: (results/multi-ap-\S+)\s*$", open(log).read(), re.M)  # the trainer names its run dir: safe with parallel lanes
    runs = [named[-1]] if named else sorted(set(glob.glob("results/multi-ap-*")) - before, key=os.path.getmtime)
    last_run = os.path.abspath(runs[-1]) if runs else ""
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
        sha = hashlib.sha256(open(os.path.join(d, "trace.csv"), "rb").read()).hexdigest()
        msg += "\n  sha256 trace.csv: " + sha
        write_summary(dst, jid, name, sha, res, int(time.time() - t0), log)
        if ref and len(cmds) == 1:
            same = subprocess.call(["cmp", os.path.join(d, "trace.csv"), os.path.join("../../..", ref, "trace.csv")]) == 0
            msg += "\n  cmp with %s: %s" % (ref, "IDENTICAL" if same else "DIFFERENT")
            if not same:
                res = "DIFFERENT"
    msg += "\n  check: " + res
    if res != "PASS":  # v4.1.0: a failed command prints the end of its trainer log so the cause is readable in the job log
        msg += "\n  log tail:\n" + "".join("    " + l for l in open(log).readlines()[-40:])
    print(msg, flush=True)
    lines.append(msg)
    ok = ok and res == "PASS"
    if not ok:
        break
if os.path.isdir(act_dir) and not fetched:
    shutil.copytree(act_dir, os.path.join(dst_root, "actors"))
text = "\n".join(lines)
open(os.path.join(dst_root, "result.txt"), "w").write(text + "\n")
with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a") as s:
    s.write("### %s\n```\n%s\n```\n" % (jid, text))
bio = io.BytesIO()
with tarfile.open(fileobj=bio, mode="w:gz") as tf:
    tf.add(dst_root, arcname=jid)
if os.environ.get("NO_BUNDLE") != "1":
    b64 = base64.b64encode(bio.getvalue()).decode()
    print("BUNDLE-BEGIN %s %d" % (jid, len(b64)))
    for i in range(0, len(b64), 4000):
        print("B64 " + b64[i:i + 4000])
    print("BUNDLE-END %s" % jid)
sys.exit(0 if ok else 1)
