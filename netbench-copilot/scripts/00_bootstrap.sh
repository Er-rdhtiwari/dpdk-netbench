#!/bin/bash
set -e

echo "==================================="
echo "NetBench Copilot - Bootstrap Script"
echo "==================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "Error: Python 3.11+ required (found: $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo "✓ uv installed"

# Create virtual environment and install dependencies
echo "Installing dependencies..."
uv sync

# Create necessary directories
echo "Creating directory structure..."
mkdir -p .cache/index
mkdir -p data/kb/pdfs
mkdir -p data/sample_runs/{cryptoperf_run_001,testpmd_run_001,l3fwd_run_001}/{logs,env}
mkdir -p out

echo "✓ Directories created"

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠ Please edit .env and add your OPENAI_API_KEY"
fi

echo ""
echo "==================================="
echo "Bootstrap complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Add DPDK tuning PDFs to data/kb/pdfs/"
echo "3. Run: make index"
echo "4. Run: make demo"
echo ""

# Made with Bob
