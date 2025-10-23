# MCP Stock Alert Agent

This project is an **automated stock and news monitoring agent**, paired with a FastAPI WebSocket server.  
It is designed for swing trading, stock alerts, and real-time analytics, with easy deployment across any Mac/Linux via Git.

---

## Features

- **FastAPI MCP Server:** Runs a local WebSocket endpoint for agentic communication and monitoring.
- **Automated Stock/News Analytics:** Periodic analysis script tracks price, news, and alerts (customizable in main.py).
- **Duplicate Alert Prevention:** Smart filtering prevents repeated alerts for the same stock conditions within 7 days.
- **Easy Startup:** One-click script launches server, analytics agent, and (optionally) a WebSocket test client.
- **Portable Setup:** Fully reproducible on any Mac/Linux via git clone and shell scripts.
- **Extensible:** Add new agents, endpoints, or analytics tasks with ease.

---

## Getting Started

### 1. Clone This Repository

```bash
git clone https://github.com/masterai6612/mcp-stock-alert.git
cd mcp-stock-alert
```

### 2. Run the Setup Script

Creates and activates a Python virtual environment, installs dependencies, and prepares startup scripts.

```bash
chmod +x setup_mcp_agent.sh
./setup_mcp_agent.sh
```

### 3. Configure Environment (Optional)

For email alerts and Twitter sentiment analysis:

```bash
cp .env.template .env
# Edit .env with your credentials
```

### 4. Run the Agent

This launches the MCP FastAPI server, your analytics/alert agent, and a WebSocket test client.

```bash
./start_stock_monitor.sh
```

### 5. Run in Background (Alternative)

For continuous operation using tmux:

```bash
./start_mcp_tmux.sh
# To stop: ./stop_mcp_tmux.sh
```

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





---

## Manual Commands

### Run Single Analysis
```bash
source venv/bin/activate
python -c 'from main_copilot import main_task; main_task()'
```

### Manual tmux Setup (if scripts don't work)
```bash
# Install tmux if needed
brew install tmux

# Start session and run agent
tmux new -s mcp-alert
source venv/bin/activate
python main_copilot.py

# Detach: Ctrl-b d
# Reattach: tmux attach -t mcp-alert
# Kill session: tmux kill-session -t mcp-alert
```

### Monitor Logs
```bash
tail -F ~/mcp-stock-alert.log
```

### Manage Alert History
```bash
# Show current alert history
python clear_alert_history.py show

# Clear alert history (to reset duplicate prevention)
python clear_alert_history.py clear
```