#!/bin/bash

set -e

echo "=================================="
echo "  Neural Agent Installer"
echo "=================================="
echo ""

if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "[4/4] Installation complete!"
echo ""

echo "=================================="
echo "  Quick Start"
echo "=================================="
echo ""
echo "Activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "Start Neural Agent:"
echo "  neural-agent"
echo ""
echo "Or with web dashboard:"
echo "  neural-agent --web"
echo ""
echo "=================================="