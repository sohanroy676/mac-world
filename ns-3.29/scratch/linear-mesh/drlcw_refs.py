"""v3.8.0 (M2b): CSMA/BEB references for drlCW's reward (paper Eq. 2), from BEB trace.csv files.
Usage: python3 drlcw_refs.py trace1.csv [trace2.csv ...]
         prints --drlRefThp / --drlRefPer: per-AP mean goodput (Mbps) and packet-error ratio over the files.
       python3 drlcw_refs.py --delay out.csv trace1.csv [...]
         BEB runs made with --delayWindow 0.5: writes the mean-over-APs p95 delay (s) at each decision (every 50th step), averaged over the files.
Goodput = sum rx * PAYLOAD_BITS / (steps * step time); per = sum(tx - rx) / sum(tx), the repo's loss definition. Step time 0.01 s."""
import csv
import sys
from collections import defaultdict

PAYLOAD_BITS = (1500 - 20 - 8 - 8) * 8
STEP = 0.01
DECISION_STEPS = 50  # 0.5 s


def refs(paths, quiet=False):
    thp, per = defaultdict(list), defaultdict(list)
    for path in paths:
        rx, tx, steps = defaultdict(float), defaultdict(float), defaultdict(int)
        for r in csv.DictReader(open(path)):
            a = int(r["ap"])
            rx[a] += float(r["rx"])
            tx[a] += float(r["tx"])
            steps[a] += 1
        for a in rx:
            thp[a].append(rx[a] * PAYLOAD_BITS / (steps[a] * STEP * 1e6))
            per[a].append((tx[a] - rx[a]) / tx[a] if tx[a] else 0.0)
    aps = sorted(thp)
    t = [sum(thp[a]) / len(thp[a]) for a in aps]
    pe = [sum(per[a]) / len(per[a]) for a in aps]
    if quiet:
        return t, pe
    print("--drlRefThp", ",".join("%.3f" % (sum(thp[a]) / len(thp[a])) for a in aps),
          "--drlRefPer", ",".join("%.4f" % (sum(per[a]) / len(per[a])) for a in aps))


def delay_ref(out, paths, quiet=False):
    per_file = []
    for path in paths:
        by_step = defaultdict(list)
        for r in csv.DictReader(open(path)):
            by_step[int(r["step"])].append(float(r["dp95"]))
        # the trainer decides at steps 50, 100, ... and reads the value held at that step (cw.cc window ends one step earlier)
        per_file.append([sum(v) / len(v) / 1000.0 for s, v in sorted(by_step.items()) if s % DECISION_STEPS == 0])
    n = min(len(p) for p in per_file)
    mean = [sum(p[k] for p in per_file) / len(per_file) for k in range(n)]
    if out:
        open(out, "w").write(",".join("%.6f" % v for v in mean))
    if quiet:
        return mean
    print("wrote %d decision delays (first %.3f s, last %.3f s) to %s" % (n, mean[0], mean[-1], out))


if __name__ == "__main__":
    if sys.argv[1] == "--write":
        import json
        import os
        os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
        t, pe = refs(sys.argv[3:], quiet=True)
        json.dump({"thp": t, "per": pe, "delay": delay_ref("", sys.argv[3:], quiet=True)}, open(sys.argv[2], "w"))
        print("wrote %s: thp %s per %s, %d decision delays" % (sys.argv[2], t, pe, len(json.load(open(sys.argv[2]))["delay"])))
    elif sys.argv[1] == "--delay":
        delay_ref(sys.argv[2], sys.argv[3:])
    else:
        refs(sys.argv[1:])
