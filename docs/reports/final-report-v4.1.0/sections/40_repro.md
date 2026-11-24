## 10. Reproducibility

- **Repository:** `sohanroy676/mac-world`. Version v4.1.0 is tagged on `feature/v4`. This report, its scripts and its figures are in `docs/reports/final-report-v4.1.0/`.
- **Code:** `ns-3.29/scratch/linear-mesh/` (project code: `cw.cc`, the trainer `OSCAR_multi_ap_train.py`, controllers in `ap_controllers.py` and `ap_layered_v4_1_0.py`, analysis scripts such as `ceilings_v4_1_0.py`, `tournament_v4_1_0.py` and `confirm_v4_1_0.py`). Upstream ns-3.29 and ns3-gym are used unchanged.
- **Runs:** every run is a job in `.github/waves/`; the batch generators are in `.github/scripts/` (`w3a_batch.py` for the tournament, `rep_batch.py` and `rep_select.py` for the report cells). Jobs run in a pinned container image on GitHub Actions; each result stores the SHA-256 of its trace, the CPU model and the commit.
- **Data:** per-run summaries are collected on branch `wave-collected` (`<wave>/summaries.jsonl`, one line per run); trained actors are on branch `wave-actors`.
- **Seeds:** tuning 0 to 3; learner training 2000 and up; ceiling validation 200 to 209; tournament 300 to 309; confirmation 103 to 122; report cells 400 to 409 (selection of static points and floors on seeds 0 to 2).
- **Rebuilding this report:** `bash docs/reports/final-report-v4.1.0/build.sh` regenerates the tables and figures from the result files and writes the Word file. Part I's text comes from the mentor's scenario list (`analyze/mentor_source.md`); a check compares the rendered text with the source.
{{include:generated/build_info.md}}
