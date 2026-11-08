# Actions vs lab: platform comparability check, 2026-11-08

Run [42506831440](https://github.com/sohanroy676/mac-world/actions/runs/42506831440) (workflow `run-jobs`, commit ab94a80 on `feature/v4`), 5 jobs on hosted `ubuntu-24.04` runners in an `ubuntu:22.04` container, clean ns-3 build per job, Python 3.7.17, torch 1.13.1+cpu. Repo is public (fact: GitHub API `private: false`).

## Results (fact)
| Job (seed 100, 30 s, `--check`) | Check | `cmp` of `trace.csv` with committed lab run | Job time | CPU |
|---|---|---|---|---|
| S4 BEB (`10,10,10 --apHidden 1-3`, load 10, norm 150) | PASS | **IDENTICAL** (lab `results/multi-ap-20261103-010425`) | 518 s | EPYC 9V74 |
| S2 static 512,512 (`20,40`) | PASS | **IDENTICAL** (lab `...20261103-075331`) | 469 s | EPYC 9V74 |
| S4 IdleSense | PASS | **IDENTICAL** (lab `...20261103-012104`) | 498 s | EPYC 7763 |
| `2,3` reference command, run a | PASS | no lab trace in the repo | 32 s | EPYC 9V74 |
| `2,3` reference command, run b | PASS | same SHA-256 as run a | 33 s | EPYC 9V74 |

`2,3` trace SHA-256 on Actions (both runs): `044cf770fe0cd1d0bb94b6382e6719697e50a29b1d1487aa0e1b10f5a4a31958`. The lab reference `results/multi-ap-20261028-083001` is not committed, so it could not be compared: run `sha256sum` on it and compare (open item).

## Conclusions
- Fact: non-learned runs (BEB, static, IdleSense) on Actions are byte-identical to the lab traces, so per-AP throughput is identical too. Identical results on two different CPU models (EPYC 9V74 and 7763) also show the result does not depend on the host CPU.
- Inference: Actions runs of non-learned modes can be mixed with lab runs in the paired design (BEB, statics, IdleSense, M2 KW/UCB seeds 100-109), pending the `2,3` lab hash. Not yet checked: learner (torch) runs, which are the CUDA-vs-CPU question in M3 step 0.
- Timing: about the same as the lab (S4 30 s: 518 s vs lab 7-9 min at 2 lanes); the gain is parallel jobs. Build plus setup was about 6 min per job.

## Harness
`.github/workflows/run-jobs.yml` runs a job list (`.github/jobs/current.json`, `{id, args, ref?}`) as one matrix job each, on push to `feature/v4*` touching that file. Each job runs `--check`, copies `config.json` + `trace.csv` + log to an artifact (7 days), and `cmp`s with `ref` if given. Artifact blobs are not reachable from the agent container (proxy), so results are read from job logs; run dirs have to be committed from a workflow or by hand.
