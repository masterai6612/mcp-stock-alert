#!/bin/bash

set -e

echo "Setting up MCP Stock Agent project..."

# Create Python virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn requests pandas yfinance beautifulsoup4 schedule holidays websockets
fi

# Make all .sh scripts in the directory executable
chmod +x ./*.sh

echo "Setup complete
