# Project Structure

## Root Directory Organization

```
mcp-stock-alert/
├── main.py                    # Core stock analysis engine
├── main_enhanced.py           # Enhanced analysis with earnings/themes
├── main_copilot.py           # Copilot integration version
├── scheduled_market_alerts.py # Scheduled alert system
├── web_dashboard.py          # Flask web dashboard
├── mcp_server.py             # FastAPI MCP WebSocket server
├── enhanced_yahoo_client.py  # Extended Yahoo Finance client
├── dashboard_features.py     # Dashboard utility functions
├── stock_change_tracker.py   # Price change tracking
├── manage_watchlist.py       # Watchlist management
└── check_alert_status.py     # Alert status checker
```

## Configuration & Data Files

```
├── stock_tracking.json       # Watchlist and tracking data
├── sent_alerts.json         # Alert history (auto-generated)
└── *.log                    # Various log files (auto-generated)
```

## Shell Scripts

```
├── setup_mcp_agent.sh        # Initial project setup
├── start_stock_monitor.sh    # Start main monitoring system
├── start_mcp_tmux.sh         # Start with tmux session
├── stop_mcp_tmux.sh          # Stop tmux session
├── start_dashboard.sh        # Start web dashboard
├── start_market_alerts.sh    # Start scheduled alerts
└── setup_yahoo_finance.sh    # Yahoo Finance setup
```

## Web Dashboard

```
dashboard/
├── dashboard.html            # Main dashboard interface
└── index.html               # Alternative dashboard entry
```

## Testing Files

```
├── test_mcp_server.py        # MCP server tests
├── test_dashboard_api.py     # Dashboard API tests
├── test_email_alerts.py      # Email functionality tests
└── ws_test.py               # WebSocket connection tests
```

## Documentation

```
├── README.md                 # Main project documentation
├── WEB_DASHBOARD_GUIDE.md    # Dashboard usage guide
├── MARKET_ALERT_SYSTEM.md    # Alert system documentation
├── YAHOO_FINANCE_SOLUTION.md # Yahoo Finance integration
├── CLEAN_YAHOO_SOLUTION.md   # Clean implementation guide
└── MCP_DEBUG_SOLUTION.md     # MCP debugging guide
```

## Architecture Patterns

### Core Components
- **Analysis Engine** (`main.py`, `main_enhanced.py`): Stock screening and recommendation logic
- **Data Layer** (`enhanced_yahoo_client.py`): Yahoo Finance API abstraction
- **Notification System** (email functions in main files): Alert delivery
- **Web Interface** (`web_dashboard.py` + `dashboard/`): Real-time monitoring
- **MCP Integration** (`mcp_server.py`): WebSocket communication

### Data Flow
1. **Scheduled Analysis**: `scheduled_market_alerts.py` runs daily analysis
2. **Data Fetching**: `enhanced_yahoo_client.py` retrieves market data
3. **Signal Generation**: Main analysis files process data and generate signals
4. **Alert Delivery**: Email notifications sent for qualifying signals
5. **Dashboard Updates**: Web interface displays real-time system status

### Configuration Management
- **Stock Lists**: Defined in main analysis files (`symbols` arrays)
- **Email Settings**: Hardcoded in main files (should be environment variables)
- **Thresholds**: Alert criteria defined in recommendation functions
- **Watchlists**: Managed via `stock_tracking.json` and `manage_watchlist.py`

## File Naming Conventions

- `main_*.py` - Core analysis engines
- `test_*.py` - Test files
- `start_*.sh` - Startup scripts
- `setup_*.sh` - Configuration scripts
- `*_SOLUTION.md` - Implementation guides
- `*_GUIDE.md` - Usage documentation

## Development Guidelines

- Keep analysis logic in `main_*.py` files
- Web dashboard code in `web_dashboard.py` + `dashboard/`
- Utility functions in dedicated modules (`dashboard_features.py`, etc.)
- Shell scripts for common operations
- JSON files for data persistence
- Markdown files for documentation