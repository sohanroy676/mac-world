"""Wave worker for a Hugging Face Space (v4.1.0). Started by tools/hf/app.py when the Space variable WAVE_WORKER=1.

What it does, in a loop (docs/reference/wave-runbook-v4.1.0.md, section 5):
  1. Read .github/waves/dispatch.json from the upstream repository (public, no token). A batch is new when the
     SHA-256 of that file differs from the last batch this Space finished.
  2. Find this Space in dispatch.json "hf": [{"space": "owner/name", "repo": "owner/fork", "shard": k}, ...]
     (the Space's own name comes from the SPACE_ID variable that Hugging Face sets). No entry = nothing to do.
  3. Check the lab-hour cap of the batch (same rule as dispatch_wave.py), check out the code, build it when the commit
     changed (tools/bench/run_bench.sh hf --no-apt --smoke), and run the packs of shard k.
  4. After every pack, push its summaries to the GitHub repository named in its "repo" entry (the main repository), branch wave-results-s<k>,
     path <wave>/s<k>/<pack>.summaries.jsonl, with the token in the Space secret GH_TOKEN (fine-grained, that repo only,
     Contents read and write). Traces stay on the Space's disk, which is ephemeral; only the SHA-256 of each trace is kept.
  5. A restarted Space skips packs whose summaries file already lists every job as PASS.

Environment: UPSTREAM (default sohanroy676/mac-world), REF (branch holding dispatch.json), SPACE_ID, GH_TOKEN, LANES (16),
POLL (seconds between looks at dispatch.json, 300), SRC (clone directory), BENCH_VENV.
Test switches: UPSTREAM_DIR (read dispatch.json and packs from a local checkout), RESULT_LOCAL (write results to a folder
instead of GitHub), SKIP_BUILD=1, ONCE=1 (one pass, then exit).
"""
import base64
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

