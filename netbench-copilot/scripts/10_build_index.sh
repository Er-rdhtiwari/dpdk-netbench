#!/bin/bash
set -e

echo "==================================="
echo "Building KB Index"
echo "==================================="

# Check if PDFs exist
pdf_count=$(find data/kb/pdfs -name "*.pdf" 2>/dev/null | wc -l)
if [ "$pdf_count" -eq 0 ]; then
    echo "⚠ No PDFs found in data/kb/pdfs/"
    echo ""
    echo "Please add DPDK tuning PDFs to data/kb/pdfs/ and update data/kb/manifest.yaml"
    echo ""
    echo "Example manifest.yaml:"
    echo "---"
    echo "version: '1.0'"
    echo "pdfs:"
    echo "  - filename: amd-epyc-dpdk-tuning.pdf"
    echo "    vendor: AMD"
    echo "    platform: EPYC"
    echo "    version: '1.0'"
    echo "    benchmark_tags: [cryptoperf, testpmd, l3fwd]"
    echo "    epyc_family_tags: [7003, 8004, 9004]"
    echo "    release_tags: [dpdk-23.11]"
    exit 1
fi

echo "Found $pdf_count PDF(s)"

# Build index
echo "Building index (this may take a few minutes)..."
uv run python -c "
from pathlib import Path
from netbench.kb import KBIndexBuilder
from netbench.config import settings

builder = KBIndexBuilder(
    kb_path=Path('data/kb'),
    index_path=settings.index_path
)
builder.build_index(force_rebuild=False)
print('✓ Index built successfully')
"

echo ""
echo "==================================="
echo "Index build complete!"
echo "==================================="

# Made with Bob
