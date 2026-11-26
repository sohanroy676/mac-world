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
$PY analyze/check_part1.py
export REPORT_COMMIT=$(git rev-parse --short=8 HEAD) REPORT_DATE=$(date -u +%Y-%m-%d)
OUT=out/MAC-WORLD-Final-Report-v4.1.0.docx
SOFFICE=$(ls /root/.claude/skills/synced/*/docx/scripts/office/soffice.py | head -1)
rm -f out/toc_pages.json
for pass in 1 2 3; do   # page numbers of the contents come from the rendered PDF; repeat until they stop changing
  node build_docx.js sections/order.txt $OUT
  /usr/bin/python3 "$SOFFICE" --headless --convert-to pdf --outdir out/pdf $OUT >/dev/null
  cp out/toc_pages.json out/toc_prev.json 2>/dev/null || echo '{}' > out/toc_prev.json
  python3 analyze/toc_pages.py out/toc_items.json out/pdf/MAC-WORLD-Final-Report-v4.1.0.pdf out/toc_pages.json
  cmp -s out/toc_pages.json out/toc_prev.json && break
done
node build_docx.js sections/order.txt $OUT
