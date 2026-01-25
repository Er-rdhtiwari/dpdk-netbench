#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: scripts/30_add_pdf.sh /path/to/file.pdf" >&2
  exit 1
fi

PDF_SRC="$1"
if [[ ! -f "$PDF_SRC" ]]; then
  echo "File not found: $PDF_SRC" >&2
  exit 1
fi

mkdir -p data/kb/pdfs
DEST="data/kb/pdfs/$(basename "$PDF_SRC")"
cp "$PDF_SRC" "$DEST"

python - <<'PY'
import sys, yaml
from pathlib import Path

manifest = Path("data/kb/manifest.yaml")
if manifest.exists():
    data = yaml.safe_load(manifest.read_text()) or {}
else:
    data = {}

pdfs = data.get("pdfs", [])
name = Path(sys.argv[1]).name
pdfs.append({
    "file": name,
    "vendor": "unknown",
    "platform": "unknown",
    "version": "unknown",
    "tags": [],
})

data["pdfs"] = pdfs
manifest.write_text(yaml.safe_dump(data, sort_keys=False))
print(f"Registered {name} in manifest")
PY "$PDF_SRC"
