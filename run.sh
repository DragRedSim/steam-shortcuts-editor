#!/bin/bash

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found."
    exit 1
fi

# Setup virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    uv venv .venv
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Run the application using the Python executable from the virtual environment
echo "Running the application..."
.venv/bin/python steam_shortcuts_editor.py 