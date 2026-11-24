#!/usr/bin/env python3
"""v4.1.0: check a --cwGateC run trace. usage: gatec_probe_v4_1_0.py <run dir> [period steps]. Fails (exit 1) unless every cw_set is 2^k-1 and per AP changes only at steps that are multiples of the period."""
import csv
import os
import sys

run, period = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10
rows = list(csv.DictReader(open(os.path.join(run, "trace.csv"))))
by_ap = {}
for r in rows:
    by_ap.setdefault(r["ap"], []).append((int(r["step"]), int(float(r["cw_set"]))))
bad_k, bad_change, changes = 0, 0, 0
for ap, seq in by_ap.items():
    seq.sort()
    prev = None
    for step, cw in seq:
        if (cw + 1) & cw:
            bad_k += 1
        if prev is not None and cw != prev:
            changes += 1
            if step % period != 0 and (step - 1) % period != 0:  # trace logs the CW after the action of this step or the previous one
                bad_change += 1
        prev = cw
print("gatec probe: aps %d, rows %d, not 2^k-1: %d, changes %d, changes off the period: %d" % (len(by_ap), len(rows), bad_k, changes, bad_change))
sys.exit(1 if bad_k or bad_change else 0)