UPSTREAM = os.environ.get("UPSTREAM", "sohanroy676/mac-world")
REF = os.environ.get("REF", "claude/project-thread-o7nshg")
SPACE = os.environ.get("SPACE_ID", "").lower()
LANES = int(os.environ.get("LANES", "16"))
POLL = int(os.environ.get("POLL", "300"))
SRC = os.environ.get("SRC", "/tmp/jobs/mac-world")
VENV = os.environ.get("BENCH_VENV", os.path.expanduser("~/venv37"))
UPSTREAM_DIR = os.environ.get("UPSTREAM_DIR", "")
RESULT_LOCAL = os.environ.get("RESULT_LOCAL", "")
BRANCH = "wave-results"  # set per shard in one_pass: wave-results-s<k>, so ten Spaces never commit to one branch at once
UA = {"User-Agent": "wave-worker"}
push_lock = threading.Lock()  # GitHub rejects concurrent commits to one branch (HTTP 409)
branch_ready = set()


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fetch_upstream(path):
    if UPSTREAM_DIR:
        return open(os.path.join(UPSTREAM_DIR, path), "rb").read()
    url = "https://raw.githubusercontent.com/%s/%s/%s" % (UPSTREAM, REF, path)
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def api(repo, path, data=None, method="GET", ref=None):
    h = dict(UA, Accept="application/vnd.github+json", **{"Content-Type": "application/json"})
    if os.environ.get("GH_TOKEN"):
        h["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    url = "%s/repos/%s/%s" % (os.environ.get("GITHUB_API", "https://api.github.com"), repo, path) + ("?ref=" + ref if ref else "")
    req = urllib.request.Request(url, json.dumps(data).encode() if data is not None else None, h, method=method)
    return json.load(urllib.request.urlopen(req, timeout=60))


def ensure_branch(repo):
    """wave-results must exist before files can be committed to it; branch it from the repository's default branch."""
    if (repo, BRANCH) in branch_ready:
        return
    try:
        api(repo, "branches/" + BRANCH)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        default = api(repo, "")["default_branch"]
        sha = api(repo, "git/ref/heads/" + default)["object"]["sha"]
        api(repo, "git/refs", {"ref": "refs/heads/" + BRANCH, "sha": sha}, "POST")
    branch_ready.add((repo, BRANCH))


def read_result(repo, path):
    if RESULT_LOCAL:
        p = os.path.join(RESULT_LOCAL, path)
        return open(p, "rb").read() if os.path.exists(p) else None
    try:
        return base64.b64decode(api(repo, "contents/" + path, ref=BRANCH)["content"])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def write_result(repo, path, blob):
    if RESULT_LOCAL:
        p = os.path.join(RESULT_LOCAL, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(blob)
        return True
    with push_lock:
        for attempt in range(4):
            try:
                ensure_branch(repo)
                sha = None
                try:
                    sha = api(repo, "contents/" + path, ref=BRANCH)["sha"]
                except urllib.error.HTTPError as e:
                    if e.code != 404:
                        raise
                body = {"message": "wave: " + path, "branch": BRANCH, "content": base64.b64encode(blob).decode()}
                if sha:
                    body["sha"] = sha
                api(repo, "contents/" + path, body, "PUT")
                return True
            except Exception as e:
                log("push failed (try %d): %s" % (attempt + 1, e))
                time.sleep(5 * (attempt + 1))
    return False


def sh(cmd, **kw):
    return subprocess.run(["bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw).stdout.decode("utf-8", "replace")


def checkout(code_commit):
    """Clone or update SRC and build it when the commit changed. Returns the commit that is built."""
    if not UPSTREAM_DIR:
        if not os.path.isdir(SRC + "/.git"):
            os.makedirs(os.path.dirname(SRC), exist_ok=True)
            log(sh("git clone -q -b %s https://github.com/%s.git %s" % (REF, UPSTREAM, SRC)))
        log(sh("cd %s && git fetch -q origin %s && git checkout -q %s" % (SRC, REF, code_commit or "FETCH_HEAD")))
    head = sh("cd %s && git rev-parse HEAD" % SRC).strip()
    built = os.path.join(SRC, ".built-commit")
    if os.environ.get("SKIP_BUILD") != "1" and (not os.path.exists(built) or open(built).read().strip() != head):
        log("building commit", head)
        out = sh("cd %s && bash tools/bench/run_bench.sh hf --no-apt --smoke" % SRC)
        log(out[-1500:])
        if "RESULT: PASS" not in out and "Single cell exit code: 0" not in out:
            raise RuntimeError("build or smoke run failed")
        open(built, "w").write(head)
    return head


def run_pack(d, shard, pack, head, repo):
    pid = pack["id"]
    base = "%s/s%d/%s" % (d["wave"], shard, pid)
    want = {j["id"] for j in pack["jobs"]}
    old = read_result(repo, base + ".summaries.jsonl")
    if old and want <= {json.loads(l)["job"] for l in old.decode().splitlines() if l and json.loads(l).get("check") == "PASS"}:
        log("pack", pid, "already done, skipped")
        return True
    out = "/tmp/jobs/out/%s-%s" % (d["wave"], pid)
    sh("rm -rf %s; mkdir -p %s" % (out, out))
    env = dict(os.environ, PACK=json.dumps(pack["jobs"]), NO_BUNDLE="1", MACWORLD_COMMIT=head, MACWORLD_IMAGE="hf-space:%s@%s" % (SPACE, head[:12]))
    t0 = time.time()
    rc = subprocess.call([VENV + "/bin/python", os.path.join(SRC, ".github/scripts/run_pack.py"), VENV + "/bin/python", "%s-s%d-%s" % (d["wave"], shard, pid), out, str(d.get("hf_lanes", d["_lanes"]))],
                         cwd=os.path.join(SRC, "ns-3.29/scratch/linear-mesh"), env=env, stdout=open(out + ".log", "w"), stderr=subprocess.STDOUT)
    lines = []
    for j in sorted(os.listdir(out)):
        for c in sorted(os.listdir(os.path.join(out, j))) if os.path.isdir(os.path.join(out, j)) else []:
            f = os.path.join(out, j, c, "summary.json")
            if os.path.exists(f):
                lines.append(json.dumps(json.load(open(f)), sort_keys=True))
    ok = write_result(repo, base + ".summaries.jsonl", ("\n".join(lines) + "\n").encode() if lines else b"")
    write_result(repo, base + ".pack.txt", ("exit %d, %d s, %d of %d jobs with a summary, space %s, commit %s\n" % (rc, time.time() - t0, len(lines), len(want), SPACE, head)).encode())
    log("pack", pid, "exit", rc, "%d/%d summaries" % (len(lines), len(want)), "pushed" if ok else "PUSH FAILED")
    return rc == 0 and ok


def lab_hours(packs):
    return sum(j["w"] for s in packs["shards"] for p in s for j in p["jobs"]) / 33.0 * 0.2


def one_pass(last):
    raw = fetch_upstream(".github/waves/dispatch.json")
    bid = hashlib.sha256(raw).hexdigest()[:12]
    if bid == last:
        return last
    d = json.loads(raw)
    mine = [h for h in d.get("hf", []) if h["space"].lower() == SPACE]
    if not mine:
        log("batch", bid, "has no entry for", SPACE)
        return bid
    h = mine[0]
    packs = json.loads(fetch_upstream(d["packs"]))
    d["_lanes"] = packs["lanes"]
    total = d.get("spent_lab_h", 0) + lab_hours(packs)
    if total > d["cap_lab_h"]:
        log("REFUSED batch", bid, ": %.1f lab-h would pass the cap %.1f" % (total, d["cap_lab_h"]))
        return bid
    global BRANCH
    shard, repo = h["shard"], h["repo"]
    BRANCH = "wave-results-s%d" % shard
    my = packs["shards"][shard]
    for pack in my:
        for j in pack["jobs"]:
            j.setdefault("timeout", int(70 * j["w"] + 300))
    log("batch", bid, "wave", d["wave"], "shard", shard, "-", len(my), "packs, results to", repo)
    head = checkout(d.get("code_commit", ""))
    per_pack = max(1, packs["lanes"])
    ok = True
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, LANES // per_pack)) as ex:
        for r in ex.map(lambda p: run_pack(d, shard, p, head, repo), my):
            ok = ok and r
    write_result(repo, "%s/s%d/done-%s.txt" % (d["wave"], shard, bid), ("%s %s\n" % ("ok" if ok else "with failures", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))).encode())
    log("batch", bid, "finished", "ok" if ok else "with failures")
    return bid


def main():
    assert SPACE or UPSTREAM_DIR, "SPACE_ID is not set (Hugging Face sets it inside a Space)"
    last = ""
    while True:
        try:
            last = one_pass(last)
        except Exception as e:
            log("pass failed:", type(e).__name__, e)
        if os.environ.get("ONCE") == "1":
            return
        time.sleep(POLL)


if __name__ == "__main__":
    sys.exit(main())
