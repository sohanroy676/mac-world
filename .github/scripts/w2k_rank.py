"""Rank class B stage-1 training seeds (Wave 2k+2k2). Usage: w2k_rank.py a.jsonl b.jsonl ..."""
import json, re, sys, collections, statistics as st
sys.path.insert(0, 'ns-3.29/scratch/linear-mesh')
from gc_analysis import utility, feasible
CELL = {'s2': ([20, 40], [9.3, 17.19]), 's4': ([10, 10, 10], [24.44, 1.31, 24.44]),
        's5a': ([10, 10, 10], [15.03, 11.25, 10.0])}
rows = collections.defaultdict(list)
for f in sys.argv[1:]:
    for l in open(f):
        r = json.loads(l)
        m = re.match(r'w2k-(s\w+?)-(rafa|global|pf)-t(\d+)$', r['job'])
        if not r['name'].startswith('eval') or not m:
            continue
        c, lr, t = m.groups()
        cnt, fl = CELL[c]
        rows[(c, lr, int(t))].append((utility(r['thr_all'], cnt, 1.0), feasible(r['thr_all'], fl, 0.05), sum(r['thr_all'])))
out = collections.defaultdict(list)
for (c, lr, t), v in rows.items():
    out[(c, lr)].append((st.mean(x[0] for x in v), all(x[1] for x in v), st.mean(x[2] for x in v), t, len(v)))
print('cell learner seeds(n) all3feas bestU1 (seed) top3 medianU1 | sumthr of best')
for k in sorted(out):
    s = sorted(out[k], key=lambda z: (not z[1], -z[0]))
    ok = [z for z in s if z[1]]
    print(k[0], k[1], len(s), len(ok), '%.2f' % s[0][0], s[0][3], [z[3] for z in s[:3]],
          '%.2f' % st.median(z[0] for z in s), '%.2f' % s[0][2], 'incomplete:%d' % sum(z[4] < 3 for z in s))
