#!/bin/bash
set -e

echo "==================================="
echo "NetBench Copilot - Demo"
echo "==================================="
echo ""

# Demo 1: Ask mode
echo "Demo 1: Ask Mode (KB Q&A)"
echo "-------------------------"
echo "Query: What are recommended hugepage settings for DPDK?"
echo ""
uv run netbench ask --query "What are recommended hugepage settings for DPDK?" || echo "⚠ Demo requires KB index and API key"
echo ""
echo "Press Enter to continue..."
read

# Demo 2: Plan mode (will fail without real KB, but shows structure)
echo ""
echo "Demo 2: Plan Mode"
echo "-----------------"
echo "Goal: Test AES-GCM-128 at 64B and 1024B frame sizes"
echo ""
echo "⚠ This demo requires:"
echo "  - KB index built from DPDK tuning PDFs"
echo "  - OPENAI_API_KEY in .env"
echo ""
echo "Example command:"
echo "  netbench plan --benchmark cryptoperf --platform epyc9004 \\"
echo "    --nl 'Test AES-GCM-128 at 64B and 1024B frame sizes'"
echo ""
echo "Press Enter to continue..."
read

# Demo 3: Parse mode with sample data
echo ""
echo "Demo 3: Parse Mode (Sample Data)"
echo "--------------------------------"
if [ -f "data/sample_runs/testpmd_run_001/logs/stdout.txt" ]; then
    echo "Parsing sample testpmd logs..."
    uv run netbench parse --benchmark testpmd \
        --run-dir data/sample_runs/testpmd_run_001 \
        --store false || echo "⚠ Parser implementation needed"
else
    echo "⚠ Sample logs not found. Create synthetic logs in:"
    echo "  data/sample_runs/testpmd_run_001/logs/stdout.txt"
fi
echo ""
echo "Press Enter to continue..."
read

# Demo 4: Compare mode
echo ""
echo "Demo 4: Compare Mode"
echo "-------------------"
echo "⚠ This demo requires stored runs in database"
echo ""
echo "Example command:"
echo "  netbench compare --baseline run_001 --candidate run_002"
echo ""
echo "Press Enter to continue..."
read

# Demo 5: Dataset export
echo ""
echo "Demo 5: Dataset Export"
echo "---------------------"
echo "⚠ This demo requires stored runs in database"
echo ""
echo "Example command:"
echo "  netbench dataset --out ./out/dataset"
echo ""
echo "Press Enter to continue..."
read

# Demo 6: Evaluation
echo ""
echo "Demo 6: Evaluation Harness"
echo "-------------------------"
echo "⚠ This demo requires eval cases and KB index"
echo ""
echo "Example command:"
echo "  netbench eval --cases data/golden_prompts/eval_cases.yaml"
echo ""

echo ""
echo "==================================="
echo "Demo Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Add DPDK tuning PDFs to data/kb/pdfs/"
echo "2. Update data/kb/manifest.yaml"
echo "3. Run: make index"
echo "4. Set OPENAI_API_KEY in .env"
echo "5. Try: netbench ask --query 'your question'"
echo ""

# Made with Bob
