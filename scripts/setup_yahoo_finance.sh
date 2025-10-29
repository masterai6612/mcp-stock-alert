#!/bin/bash

echo "🚀 Setting up Yahoo Finance Enhanced Stock Analysis"
echo "=================================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Activating existing virtual environment..."
    source venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install required packages
echo "📥 Installing required packages..."
pip install --upgrade pip
pip install yfinance requests beautifulsoup4 pandas schedule smtplib-ssl mcp

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 AVAILABLE FEATURES:"
echo "====================="
echo "✅ Real-time stock quotes"
echo "✅ Earnings calendar (upcoming 7 days)"
echo "✅ Investment themes (AI, EV, Cloud, etc.)"
echo "✅ Sector performance tracking"
echo "✅ Enhanced stock alerts with themes"
echo "✅ MCP server integration for Kiro"
echo ""
echo "🧪 TEST THE SYSTEM:"
echo "=================="
echo "1. Test Yahoo Finance client:"
echo "   python enhanced_yahoo_client.py"
echo ""
echo "2. Test MCP server:"
echo "   python test_mcp_server.py"
echo ""
echo "3. Run enhanced stock analysis:"
echo "   python main_enhanced.py"
echo ""
echo "🔧 MCP INTEGRATION:"
echo "=================="
echo "The MCP server 'yahoo-finance-enhanced' is configured in .kiro/settings/mcp.json"
echo "Available tools:"
echo "  - get_stock_quote"
echo "  - get_earnings_calendar"
echo "  - get_investment_themes"
echo ""
echo "🎉 Ready to use! No API keys required!"