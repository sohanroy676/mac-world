"""v3.8.0 (M2b): CSMA/BEB reference per-AP goodput (Mbps) and packet-error ratio for drlCW's reward (paper Eq. 2), from BEB trace.csv files.
Usage: python3 drlcw_refs.py trace1.csv [trace2.csv ...]   (means over the files; prints the two flag values)
Goodput = sum rx * PAYLOAD_BITS / (steps * step time); per = sum(tx - rx) / sum(tx), the repo's loss definition. Step time 0.01 s."""
import csv
import sys
from collections import defaultdict

PAYLOAD_BITS = (1500 - 20 - 8 - 8) * 8
STEP = 0.01
thp, per = defaultdict(list), defaultdict(list)
for path in sys.argv[1:]:
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
print("--drlRefThp", ",".join("%.3f" % (sum(thp[a]) / len(thp[a])) for a in aps), "--drlRefPer", ",".join("%.4f" % (sum(per[a]) / len(per[a])) for a in aps))
