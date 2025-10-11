# MCP Stock Alert Agent

This project is an **automated stock and news monitoring agent**, paired with a FastAPI WebSocket server.  
It is designed for swing trading, stock alerts, and real-time analytics, with easy deployment across any Mac/Linux via Git.

---

## Features

- **FastAPI MCP Server:** Runs a local WebSocket endpoint for agentic communication and monitoring.
- **Automated Stock/News Analytics:** Periodic analysis script tracks price, news, and alerts (customizable in main.py).
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
