# MCP Stock Alert Agent

This project is an **automated stock and news monitoring agent**, paired with a FastAPI WebSocket server.  
It is designed for swing trading, stock alerts, and real-time analytics, with easy deployment across any Mac/Linux via Git.

---

## Features

- **FastAPI MCP Server:** Runs a local WebSocket endpoint for agentic communication and monitoring.
- **Automated Stock/News Analytics:** Monitors 269+ stocks including S&P 500 large caps, recent IPOs, and trending stocks with periodic analysis for price, news, and alerts.
- **Easy Startup:** One-click script launches server, analytics agent, and (optionally) a WebSocket test client.
- **Portable Setup:** Fully reproducible on any Mac/Linux via git clone and shell scripts.
- **Extensible:** Add new agents, endpoints, or analytics tasks with ease.

---

## Getting Started

### 1. Clone This Repository

git clone https://github.com/masterai6612/mcp-stock-alert.git
cd mcp-stock-alert

text

### 2. Run the Setup Script

Creates and activates a Python virtual environment, installs dependencies, and prepares startup scripts.

chmod +x setup_mcp_agent.sh
./setup_mcp_agent.sh

text

### 3. Run the Agent

This launches the MCP FastAPI server, your analytics/alert agent, and a WebSocket test client (optional).

./start_stock_monitor.sh

text

---

## What This Code Does

- **Starts a FastAPI server** (MCP agent) on `ws://127.0.0.1:8000/ws`.
- **Runs a stock/news analytics agent** (main.py) for trading alerts and background jobs.
- **Includes a WebSocket client test** (ws_test.py) to verify connections.
- **Setup and startup scripts** ensure consistent environments, easy usage, and reproducibility.

---

## Requirements

- Python 3.8+
- macOS/Linux terminal
- Email/X (Twitter) API keys as needed (see main.py or .env for details)

---





# GitHub Copilot

source venv/bin/activate
python -c 'from main_copilot import main_task; main_task()'


# To run this continiously

# install tmux if needed
brew install tmux

# start a session
tmux new -s mcp-alert

# inside tmux: activate venv and run the script
cd /Users/monie/Desktop/GitHub/Stocks/Preplexity/mcp-stock-alert
source venv/bin/activate
# run continuously (script already loops)
python main_copilot.py

# detach from session: Ctrl-b d
# reattach later:
tmux attach -t mcp-alert


# Graceful stop: attach and Ctrl-C inside session
tmux attach -t mcp-alert   # then Ctrl-C in the running window

# Kill the whole session from shell:
tmux kill-session -t mcp-alert

# To restart, create a new session as above or run:
tmux new -s mcp-alert 'cd /Users/monie/Desktop/GitHub/Stocks/Preplexity/mcp-stock-alert && source venv/bin/activate && python main_copilot.py >> ~/mcp-stock-alert.log 2>&1'


# follow output
tail -F ~/mcp-stock-alert.log