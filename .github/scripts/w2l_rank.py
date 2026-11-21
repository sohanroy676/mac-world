"""Wave 2l: learner evals on tournament seeds 300-309. Usage: w2l_rank.py summaries.jsonl"""
import json, re, sys, collections, statistics as st
sys.path.insert(0, 'ns-3.29/scratch/linear-mesh')
from gc_analysis import utility, feasible
CELL = {'s2': ([20, 40], [9.3, 17.19]), 's4': ([10, 10, 10], [24.44, 1.31, 24.44]), 's5a': ([10, 10, 10], [15.03, 11.25, 10.0])}
d = collections.defaultdict(dict)
for l in open(sys.argv[1]):
    r = json.loads(l)
    m = re.match(r'w2l-(s\w+?)-(rafa|global|pf)-t(\d+)-a(\d+)-h\d$', r['job'])
    if not m or not r['name'].startswith('eval'):
        continue
    c, lr, t, a = m.groups()
    d[(c, lr, int(t), int(a))][r['name']] = r['thr_all']
print('cell learner seed trainedAlpha n | U(0) U(1) U(4) at score alpha (mean) | feasible/n (score tol .05)')
for k in sorted(d):
    c, lr, t, a = k
    cnt, fl = CELL[c]
    th = list(d[k].values())
    us = {al: st.mean(utility(x, cnt, al) for x in th) for al in (0, 1, 4)}
    fe = sum(feasible(x, fl, 0.05) for x in th)
    print(c, lr, t, 'a%d' % a, len(th), ' '.join('%.2f' % us[al] for al in (0, 1, 4)), '%d/%d' % (fe, len(th)))
