# Wave 2k: class B stage 1 (v4.1.0)

- 108 learner jobs (12 training seeds 2000-2011 x RAFA/Global/PF x S2/S4/S5a); each trained, then evaluated 60 s on seeds 0-2 at alpha 1.
- Run in two parts: Wave 2k (82 of 108 done; 26 lost to the 120 min pack limit) and Wave 2k2 (the 26 reruns, timeout 330 min). All 108 complete, 0 hash mismatches, 432 records.
- The release publish failed once (403) for 2k and worked for 2k2. Cause unknown. Actors are on branch `wave-actors` (2k) and 2k2 collected the same way.
- Ranking script: `.github/scripts/w2k_rank.py`. Score = mean over the 3 eval seeds of station-weighted alpha-fair U1; "all-3-feasible" = feasible (tol 0.05) vs the BEB floors on all 3.

```
cell learner seeds(n) all3feas bestU1 (seed) top3 medianU1 | sumthr of best
s2 global 12 12 -25.27 2003 [2003, 2005, 2004] -27.32 39.45 incomplete:0
s2 pf 12 3 -27.53 2006 [2006, 2007, 2011] -36.10 39.42 incomplete:0
s2 rafa 12 12 -30.75 2011 [2011, 2000, 2002] -30.80 36.01 incomplete:0
s4 global 12 12 14.98 2008 [2008, 2007, 2002] 11.88 75.83 incomplete:0
s4 pf 12 10 20.16 2003 [2003, 2004, 2001] 19.74 65.01 incomplete:0
s4 rafa 12 11 20.50 2001 [2001, 2005, 2011] 17.89 65.15 incomplete:0
s5a global 12 12 13.04 2001 [2001, 2003, 2009] 13.01 49.84 incomplete:0
s5a pf 12 12 13.56 2007 [2007, 2003, 2002] 13.05 49.56 incomplete:0
s5a rafa 12 12 13.01 2007 [2007, 2010, 2008] 12.72 49.24 incomplete:0
```

## Reading
- S2: Global is best (U1 -25.27) and feasible for all 12 seeds; RAFA is feasible for all 12 but lower (-30.75); PF is feasible for only 3 of 12.
- S4: RAFA best (20.50, 11/12 feasible), PF close (20.16, 10/12), Global lower (14.98, 12/12).
- S5a: all three tie near 13.0-13.6.
- Seed choice used eval seeds 0-2, so the best-seed numbers are optimistic. Stage 2 re-evaluates the best seed and the top 3 on fresh tournament seeds 300-309.
- Not yet compared to the measured ceilings; that happens in the tournament analysis.
