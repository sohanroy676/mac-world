"""v4.1.0 (max-CW plan, Track A): frame times and Tc from a cw.cc --phyDurations log.

  cd ns-3.29 && ./waf --run "scratch/linear-mesh/linear-mesh --apStaCounts=20,40 --dryRun=true --disableGym=true \
      --offeredLoad=10 --simTime=5 --seed=1 --phyDurations=true" > phy.log 2>&1
  python scratch/linear-mesh/phy_times_v4_1_0.py phy.log

Reads the "PHYDUR <key> <microseconds> <count>" lines (AP 1's radio) and reports, with the counts behind each value:
  T_data  = most frequent RX_OK duration (the data frame)
  T_ack   = most frequent TX duration (the AP's ACK)
  SIFS    = most frequent IDLE_AFTER_RX_OK gap
  AIFS    = most frequent IDLE_AFTER_TX gap (the gap with zero backoff slots; longer gaps add 9 us per slot)
  gap_c   = most frequent idle gap after a failed reception (IDLE_AFTER_RX_ERR and IDLE_AFTER_CCA_BUSY together: ns-3
            logs a zero-length CCA_BUSY record after most failed receptions). The five most frequent gaps are printed
            so the choice can be checked by eye: they must rise in steps of one slot from gap_c.
  Ts = T_data + SIFS + T_ack + AIFS   one successful exchange with zero backoff slots
  Tc = T_data + gap_c                 one collision until the first slot in which a station may transmit again
  C  = payload bits / Ts              capacity for the scheduled-access bound (bounds_v4_1_0.py --caps)
Both Ts and Tc include the idle time before the first backoff slot (Bianchi's convention).
"""
import sys
from collections import defaultdict

from multi_ap import PAYLOAD_BITS

hist = defaultdict(dict)
for line in open(sys.argv[1], errors="replace"):
    p = line.split()
    if len(p) == 4 and p[0] == "PHYDUR":
        hist[p[1]][int(p[2])] = int(p[3])
assert hist, "no PHYDUR lines: run cw.cc with --phyDurations=true"
mode = lambda k: max(hist[k].items(), key=lambda kv: kv[1])


t_data, t_ack, sifs = mode("RX_OK"), mode("TX"), mode("IDLE_AFTER_RX_OK")
aifs = mode("IDLE_AFTER_TX")
after_err = defaultdict(int)  # an RX_ERR is followed by IDLE directly, or by a CCA_BUSY record and then IDLE
for k in ("IDLE_AFTER_RX_ERR", "IDLE_AFTER_CCA_BUSY"):
    for us, c in hist.get(k, {}).items():
        after_err[us] += c
gap_c = max(after_err.items(), key=lambda kv: kv[1])
ts = t_data[0] + sifs[0] + t_ack[0] + aifs[0]
tc = t_data[0] + gap_c[0]
print("| Quantity | us | Count |\n|---|---|---|")
for name, (us, c) in (("T_data", t_data), ("T_ack", t_ack), ("SIFS", sifs), ("AIFS", aifs), ("gap after collision", gap_c)):
    print("| %s | %d | %d |" % (name, us, c))
print("| failed receptions of length T_data | %d | %d |" % (t_data[0], hist.get("RX_ERR", {}).get(t_data[0], 0)))
print("\nmost frequent idle gaps after a failed reception (us: count): " + ", ".join("%d: %d" % kv for kv in sorted(after_err.items(), key=lambda kv: -kv[1])[:5]))
print("Ts = %d us, Tc = %d us, C = %.2f Mbps (payload %d bits)" % (ts, tc, PAYLOAD_BITS / ts, PAYLOAD_BITS))
