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

echo "Setup complete!"

echo ""
echo "Next steps:"
echo "1. Set environment variables for email alerts (optional):"
echo "   export ALERT_EMAIL_TO='your-email@gmail.com'"
echo "   export ALERT_EMAIL_FROM='your-email@gmail.com'"
echo "   export ALERT_EMAIL_PASS='your-gmail-app-password'"
echo "   export X_BEARER_TOKEN='your-twitter-bearer-token'"
echo ""
echo "2. Run the stock monitor:"
echo "   ./start_stock_monitor.sh"
echo ""
echo "3. Or run with tmux for background operation:"
echo "   ./start_mcp_tmux.sh"
