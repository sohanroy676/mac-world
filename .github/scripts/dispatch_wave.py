"""v4.1.0: start one batch of a wave, one wave-run.yml dispatch per shard. Usage: dispatch_wave.py <dispatch.json> <this repo> <this commit>

dispatch.json = {"wave": "w0", "packs": ".github/waves/w0-r0-packs.json", "image": "ghcr.io/..@sha256:..",
                 "max_parallel": 5, "cap_lab_h": 30, "spent_lab_h": 0,
                 "shards": [{"repo": "owner/mac-world", "token": 0, "ref": "branch with wave-run.yml"}, ...]}
Shard k of the packs file goes to shards[k]; the Spaces listed under "hf": [{"space", "repo", "shard"}] take the shards after the
forks and start themselves (tools/hf/wave_worker.py reads this same file), so only the cap is checked for them here. "token": n reads env FORK_TOKEN_n; a shard on this repository uses
SELF_TOKEN. Refuses to start when the batch would take the wave over its approved lab-hour cap (a run of w = 33
counts 0.2 lab-h, the plan's unit), when the image has no digest, or when a token is missing. Tokens are never printed.
"""
import json
import os
import sys
import urllib.request

cfg = json.load(open(sys.argv[1]))
repo, sha = sys.argv[2], sys.argv[3]
packs = json.load(open(cfg["packs"]))
n_gh = len(cfg["shards"])
assert sorted(h["shard"] for h in cfg.get("hf", [])) == list(range(n_gh, n_gh + len(cfg.get("hf", [])))), "hf shards must be numbered n_forks, n_forks+1, ..."
assert len(packs["shards"]) == n_gh + len(cfg.get("hf", [])), "packs file has %d shards, dispatch.json %d forks + %d Spaces" % (len(packs["shards"]), n_gh, len(cfg.get("hf", [])))
assert "@sha256:" in cfg["image"], "image must be pinned by digest"
lab_h = sum(j["w"] for s in packs["shards"] for p in s for j in p["jobs"]) / 33.0 * 0.2
total = cfg.get("spent_lab_h", 0) + lab_h
print("wave %s: this batch %.1f lab-h, wave total %.1f of cap %.1f" % (cfg["wave"], lab_h, total, cfg["cap_lab_h"]))
if total > cfg["cap_lab_h"]:
    sys.exit("REFUSED: over the approved lab-hour cap")
todo = []
for k, s in enumerate(cfg["shards"]):
    if not packs["shards"][k]:
        continue
    tok = os.environ.get("SELF_TOKEN" if s["repo"].lower() == repo.lower() else "FORK_TOKEN_%d" % s["token"], "")
    if not tok:
        sys.exit("REFUSED: no token for shard %d (%s)" % (k, s["repo"]))
    todo.append((k, s, tok))
failed = 0
for k, s, tok in todo:
    body = {"ref": s["ref"], "inputs": {"upstream": repo, "commit": sha, "packs": cfg["packs"], "shard": str(k), "image": cfg["image"],
                                        "wave": cfg["wave"], "max_parallel": str(cfg.get("max_parallel", 5))}}
    req = urllib.request.Request("https://api.github.com/repos/%s/actions/workflows/wave-run.yml/dispatches" % s["repo"], data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=30)
        print("shard %d -> %s: started (%d packs)" % (k, s["repo"], len(packs["shards"][k])))
    except Exception as e:  # report and go on: the collector re-queues what is missing
        failed += 1
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:300].replace("\n", " ")  # GitHub's message (never contains the token)
        except Exception:
            pass
        print("shard %d -> %s: FAILED %s %s" % (k, s["repo"], getattr(e, "code", type(e).__name__), body))
sys.exit(1 if failed else 0)
