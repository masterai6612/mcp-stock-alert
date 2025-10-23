#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting MCP Stock Monitor from: $SCRIPT_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./setup_mcp_agent.sh first"
    exit 1
fi

source venv/bin/activate

# Kill any running MCP server (on port 8000)
PIDS=$(lsof -t -i:8000 2>/dev/null || true)
if [ ! -z "$PIDS" ]; then
    echo "Killing existing MCP server(s) with PID(s): $PIDS"
    kill -9 $PIDS
    sleep 1
fi

echo "Starting MCP FastAPI server..."
# Start MCP FastAPI server in the background
uvicorn mcp_server:app --host 127.0.0.1 --port 8000 --reload &
SERVER_PID=$!

# Wait for server startup
sleep 3

echo "Starting WebSocket test client..."
# Start the WebSocket test client in the background (logs output to ws_test.log)
python ws_test.py > ws_test.log 2>&1 &
WS_TEST_PID=$!

echo "Starting stock alert agent..."
# Run your automated stock/news alert agent
python main_copilot.py

# Cleanup function
cleanup() {
    echo "Shutting down processes..."
    kill $SERVER_PID 2>/dev/null || true
    kill $WS_TEST_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

