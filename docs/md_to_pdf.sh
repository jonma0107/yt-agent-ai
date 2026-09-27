#!/usr/bin/env bash
# Markdown -> PDF simple (pandoc + xelatex) según la skill.
# Uso: ./md_to_pdf.sh [archivo.md]
set -euo pipefail
cd "$(dirname "$0")"

MD="${1:-README.md}"
PDF="${MD%.md}-pandoc.pdf"

pandoc "$MD" -o "$PDF" \
  --pdf-engine=xelatex \
  -V colorlinks=true -V linkcolor=blue -V urlcolor=blue -V toccolor=black \
  --highlight-style=tango --toc --toc-depth=3 \
  -V papersize=a3 -V fontsize=11pt \
  -V mainfont="DejaVu Sans" -V monofont="DejaVu Sans Mono"

echo "OK: $PDF"
