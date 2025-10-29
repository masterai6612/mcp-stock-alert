#!/bin/bash

echo "🚀 Starting Stock Alert Dashboard (Production)"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
python -c "import flask, psutil, gunicorn" 2>/dev/null || {
    echo "📥 Installing missing dependencies..."
    pip install flask psutil gunicorn
}

echo "🛡️  Starting with Gunicorn WSGI server..."
echo "📊 Dashboard: http://localhost:5001"
echo "🔄 Auto-updates: Every 5 minutes (optimized for low API traffic)"
echo "💡 Press Ctrl+C to stop"
echo ""

# Start with configuration file
gunicorn --config gunicorn.conf.py web_dashboard:app