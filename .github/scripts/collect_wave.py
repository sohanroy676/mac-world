"""v4.1.0: collect the summaries of one wave batch from the release assets of the shard repositories.

  collect_wave.py <dispatch.json> --out docs/figures/<wave>/summaries.jsonl [--retry retry.json] [--local DIR]

Reads the packs file named in dispatch.json, reads the Spaces' <wave>/s<k>/*.summaries.jsonl from branch wave-results-s<k> of
their repositories ("hf" entries), downloads every summaries-*.jsonl asset of release
"wave-<wave>-s<k>" from shard k's repository (public, no token), or reads *.jsonl from --local DIR, and then:
  * keeps one PASS record per (job, command); two PASS records of the same job with different trace hashes are
    reported as HASH-MISMATCH and the job is dropped (non-learned runs must hash identically on every machine);
  * appends new records to --out (existing lines are kept, duplicates skipped);
  * lists jobs of the batch that have no PASS record and, with --retry, writes them as a batch for one more try.
Only summary lines go into the main repository; traces stay in the release tarballs of the shard repositories.
Exit code 0 = batch complete, 2 = jobs missing, 3 = hash mismatch.
"""
import argparse
import glob
import json
import os
import sys
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("dispatch")
ap.add_argument("--out", required=True)
ap.add_argument("--retry", default="")
ap.add_argument("--local", default="")
args = ap.parse_args()
cfg = json.load(open(args.dispatch))
packs = json.load(open(cfg["packs"]))
jobs = {j["id"]: j for s in packs["shards"] for p in s for j in p["jobs"]}


def get(url):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "collect-wave"}
    if os.environ.get("GH_TOKEN") and url.startswith("https://api.github.com/"):  # only against the API: a higher rate limit for public reads
        h["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=60).read()


lines = []
if args.local:
    for f in sorted(glob.glob(os.path.join(args.local, "*.jsonl"))):
        lines += open(f).read().splitlines()
else:
    for k, s in enumerate(cfg["shards"]):
        tag = "wave-%s-s%d" % (cfg["wave"], k)
        try:
            rel = json.loads(get("https://api.github.com/repos/%s/releases/tags/%s" % (s["repo"], tag)))
        except Exception as e:
            print("shard %d %s: no release %s (%s)" % (k, s["repo"], tag, getattr(e, "code", type(e).__name__)))
            continue
        for a in rel.get("assets", []):
            if a["name"].startswith("summaries-") and a["name"].endswith(".jsonl"):
                lines += get(a["browser_download_url"]).decode().splitlines()
        print("shard %d %s: release %s read" % (k, s["repo"], tag))
    for k, s in enumerate(cfg["shards"]):  # state of the fork runs, for diagnosis
        try:
            runs = json.loads(get("https://api.github.com/repos/%s/actions/workflows/wave-run.yml/runs?per_page=3" % s["repo"]))["workflow_runs"]
            print("shard %d %s runs: %s" % (k, s["repo"], ", ".join("%s %s/%s %s" % (r["id"], r["status"], r["conclusion"], r["created_at"]) for r in runs) or "none"))
        except Exception as e:
            print("shard %d %s runs: not readable (%s)" % (k, s["repo"], getattr(e, "code", type(e).__name__)))

if not args.local:
    for h in cfg.get("hf", []):  # Spaces push <wave>/s<shard>/<pack>.summaries.jsonl to branch wave-results of their owner's repository
        try:
            items = json.loads(get("https://api.github.com/repos/%s/contents/%s/s%d?ref=wave-results-s%d" % (h["repo"], cfg["wave"], h["shard"], h["shard"])))
        except Exception as e:
            print("space %s: nothing under %s/s%d in %s (%s)" % (h["space"], cfg["wave"], h["shard"], h["repo"], getattr(e, "code", type(e).__name__)))
            continue
        for it in items:
            if it["name"].endswith(".summaries.jsonl"):
                lines += get(it["download_url"]).decode().splitlines()
        print("space %s (%s): read" % (h["space"], h["repo"]))

have, mismatch = {}, set()
if os.path.exists(args.out):
    for l in open(args.out):
        r = json.loads(l)
        have[(r["job"], r["name"])] = r
new = []
for l in filter(None, lines):
    r = json.loads(l)
    key = (r["job"], r["name"])
    if r.get("check") != "PASS":
        continue
    if key in have:
        if have[key]["sha256"] != r["sha256"]:
            mismatch.add(r["job"])
        continue
    have[key] = r
    new.append(r)
if new:
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "a") as f:
        for r in new:
            if r["job"] not in mismatch:
                f.write(json.dumps(r, sort_keys=True) + "\n")
done = {j for (j, _) in have} - mismatch
missing = sorted(set(jobs) - done)
print("%d jobs in the batch, %d complete, %d new records, %d missing, %d hash mismatches %s" % (len(jobs), len(set(jobs) & done), len(new), len(missing), len(mismatch), sorted(mismatch)))
if args.retry and missing:
    json.dump({"jobs": [jobs[j] for j in missing]}, open(args.retry, "w"), indent=1)
    print("retry batch: %s (cut it with make_packs.py and list the shards in a different order)" % args.retry)
sys.exit(3 if mismatch else 2 if missing else 0)
