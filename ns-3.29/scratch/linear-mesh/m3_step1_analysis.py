"""M3 step 1: per training seed, mean CW per AP over the policy window (after 300 steps) and the three eval seeds;
edge/middle ratio for 3-AP chains (gate G1). Usage: python m3_step1_analysis.py docs/figures/v4.0.0-step1"""
import os
import sys

import numpy as np

from summarize_run import summarize

root = sys.argv[1]
for nd in ("gaussian", "gumbel", "gumbel-raw"):
    for c in ("s4", "s2", "s5a"):
        for k in range(3):
            j = os.path.join(root, "s1-%s-%s-t%d" % (c, nd, k))
            if not os.path.isdir(j):
                continue
            cws = []
            for e in range(3):
                s = summarize(os.path.join(j, "eval%d" % e))
                cws.append([s["cw"][a][300:].mean() for a in s["aps"]])
            m = np.mean(cws, 0)
            ratio = " edge/mid %.2f" % ((m[0] + m[2]) / 2 / m[1]) if len(m) == 3 else ""
            print("%-10s %-4s t%d mean CW %s%s" % (nd, c, k, np.round(m, 1).tolist(), ratio))
