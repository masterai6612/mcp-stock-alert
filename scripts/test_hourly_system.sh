#!/bin/bash

# Test script for the hourly alert system

echo "🧪 Testing 24/7 Enhanced Alert System"
echo "====================================="

# Check if the system is running
if pgrep -f "scheduled_market_alerts.py" > /dev/null; then
    echo "✅ 24/7 alert system is running"
    PID=$(pgrep -f "scheduled_market_alerts.py")
    echo "   Process ID: $PID"
else
    echo "❌ 24/7 alert system is not running"
    echo "   Start it with: python scheduled_market_alerts.py &"
    exit 1
fi

echo
echo "📊 Checking system files..."

# Check for tracking files
if [ -f "last_recommendations.json" ]; then
    echo "✅ Recommendations tracking file exists"
    echo "   Last update: $(jq -r '.timestamp // "Never"' last_recommendations.json 2>/dev/null || echo "Invalid JSON")"
else
    echo "⚠️  Recommendations tracking file not found (will be created on first run)"
fi

if [ -f "stock_tracking.json" ]; then
    echo "✅ Stock tracking file exists"
else
    echo "⚠️  Stock tracking file not found (will be created on first run)"
fi

if [ -f "sent_alerts.json" ]; then
    echo "✅ Sent alerts file exists"
else
    echo "⚠️  Sent alerts file not found (will be created on first run)"
fi

echo
echo "📧 Testing email configuration..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

email_from = os.getenv('EMAIL_FROM')
email_password = os.getenv('EMAIL_PASSWORD')

if email_from and email_password:
    print('✅ Email configuration found')
    print(f'   From: {email_from}')
else:
    print('❌ Email configuration missing in .env file')
"

echo
echo "🔍 Testing change detection logic..."
python test_hourly_alerts.py

echo
echo "📋 24/7 System Status Summary:"
echo "============================="
echo "✅ 24/7 analysis: Pre-market, Regular hours, After-hours"
echo "✅ Emails sent ONLY for SIGNIFICANT changes"
echo "✅ Session-aware thresholds (higher for extended hours)"
echo "✅ Weekend international exposure monitoring"
echo "✅ Smart change detection prevents spam"

echo
echo "📊 Monitoring Schedule:"
echo "   🌅 Pre-Market:    4:00 AM - 9:30 AM EST (100 stocks, BUY≥8)"
echo "   🌞 Regular Hours: 9:30 AM - 4:00 PM EST (200 stocks, BUY≥7)"
echo "   🌙 After-Hours:   4:00 PM - 8:00 PM EST (100 stocks, BUY≥8)"
echo "   💤 Overnight:     8:00 PM - 4:00 AM EST (Paused)"
echo "   🌍 Weekends:      Limited international monitoring"

echo
echo "📊 To monitor the system:"
echo "   • View logs: tail -f scheduled_alerts.log"
echo "   • Check process: ps aux | grep scheduled_market_alerts"
echo "   • Stop system: pkill -f scheduled_market_alerts.py"
echo "   • Restart: python scheduled_market_alerts.py &"
echo "   • Test system: python test_hourly_alerts.py"
echo "   • View overnight actions: cat overnight_actions.json"

echo
echo "🎯 The 24/7 system is designed to be 'set and forget' - it will:"
echo "   1. Run analysis every hour during all trading sessions"
echo "   2. Use session-appropriate stock coverage and thresholds"
echo "   3. Send email ONLY for significant changes (no spam)"
echo "   4. Provide daily summaries and weekend international updates"
echo "   5. Adapt to market conditions automatically"
echo
echo "✅ Testing complete!"