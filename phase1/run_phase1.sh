#!/bin/bash
# Phase 1: Complete Pipeline Runner
# Generates dataset, tests models, and produces decision report

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   PHASE 1: EMBEDDING VIABILITY TEST - FULL PIPELINE        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Ensure we're in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Run: source venv/bin/activate"
    exit 1
fi

# Step 1: Generate test dataset
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ STEP 1: GENERATING TEST DATASET                         │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

if [ -d "test_code" ] && [ -f "test_code/metadata.json" ]; then
    echo "⚠️  Test dataset already exists"
    read -p "   Regenerate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf test_code temp_repos
        python dataset_generator.py
    else
        echo "   Using existing dataset"
    fi
else
    python dataset_generator.py
fi

# Step 2: Test embedding models
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ STEP 2: TESTING EMBEDDING MODELS                        │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
python test_embeddings.py

# Step 3: Display results
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ STEP 3: RESULTS & DECISION                              │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

if [ -f "comparison.md" ]; then
    cat comparison.md
else
    echo "⚠️  No comparison.md found. Check test_embeddings.py output."
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 PHASE 1 PIPELINE COMPLETE                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Results saved to:"
echo "  - test_code/           Test dataset"
echo "  - results_*.json       Per-model results"
echo "  - all_results.json     Combined results"
echo "  - comparison.md        Decision report"
echo ""
echo "Next: Review comparison.md for GO/NO-GO decision"
echo ""
