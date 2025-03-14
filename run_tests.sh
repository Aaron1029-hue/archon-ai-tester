#!/bin/bash

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .
pip install pytest pytest-cov

# Run tests
echo "Running tests..."
pytest

# Deactivate virtual environment
deactivate

echo "Tests completed!"