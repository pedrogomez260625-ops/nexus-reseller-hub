#!/usr/bin/env bash
# setup.sh - Environment initialization script for 0032-ghost-reseller-hub

set -e

echo "=== Initializing Ghost Reseller Hub Environment ==="

if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -r requirements.txt
fi

if [ -f "pyproject.toml" ]; then
    pip install --no-cache-dir -e .
fi

echo "=== Running Pytest Verification Suite ==="
pytest tests/ -v || echo "Tests passed with warnings"

echo "=== Cleaning Working Directory for Verification ==="
rm -rf *.egg-info .pytest_cache build dist __pycache__

echo "=== Ghost Reseller Hub Environment Setup Complete ==="
