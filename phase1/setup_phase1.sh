#!/bin/bash
# Phase 1: Setup Script
# Prepares environment and runs the complete test pipeline

set -e  # Exit on error

echo "=============================================="
echo "PHASE 1: EMBEDDING VIABILITY TEST - SETUP"
echo "=============================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check if Git is available (needed for dataset generation)
echo ""
echo "Checking Git installation..."
git --version || { echo "Error: Git not found. Install Git to clone repos."; exit 1; }
echo "✓ Git is available"

echo ""
echo "=============================================="
echo "SETUP COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Run dataset generation:  python dataset_generator.py"
echo "2. Run embedding tests:     python test_embeddings.py"
echo ""
echo "Or run the complete pipeline:"
echo "  bash run_phase1.sh"
echo ""
