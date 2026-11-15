"""Serial/lane job driver for the v3.5.0 M0 batches. Usage: driver.py JOBS.json LANES BATCH_DIR
JOBS.json = list of {id, args:[trainer args], deps:[ids]}; runs OSCAR_multi_ap_train.py in linear-mesh dir.
Honours BATCH_DIR/STOP between jobs. Writes BATCH_DIR/manifest.csv and batch.log lines START/-> PASS|FAIL/DONE/STOP."""
import csv, json, os, re, subprocess, sys, threading, time

jobs = json.load(open(sys.argv[1]))
lanes = int(sys.argv[2])
bdir = os.path.abspath(sys.argv[3])
os.makedirs(bdir, exist_ok=True)
cwd = "/home/pranay/mac-world/ns-3.29/scratch/linear-mesh"
py = "/home/pranay/mac-world/ns-3.29/venv/bin/python"
man = os.path.join(bdir, "manifest.csv")
lock = threading.Lock()
done = {}
if os.path.exists(man):
    for r in csv.DictReader(open(man)):
        if r["result"] == "PASS":
            done[r["id"]] = r["run_dir"]
running, failed = set(), set()


def log(msg):
    with lock:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def pick():
    with lock:
        if os.path.exists(os.path.join(bdir, "STOP")) or failed:
            return None, True
        for j in jobs:
            if j["id"] in done or j["id"] in running:
                continue
            if all(d in done for d in j.get("deps", [])):
                running.add(j["id"])
                return j, False
        pending = [j for j in jobs if j["id"] not in done]
        return None, not pending and not running


def worker(k):
    while True:
        j, fin = pick()
        if j is None:
            if fin or (os.path.exists(os.path.join(bdir, "STOP")) or failed):
                return
            if not running:
                return
            time.sleep(10)
            continue
        lf = os.path.join(bdir, j["id"] + ".log")
        log("START lane%d %s" % (k, j["id"]))
        t0 = time.time()
        rc = subprocess.run([py, "OSCAR_multi_ap_train.py"] + j["args"], cwd=cwd, stdout=open(lf, "w"), stderr=subprocess.STDOUT).returncode
        text = open(lf).read()
        m = re.search(r"out: (results/multi-ap-\S+)", text)
        ok = rc == 0 and "CHECK FAIL" not in text and ("--check" not in j["args"] or "RESULT: PASS" in text)
        with lock:
            running.discard(j["id"])
            if ok:
                done[j["id"]] = m.group(1) if m else ""
            else:
                failed.add(j["id"])
            new = not os.path.exists(man)
            with open(man, "a", newline="") as f:
                w = csv.DictWriter(f, ["id", "run_dir", "result", "returncode", "seconds"])
                if new:
                    w.writeheader()
                w.writerow(dict(id=j["id"], run_dir=m.group(1) if m else "", result="PASS" if ok else "FAIL", returncode=rc, seconds=int(time.time() - t0)))
        log("%s -> %s (%d s) %s" % (j["id"], "PASS" if ok else "FAIL", time.time() - t0, m.group(1) if m else ""))


ths = [threading.Thread(target=worker, args=(k,)) for k in range(lanes)]
for t in ths:
    t.start()
    time.sleep(3)  # stagger so same-second launches never share a results dir name
for t in ths:
    t.join()
if failed:
    log("ABORT failed: %s" % sorted(failed))
elif all(j["id"] in done for j in jobs):
    log("DONE")
else:
    log("STOP")
