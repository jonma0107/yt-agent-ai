#!/usr/bin/env bash
# HTML diseñado -> PDF fiel (Chrome headless, sin headers/footers).
# Uso: ./html_to_pdf.sh [archivo.html] [nombre_base_pdf]
set -euo pipefail
cd "$(dirname "$0")"

HTML="${1:-docs.html}"
BASE="${2:-${HTML%.html}}"

if ! command -v google-chrome >/dev/null 2>&1; then
  echo "ERROR: se requiere google-chrome para preservar colores y tipografías." >&2
  exit 1
fi

google-chrome \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --print-to-pdf="${BASE}.pdf" \
  --print-to-pdf-no-header \
  "file://$(pwd)/${HTML}"

echo "OK: ${BASE}.pdf"
