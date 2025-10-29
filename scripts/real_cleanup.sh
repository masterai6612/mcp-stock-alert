#!/bin/bash

echo "🧹 REAL CLEANUP - Removing Actual Redundancy"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

echo "🔍 Analyzing current directory structure..."
echo

# 1. Remove duplicate mcp-stock-alert subdirectory (it's a nested copy)
if [ -d "mcp-stock-alert" ]; then
    print_warning "Found nested mcp-stock-alert directory - this is a duplicate!"
    echo "   Contents:"
    ls -la mcp-stock-alert/ | head -10
    echo
    read -p "   Remove this duplicate directory? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf mcp-stock-alert/
        print_status "Removed duplicate mcp-stock-alert directory"
    fi
fi

# 2. Remove redundant start scripts
echo "🚀 Analyzing start scripts..."
echo "   start_complete_system.sh - ✅ KEEP (main startup script)"
echo "   start_dashboard_prod.sh - ❌ REDUNDANT (dashboard is in complete system)"
echo "   start_mcp_tmux.sh - ❌ REDUNDANT (old tmux approach)"
echo "   start_stock_monitor.sh - ❌ REDUNDANT (old monitoring approach)"
echo

read -p "Remove redundant start scripts? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f start_dashboard_prod.sh start_mcp_tmux.sh start_stock_monitor.sh
    print_status "Removed redundant start scripts"
fi

# 3. Remove redundant MCP servers
echo "🔗 Analyzing MCP servers..."
echo "   mcp_server.py - ❌ REDUNDANT (basic WebSocket server)"
echo "   yahoo_finance_mcp_server.py - ✅ KEEP (enhanced Yahoo Finance MCP)"
echo

read -p "Remove basic mcp_server.py? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f mcp_server.py
    print_status "Removed basic mcp_server.py"
fi

# 4. Remove redundant test files
echo "🧪 Analyzing test files..."
echo "   test_stock_universe_integration.py - ❌ REDUNDANT (covered by tests/ folder)"
echo "   ws_test.py - ❌ REDUNDANT (old WebSocket test)"
echo

read -p "Remove redundant test files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f test_stock_universe_integration.py ws_test.py
    print_status "Removed redundant test files"
fi

# 5. Remove old tmux scripts
echo "📺 Analyzing tmux scripts..."
if [ -f "stop_mcp_tmux.sh" ]; then
    echo "   stop_mcp_tmux.sh - ❌ REDUNDANT (old tmux approach)"
    read -p "Remove tmux scripts? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f stop_mcp_tmux.sh
        print_status "Removed tmux scripts"
    fi
fi

# 6. Clean up documentation files
echo "📚 Analyzing documentation..."
echo "   README.md - ✅ KEEP (main documentation)"
echo "   CLEANUP_SUMMARY.md - ❌ REDUNDANT (cleanup is done)"
echo "   STOCK_UNIVERSE_UPDATE.md - ❌ REDUNDANT (info is in docs/)"
echo

read -p "Remove redundant documentation? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f CLEANUP_SUMMARY.md STOCK_UNIVERSE_UPDATE.md
    print_status "Removed redundant documentation"
fi

# 7. Move misplaced files to correct locations
echo "📁 Moving misplaced files..."

if [ -f "verify_organization.py" ]; then
    mv verify_organization.py scripts/
    print_status "Moved verify_organization.py to scripts/"
fi

# 8. Clean up Python cache and logs
echo "🧹 Cleaning Python cache and old logs..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true
print_status "Cleaned Python cache and logs"

# 9. Show final clean structure
echo
echo "============================================="
print_status "🎉 REAL CLEANUP COMPLETE!"
echo "============================================="
echo
echo "📁 FINAL CLEAN STRUCTURE:"
echo "├── 🚀 start_complete_system.sh    # ONE startup script"
echo "├── 📊 Core Files:"
echo "│   ├── main.py                    # Basic analysis"
echo "│   ├── main_enhanced.py           # Enhanced analysis"
echo "│   ├── n8n_integration.py         # n8n API server"
echo "│   ├── stock_universe.py          # 269+ stocks"
echo "│   ├── enhanced_yahoo_client.py   # Yahoo Finance client"
echo "│   ├── web_dashboard.py           # Dashboard"
echo "│   ├── yahoo_finance_mcp_server.py # MCP server"
echo "│   └── scheduled_market_alerts.py # Scheduler"
echo "├── 📁 scripts/                    # Management utilities"
echo "├── 📁 tests/                      # Testing"
echo "├── 📁 workflows/                  # n8n workflows"
echo "├── 📁 docs/                       # Documentation"
echo "├── 📁 config/                     # Configuration"
echo "├── 📁 utils/                      # Utilities"
echo "└── 🔒 .env                        # Secrets"
echo
echo "🎯 TO START YOUR SYSTEM:"
echo "   ./start_complete_system.sh"
echo
echo "📊 CURRENT ROOT DIRECTORY:"
ls -la | grep -E '^-' | wc -l | xargs echo "   Files:"
ls -la | grep -E '^d' | wc -l | xargs echo "   Directories:"
echo
print_status "Your system is now truly clean and organized!"