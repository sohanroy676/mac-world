"""Run a pack of jobs on one runner, `lanes` jobs at a time (each job is a full run_job.py call, so its commands stay
in order and share {ACT}). Output of each finished job (its BUNDLE block) is printed in one piece so fetch_bundles.py
works unchanged. Usage: run_pack.py <python> <pack-id> <out-dir> <lanes>   (env PACK = JSON list of jobs; cwd = ns-3.29/scratch/linear-mesh)"""
import json
import os
import subprocess
import sys
import threading
import time

py, pid, out, lanes = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
jobs = json.loads(os.environ["PACK"])
here = os.path.dirname(os.path.abspath(__file__))
queue = list(jobs)
qlock, plock, start_lock = threading.Lock(), threading.Lock(), threading.Lock()
failed = []
t00 = time.time()


def worker():
    while True:
        with qlock:
            if not queue:
                return
            j = queue.pop(0)
        cmds = j["cmds"] if "cmds" in j else j["args"]
        env = dict(os.environ, PIN="1" if j.get("pin") else "")
        with start_lock:  # run dirs are named to the second: stagger starts
            p = subprocess.Popen([py, os.path.join(here, "run_job.py"), py, j["id"], json.dumps(cmds), j.get("ref", ""), out],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            time.sleep(2.5)
        text = p.communicate()[0].decode("utf-8", "replace")
        with plock:
            print(text, flush=True)
            print("PACK %s: job %s exit %d at %d s" % (pid, j["id"], p.returncode, time.time() - t00), flush=True)
        if p.returncode:
            failed.append(j["id"])


ts = [threading.Thread(target=worker) for _ in range(min(lanes, len(jobs)))]
for t in ts:
    t.start()
for t in ts:
    t.join()
print("PACK %s: %d jobs, %d failed %s, %d s" % (pid, len(jobs), len(failed), failed, time.time() - t00))
sys.exit(1 if failed else 0)
