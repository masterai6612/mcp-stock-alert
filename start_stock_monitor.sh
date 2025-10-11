#!/bin/bash

# Switch to your project folder
cd ~/Desktop/Stockmarket/mcp-ai_agent/mcp-stock-alert

# Activate your virtual environment
source venv/bin/activate

# Kill any running MCP server (on port 8000)
PIDS=$(lsof -t -i:8000)
if [ ! -z "$PIDS" ]; then
    echo "Killing existing MCP server(s) with PID(s): $PIDS"
    kill -9 $PIDS
fi

# Start MCP FastAPI server in the background
uvicorn mcp_server:app --reload &

# Wait for server startup
sleep 2

# Start the WebSocket test client in the background (logs output to ws_test.log)
python ws_test.py > ws_test.log 2>&1 &

# Run your automated stock/news alert agent
python main.py

# Optional: kill background processes when main.py exits
# kill %1
# kill %2

