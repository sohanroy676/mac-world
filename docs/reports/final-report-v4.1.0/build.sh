#!/usr/bin/env bash
# Rebuild the report from the collected wave summaries.
# usage: build.sh <dir with rs2a.jsonl rs2b.jsonl rs2c.jsonl> [python]   (default python: python3)
set -euo pipefail
cd "$(dirname "$0")"
D=${1:?dir with rs2a/rs2b/rs2c.jsonl}; PY=${2:-python3}
$PY analyze/compare_tables.py
$PY analyze/maxcw_figs.py
$PY analyze/rep_cells.py "$D/rs2a.jsonl" "$D/rs2b.jsonl" "$D/rs2c.jsonl"
$PY analyze/rep_narr.py
$PY analyze/rep_extra.py
export REPORT_COMMIT=$(git rev-parse --short=8 HEAD) REPORT_DATE=$(date -u +%Y-%m-%d)
node build_docx.js sections/order.txt out/MAC-WORLD-Final-Report-v4.1.0.docx
