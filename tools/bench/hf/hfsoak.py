"""HF Space scaling + soak harness (branch bench/hf-scale). Run after tools/bench/run_bench.sh hf --no-apt --smoke
has built ns-3 and the venv. Modes:
  scale N [N ...]   run N copies of the 20,40 beb cell at once for each N, log time per cell + CPU steal/throttle
  soak HOURS K      keep K cells running for HOURS, log every cell, heartbeat every 60 s
Every record is appended to LOGDIR/events.jsonl and pushed to GitHub branch bench/hf-results when GH_TOKEN is set."""
import base64, json, os, subprocess, sys, threading, time, urllib.request

ROOT = os.environ.get("BENCH_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
VENV = os.environ.get("BENCH_VENV", os.path.expanduser("~/venv37"))
TRAIN = os.path.join(ROOT, "ns-3.29/scratch/linear-mesh")
LOGDIR = os.environ.get("BENCH_LOGDIR", os.path.join(ROOT, "bench-results/hfsoak"))
CELL_CMD = os.environ.get("CELL_CMD")  # test hook: replace the real cell with another command ({seed} is substituted)
REPO, BRANCH = "sohanroy676/mac-world", "bench/hf-results"
EV = os.path.join(LOGDIR, "events.jsonl")
os.makedirs(LOGDIR, exist_ok=True)
lock = threading.Lock()
start_lock = threading.Lock()  # output dirs are named to the second: never start two cells in the same second

def boot_id():
    try: return open("/proc/sys/kernel/random/boot_id").read().strip()
    except OSError: return "?"

def cpu_stats():
    """Cumulative steal jiffies, cgroup throttling counters and load: shows shared or throttled CPU."""
    d = {"load": os.getloadavg(), "nproc": os.cpu_count()}
    try:
        f = open("/proc/stat").readline().split()
        d["jiffies_total"], d["jiffies_steal"] = sum(map(int, f[1:])), int(f[8])
    except OSError: pass
    for p in ("/sys/fs/cgroup/cpu.stat", "/sys/fs/cgroup/cpu/cpu.stat"):
        try:
            d["cgroup_cpu_stat"] = dict(l.split() for l in open(p)); break
        except OSError: pass
    for p in ("/sys/fs/cgroup/cpu.max", "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"):
        try:
            d["cgroup_cpu_limit"] = open(p).read().strip(); break
        except OSError: pass
    return d

def gh_put(path, text):
    tok = os.environ.get("GH_TOKEN")
    if not tok: return False
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "Content-Type": "application/json", "User-Agent": "bench"}
    sha = None
    try:
        sha = json.load(urllib.request.urlopen(urllib.request.Request(f"{url}?ref={BRANCH}", headers=h)))["sha"]
    except Exception: pass
    body = {"message": f"bench: {path}", "branch": BRANCH, "content": base64.b64encode(text.encode()).decode()}
    if sha: body["sha"] = sha
    try:
        urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), h, method="PUT"), timeout=30)
    except Exception as e:
        print("push failed:", e, getattr(e, "read", lambda: b"")()[:300], flush=True)
        return False
    return True

def push():
    with lock:
        text = open(EV).read() if os.path.exists(EV) else ""
    gh_put(f"hf/{os.environ.get('RUN_LABEL', 'run')}-events.jsonl", text)

def log(kind, **kw):
    rec = {"t": time.time(), "kind": kind, "boot": boot_id(), "up_s": float(open("/proc/uptime").read().split()[0]), **kw}
    with lock:
        open(EV, "a").write(json.dumps(rec) + "\n")

def run_cell(seed, tag):
    s = time.time()
    if CELL_CMD:
        cmd = ["bash", "-c", CELL_CMD.format(seed=seed)]; cwd = LOGDIR
    else:
        cmd = [f"{VENV}/bin/python", "OSCAR_multi_ap_train.py", "--apStaCounts", "20,40", "--mode", "beb", "--seed", str(seed),
               "--simTime", "15", "--start_timesteps", "300"]; cwd = TRAIN
    with open(os.path.join(LOGDIR, f"{tag}-seed{seed}.log"), "w") as f:
        with start_lock:
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
            time.sleep(2.5)
        rc = proc.wait()
    log("cell", tag=tag, seed=seed, rc=rc, secs=round(time.time() - s, 1))

def scale(ns):
    for n in ns:
        tag, c0 = f"scale{n}", cpu_stats()
        log("scale_start", n=n, cpu=c0)
        ts = []
        for i in range(n):
            t = threading.Thread(target=run_cell, args=(1000 + n * 100 + i, tag)); t.start(); ts.append(t)
            time.sleep(3)  # output dirs are named to the second
        for t in ts: t.join()
        log("scale_end", n=n, cpu=cpu_stats()); push()

def soak(hours, k):
    end, seed, stop = time.time() + hours * 3600, [5000], threading.Event()
    log("soak_start", hours=hours, k=k, cpu=cpu_stats())
    def hb():
        while not stop.is_set():
            log("heartbeat", cpu=cpu_stats()); push(); stop.wait(60)
    threading.Thread(target=hb, daemon=True).start()
    def worker():
        while time.time() < end:
            with lock: seed[0] += 1; s = seed[0]
            run_cell(s, "soak")
    ts = []
    for _ in range(k):
        t = threading.Thread(target=worker); t.start(); ts.append(t); time.sleep(3)
    for t in ts: t.join()
    stop.set(); log("soak_end", cpu=cpu_stats()); push()

if __name__ == "__main__":
    log("boot_script", argv=sys.argv[1:])
    if sys.argv[1] == "pushtest":
        print("push ok" if gh_put(f"hf/pushtest-{int(time.time())}.txt", "ok\n") else "push NOT ok (no GH_TOKEN or bad token)")
    elif sys.argv[1] == "scale": scale([int(x) for x in sys.argv[2:]])
    elif sys.argv[1] == "soak": soak(float(sys.argv[2]), int(sys.argv[3]))
