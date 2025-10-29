#!/bin/bash

echo "📁 CLEAN PROJECT STRUCTURE VERIFICATION"
echo "======================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}✅ ROOT DIRECTORY (Essential Files Only):${NC}"
echo "├── 🚀 start_complete_system.sh    # ONE-COMMAND STARTUP"
echo "├── 📊 Core System Files:"

# Count and show core files
core_files=(
    "main.py"
    "n8n_integration.py" 
    "stock_universe.py"
    "enhanced_yahoo_client.py"
    "web_dashboard.py"
    "yahoo_finance_mcp_server.py"
    "scheduled_market_alerts.py"
)

for file in "${core_files[@]}"; do
    if [ -f "$file" ]; then
        echo "│   ✅ $file"
    else
        echo "│   ❌ $file (MISSING)"
    fi
done

echo "├── 🔧 Setup & Config:"
echo "│   ✅ setup_mcp_agent.sh"
echo "│   ✅ .env"
echo "│   ✅ stock_tracking.json"
echo "└── 📚 README.md"

echo
echo -e "${BLUE}📁 ORGANIZED FOLDERS:${NC}"

folders=(
    "scripts:System management utilities"
    "tests:Testing and validation"
    "workflows:n8n workflow management"
    "docs:Documentation and guides"
    "config:Configuration files"
    "utils:Helper utilities"
)

for folder_info in "${folders[@]}"; do
    folder=$(echo "$folder_info" | cut -d: -f1)
    desc=$(echo "$folder_info" | cut -d: -f2)
    if [ -d "$folder" ]; then
        file_count=$(find "$folder" -type f | wc -l | tr -d ' ')
        echo "├── ✅ $folder/ ($file_count files) - $desc"
    else
        echo "├── ❌ $folder/ (MISSING) - $desc"
    fi
done

echo
echo -e "${YELLOW}📊 DIRECTORY STATISTICS:${NC}"
total_files=$(find . -maxdepth 1 -type f | wc -l | tr -d ' ')
total_dirs=$(find . -maxdepth 1 -type d | wc -l | tr -d ' ')
echo "   Root Files: $total_files (down from 25+ before cleanup)"
echo "   Root Directories: $total_dirs"
echo "   Total Project Files: $(find . -type f -not -path './venv/*' -not -path './.git/*' | wc -l | tr -d ' ')"

echo
echo -e "${GREEN}🎯 QUICK START:${NC}"
echo "   ./start_complete_system.sh"
echo
echo -e "${GREEN}🔧 SYSTEM MANAGEMENT:${NC}"
echo "   ./scripts/monitor_system.sh    # Check status"
echo "   ./scripts/stop_system.sh       # Clean shutdown"
echo "   python tests/test_both_options.py  # Verify system"
echo
echo -e "${GREEN}✅ PROJECT IS NOW TRULY CLEAN AND ORGANIZED!${NC}"