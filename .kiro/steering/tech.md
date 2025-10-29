# Technology Stack

## Core Technologies

- **Python 3.8+**: Primary language for all components
- **FastAPI**: WebSocket server for MCP integration
- **Flask**: Web dashboard backend
- **yfinance**: Yahoo Finance API client for stock data
- **pandas**: Data analysis and manipulation
- **requests + BeautifulSoup**: Web scraping for news and sentiment
- **schedule**: Task scheduling for automated alerts

## Key Libraries

### Data & Analysis
- `yfinance` - Stock price and company data
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations
- `holidays` - Market holiday detection

### Web & APIs
- `fastapi` - MCP server framework
- `flask` - Dashboard web server
- `uvicorn` - ASGI server for FastAPI
- `websockets` - WebSocket client/server
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing

### Notifications
- `smtplib` - Email alerts (built-in)
- Email configuration uses Gmail SMTP

### System & Utilities
- `psutil` - System process monitoring
- `schedule` - Cron-like job scheduling
- `threading` - Background tasks

## Build & Run Commands

### Initial Setup
```bash
# Setup virtual environment and dependencies
chmod +x setup_mcp_agent.sh
./setup_mcp_agent.sh
```

### Running Components

#### Stock Monitor (Main System)
```bash
# Start MCP server + analytics agent
./start_stock_monitor.sh

# Or run components individually:
source venv/bin/activate
uvicorn mcp_server:app --reload &
python main.py
```

#### Enhanced Analytics
```bash
source venv/bin/activate
python main_enhanced.py  # One-time run
python scheduled_market_alerts.py  # Scheduled runs
```

#### Web Dashboard
```bash
source venv/bin/activate
python web_dashboard.py
# Access at http://localhost:5001
```

#### Background Services with tmux
```bash
# Start persistent session
./start_mcp_tmux.sh

# Stop session
./stop_mcp_tmux.sh
```

### Testing
```bash
source venv/bin/activate
python test_mcp_server.py      # Test MCP server
python test_dashboard_api.py   # Test dashboard APIs
python test_email_alerts.py    # Test email functionality
python ws_test.py             # Test WebSocket connection
```

## Configuration

### Email Settings
Configure in main Python files:
- `email_to` - Recipient email
- `email_from` - Sender email (Gmail)
- `email_password` - Gmail app password

### Stock Symbols
Modify `symbols` list in main files to customize monitored stocks.

### Alert Criteria
Adjust thresholds in recommendation functions:
- Growth percentage (default: ≥7%)
- RSI ranges (default: 55-80)
- News sentiment weights

## Development Notes

- Virtual environment required (`venv/`)
- All shell scripts should be executable (`chmod +x`)
- Port 8000 for MCP server, 5001 for dashboard
- Logs written to individual `.log` files
- JSON files used for data persistence (`stock_tracking.json`, etc.)