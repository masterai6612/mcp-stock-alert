#!/bin/bash

echo "🚀 Starting Market Alert System"
echo "==============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install any missing dependencies
pip install holidays schedule > /dev/null 2>&1

echo "📧 Email alerts configured for: masterai6612@gmail.com"
echo "⏰ Morning alerts: 7:30 AM EST (weekdays)"
echo "🔍 Trend monitoring: Every 30 minutes during trading hours"
echo ""
echo "🎯 MONITORING FEATURES:"
echo "  ✅ Technical analysis (RSI, MACD, Moving Averages)"
echo "  ✅ Multi-market coverage (NYSE, NASDAQ, TSX)"
echo "  ✅ Earnings calendar integration"
echo "  ✅ Investment themes tracking"
echo "  ✅ Upward trend detection"
echo ""
echo "🔄 Starting system... Press Ctrl+C to stop"
echo ""

# Run the scheduled alert system
python scheduled_market_alerts.py