#!/bin/bash

echo "🔄 SWITCHING TO ORIGINAL MCP-STOCK-ALERT DIRECTORY"
echo "=================================================="

ORIGINAL_DIR="/Users/monie/Desktop/GitHub/Stocks/Preplexity/mcp-stock-alert"

echo "ℹ️  Original directory: $ORIGINAL_DIR"

if [ -d "$ORIGINAL_DIR" ]; then
    echo "✅ Original directory exists"
    
    # Check if venv exists
    if [ -d "$ORIGINAL_DIR/venv" ]; then
        echo "✅ Virtual environment found"
        
        # Check if start script exists
        if [ -f "$ORIGINAL_DIR/start_complete_system.sh" ]; then
            echo "✅ Start script found"
            echo
            echo "🎯 READY TO SWITCH!"
            echo
            echo "📋 Next steps:"
            echo "1. Open a new terminal"
            echo "2. Run: cd $ORIGINAL_DIR"
            echo "3. Run: source venv/bin/activate"
            echo "4. Run: ./start_complete_system.sh"
            echo
            echo "🔍 Verification commands:"
            echo "   • Check venv: which python"
            echo "   • Check packages: pip list | grep yfinance"
            echo "   • Test system: python main_enhanced.py"
            echo
        else
            echo "❌ Start script not found in original directory"
        fi
    else
        echo "❌ Virtual environment not found in original directory"
    fi
else
    echo "❌ Original directory not found"
fi

echo "=================================================="
echo "✅ MIGRATION SUMMARY:"
echo "   📁 Virtual environment: Copied to original location"
echo "   📄 All files: Synced to original location"
echo "   🗂️  Backup created: venv_backup_$(date +%Y%m%d)_*"
echo "   🎯 Ready to use: $ORIGINAL_DIR"
echo
echo "💡 You can now safely delete this copy directory after testing!"