#!/bin/bash

echo "🚀 Starting Stock Alert System Dashboard"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import flask, psutil" 2>/dev/null || {
    echo "📥 Installing missing dependencies..."
    pip install flask psutil
}

echo "🌐 Starting web dashboard..."
echo "📊 Dashboard will be available at: http://localhost:5001"
echo "🔄 Data updates every 5 minutes (optimized for low API traffic)"
echo "💡 Press Ctrl+C to stop the dashboard"
echo ""

# Start the dashboard
python web_dashboard.py