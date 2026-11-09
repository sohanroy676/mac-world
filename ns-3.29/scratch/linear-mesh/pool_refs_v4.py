"""M3 step 0: per-AP BEB throughput of the 24 pool configs rerun at 10 Mbps per STA (+ --rewardNorm 150), next to the
v3.5.0 references (150 Mbps per STA). Usage: python pool_refs_v4.py <bundle_dir> <old_csv> <out_csv>"""
import csv
import glob
import json
import os
import sys

from gc_analysis import floors
from summarize_run import summarize

bundles, old_csv, out_csv = sys.argv[1:4]
old = {int(r["k"]): r for r in csv.DictReader(open(old_csv))}
rows = []
for d in sorted(glob.glob(os.path.join(bundles, "pool10-*"))):
    k = int(os.path.basename(d).split("-")[1])
    cfg = json.load(open(os.path.join(d, "config.json")))
    s = summarize(d)
    thr = [s["thr_policy"][a] for a in s["aps"]]
    counts = cfg["counts"]
    fl = floors(thr, counts)
    o = old[k]
    othr = [float(x) for x in (o["ap1"], o["ap2"], o["ap3_or_blank"]) if x != ""]
    rows.append({"k": k, "name": o["name"], "apStaCounts": cfg["apStaCounts"], "seed": cfg["seed"],
                 "offeredLoad": cfg["offeredLoad"], "rewardNorm": cfg["rewardNorm"],
                 "agg_mbps": round(sum(thr), 2), "per_ap_mbps": ";".join("%.2f" % x for x in thr),
                 "floors_mbps": ";".join("%.2f" % x for x in fl),
                 "old_per_ap_mbps_150": ";".join("%.2f" % x for x in othr),
                 "max_rel_diff_vs_150": round(max(abs(a - b) / max(b, 1e-9) for a, b in zip(thr, othr)), 3)})
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["k"], r["name"], r["per_ap_mbps"], "| old", r["old_per_ap_mbps_150"], "| maxrel", r["max_rel_diff_vs_150"])
