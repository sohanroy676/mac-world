"""Run the 'hf' jobs of a batch file on the Hugging Face Space, `lanes` at a time, and push every finished job to GitHub.
Usage: hfjobs.py <batch.json> [lanes=16]     (env: GH_TOKEN for pushing, RUN_LABEL, BENCH_VENV, BENCH_ROOT, ALL=1 runs every job)
Each job = one .github/scripts/run_job.py call (same interface as Actions). Results: branch bench/hf-results,
hf-jobs/<batch>/<job>.tar.gz + <job>.result.txt, status.json every minute. A restarted Space skips jobs whose result.txt
already says PASS, so the batch resumes where it stopped."""
import base64, io, json, os, subprocess, sys, tarfile, threading, time, urllib.request

ROOT = os.environ.get("BENCH_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
VENV = os.environ.get("BENCH_VENV", os.path.expanduser("~/venv37"))
TRAIN = os.path.join(ROOT, "ns-3.29/scratch/linear-mesh")
RUN_JOB = os.environ.get("RUN_JOB", os.path.join(ROOT, ".github/scripts/run_job.py"))
OUT = os.environ.get("HFJOBS_OUT", os.path.join(ROOT, "bench-results/hfjobs"))
REPO, BRANCH = "sohanroy676/mac-world", "bench/hf-results"
sys.path.insert(0, os.path.join(ROOT, ".github/scripts"))
import jobsplit  # noqa: E402

batch_path, lanes = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 16
batch = json.load(open(os.path.join(ROOT, batch_path) if not os.path.isabs(batch_path) else batch_path))
jobs = batch if isinstance(batch, list) else batch["jobs"]
name = os.path.splitext(os.path.basename(batch_path))[0]
mine = [j for j in jobs if os.environ.get("ALL") or jobsplit.target(j) == "hf"]
os.makedirs(OUT, exist_ok=True)
lock = threading.Lock()
st = {"total": len(mine), "done": [], "failed": [], "running": [], "skipped": [], "boot": open("/proc/sys/kernel/random/boot_id").read().strip() if os.path.exists("/proc/sys/kernel/random/boot_id") else "?"}


def api(path, data=None, method="GET"):
    tok = os.environ.get("GH_TOKEN")
    if not tok:
        return None
    h = {"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json", "Content-Type": "application/json", "User-Agent": "hfjobs"}
    url = "https://api.github.com/repos/%s/contents/%s" % (REPO, path)
    req = urllib.request.Request(url + ("?ref=" + BRANCH if method == "GET" else ""), json.dumps(data).encode() if data else None, h, method=method)
    return json.load(urllib.request.urlopen(req, timeout=60))


def put(path, blob):
    for attempt in range(4):
        try:
            sha = None
            try:
                sha = api(path)["sha"]
            except Exception:
                pass
            body = {"message": "hf-jobs: " + path, "branch": BRANCH, "content": base64.b64encode(blob).decode()}
            if sha:
                body["sha"] = sha
            return api(path, body, "PUT") is not None
        except Exception as e:
            print("push failed (try %d): %s" % (attempt + 1, e), flush=True)
            time.sleep(5 * (attempt + 1))
    return False


def already_passed(jid):
    try:
        r = api("hf-jobs/%s/%s.result.txt" % (name, jid))
        text = base64.b64decode(r["content"]).decode()
        return "check: PASS" in text and "FAIL" not in text and "DIFFERENT" not in text and "NOT-PASS" not in text
    except Exception:
        return False


def status():
    with lock:
        s = dict(st, t=time.time(), batch=name, lanes=lanes)
    put("hf-jobs/%s/status.json" % name, json.dumps(s, indent=1).encode())


queue = sorted(mine, key=jobsplit.weight, reverse=True)
start_lock = threading.Lock()


def worker():
    while True:
        with lock:
            if not queue:
                return
            j = queue.pop(0)
        jid = j["id"]
        if already_passed(jid):
            with lock:
                st["skipped"].append(jid)
            continue
        cmds = j["cmds"] if "cmds" in j else j["args"]
        env = dict(os.environ, PIN="1" if j.get("pin") else "")
        with lock:
            st["running"].append(jid)
        with start_lock:  # run dirs are named to the second
            log = open(os.path.join(OUT, jid + ".log"), "w")
            p = subprocess.Popen([VENV + "/bin/python", RUN_JOB, VENV + "/bin/python", jid, json.dumps(cmds), j.get("ref", ""), os.path.join(OUT, "bundles")],
                                 cwd=TRAIN, stdout=log, stderr=subprocess.STDOUT, env=env)
            time.sleep(2.5)
        rc = p.wait()
        log.close()
        d = os.path.join(OUT, "bundles", jid)
        ok = rc == 0 and os.path.isdir(d)
        if os.path.isdir(d):
            bio = io.BytesIO()
            with tarfile.open(fileobj=bio, mode="w:gz") as tf:
                tf.add(d, arcname=jid)
            put("hf-jobs/%s/%s.tar.gz" % (name, jid), bio.getvalue())
            put("hf-jobs/%s/%s.result.txt" % (name, jid), open(os.path.join(d, "result.txt"), "rb").read() if os.path.exists(os.path.join(d, "result.txt")) else b"no result.txt\n")
        else:
            put("hf-jobs/%s/%s.result.txt" % (name, jid), ("exit %d, no output dir\nFAIL\n" % rc).encode())
        with lock:
            st["running"].remove(jid)
            st["done" if ok else "failed"].append(jid)
        print("job %s rc %d ok=%s" % (jid, rc, ok), flush=True)


stop = threading.Event()


def hb():
    while not stop.is_set():
        status()
        stop.wait(60)


threading.Thread(target=hb, daemon=True).start()
ts = [threading.Thread(target=worker) for _ in range(min(lanes, max(1, len(mine))))]
for t in ts:
    t.start()
for t in ts:
    t.join()
stop.set()
status()
print("finished: %d done, %d failed %s, %d skipped" % (len(st["done"]), len(st["failed"]), st["failed"], len(st["skipped"])), flush=True)
sys.exit(1 if st["failed"] else 0)
