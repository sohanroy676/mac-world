# Wave 2l: class B stage 2 on tournament seeds 300-309 (v4.1.0)

- Top-3 seeds per learner and cell (Wave 2k ranking) frozen and evaluated for 60 s on seeds 300-309. RAFA best seed also evaluated with alpha input 0 and 4.
- 61 of 66 jobs done (305 evals); 5 jobs lost with pack 1 (330 min timeout) and rerun as Wave 2l2. Rows with n=5 are missing their second half until 2l2 lands.
- Script `.github/scripts/w2l_rank.py`. Columns: U(0) = sum goodput, U(1) = proportional fair, U(4) = alpha-4 utility, all scored on the same 60 s eval, mean over seeds. "feasible" = meets BEB floors within 0.05.
- Not yet compared with BEB or the measured ceilings on these seeds: that comes with the tournament baselines (Wave 3). No ranking claims below beyond what the table shows.

```
cell learner seed trainedAlpha n | U(0) U(1) U(4) at score alpha (mean) | feasible/n (score tol .05)
s2 global 2003 a1 5 39.64 -26.07 -108.57 4/5
s2 global 2004 a1 10 39.63 -25.64 -91.86 9/10
s2 global 2005 a1 10 39.64 -25.61 -91.67 9/10
s2 pf 2006 a1 10 39.57 -26.45 -90.23 10/10
s2 pf 2007 a1 10 39.62 -28.38 -118.95 10/10
s2 pf 2011 a1 10 39.53 -28.56 -120.34 10/10
s2 rafa 2000 a1 10 36.25 -30.99 -124.05 8/10
s2 rafa 2002 a1 5 36.17 -31.61 -151.47 4/5
s2 rafa 2011 a0 10 36.26 -30.97 -123.67 8/10
s2 rafa 2011 a1 10 36.26 -30.96 -123.40 8/10
s2 rafa 2011 a4 10 36.27 -30.96 -122.97 8/10
s4 global 2002 a1 10 76.60 12.80 -216.84 10/10
s4 global 2007 a1 10 76.62 12.84 -214.11 10/10
s4 global 2008 a1 10 75.75 15.16 -86.58 10/10
s4 pf 2001 a1 5 61.93 20.13 -2.35 4/5
s4 pf 2003 a1 10 64.79 20.18 -3.79 10/10
s4 pf 2004 a1 10 65.58 20.11 -4.36 10/10
s4 rafa 2001 a0 10 65.52 8.21 -293.69 10/10
s4 rafa 2001 a1 10 64.98 20.52 -3.29 10/10
s4 rafa 2001 a4 10 60.43 16.88 -8.47 10/10
s4 rafa 2005 a1 10 66.99 20.21 -5.01 10/10
s4 rafa 2011 a1 5 66.21 19.81 -5.25 5/5
s5a global 2001 a1 10 49.81 13.25 -4.47 10/10
s5a global 2003 a1 10 49.80 13.24 -4.48 10/10
s5a global 2009 a1 10 49.81 13.25 -4.47 10/10
s5a pf 2002 a1 10 49.01 13.32 -4.26 10/10
s5a pf 2003 a1 10 49.36 13.49 -4.24 10/10
s5a pf 2007 a1 10 49.48 13.57 -4.21 10/10
s5a rafa 2007 a0 5 49.55 13.30 -4.38 5/5
s5a rafa 2007 a1 10 49.35 13.23 -4.38 10/10
s5a rafa 2007 a4 10 48.08 12.61 -4.46 10/10
s5a rafa 2008 a1 10 49.70 13.17 -4.49 10/10
s5a rafa 2010 a1 10 49.71 13.21 -4.47 10/10
```

## Reading (preliminary, learners only)
- S2: Global, PF and RAFA all stay within about 5 U(1) of each other (-26 to -31); Global is best on U(1) and U(0). RAFA is below on throughput (36.3 vs 39.6) and feasible on 8 of 10 seeds, the others 9-10 of 10.
- S4: PF and RAFA tie at U(1) about 20.1-20.5 and beat Global (12.8-15.2); Global is best at U(0) (76.6) but PF/RAFA are far better at U(4) (about -3 to -5 against -87 to -217).
- S5a: all learners tie at U(1) about 13.2-13.6.
- RAFA alpha conditioning: alpha 0 and 4 do not beat the alpha 1 model scored at those alphas (S4 alpha 4: -8.5 vs -3.3; S4 alpha 0: 65.5 vs Global 76.6). So the alpha input is not delivering a per-alpha gain here.
- Global and PF actors do not take alpha; they are scored at all three alphas from the same eval.
