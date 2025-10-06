#!/usr/bin/env bash
set -euo pipefail

REPORT_MD="Assignment_4_Report.md"
OUTPUT_PDF="../Assignment 4.pdf"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is required but not found. Install pandoc and re-run."
  echo "On Ubuntu: sudo apt-get update && sudo apt-get install -y pandoc"
  exit 1
fi

echo "Exporting $REPORT_MD to $OUTPUT_PDF ..."
pandoc "$REPORT_MD" -o "$OUTPUT_PDF" --from gfm --pdf-engine=xelatex || pandoc "$REPORT_MD" -o "$OUTPUT_PDF" --from gfm

echo "Done: $OUTPUT_PDF"
