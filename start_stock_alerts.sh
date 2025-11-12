#!/bin/bash

# 🚀 Simple Stock Alert System Startup
# Run this after laptop restart to get email alerts

echo "🚀 Starting Stock Alert System..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "scheduled_market_alerts.py" ]; then
    echo "❌ Error: Please run this script from the mcp-stock-alert directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "💡 Create .env file with EMAIL_FROM and EMAIL_PASSWORD"
    exit 1
fi

# Start the 24/7 monitoring system
echo "🔍 Starting 24/7 Stock Monitoring System..."
echo ""
echo "📧 Email alerts will be sent to: masterai6612@gmail.com"
echo "⚡ Alerts sent ONLY when significant changes occur"
echo ""
echo "📊 Monitoring Schedule:"
echo "   🌅 Pre-Market:    4:00 AM - 9:30 AM EST"
echo "   🌞 Regular Hours: 9:30 AM - 4:00 PM EST"
echo "   🌙 After-Hours:   4:00 PM - 8:00 PM EST"
echo ""
echo "💡 Press Ctrl+C to stop"
echo "=================================="
echo ""

# Run the scheduled alerts system
python scheduled_market_alerts.py
