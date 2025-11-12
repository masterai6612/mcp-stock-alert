#!/bin/bash

# Setup Daily Auto-Updates for Streamlit Dashboard
# This script configures cron to update data daily

echo "📅 Setting up daily auto-updates for Streamlit"
echo "=" * 60

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📁 Project directory: $SCRIPT_DIR"
echo ""

# Create cron job
CRON_JOB="0 7 * * 1-5 cd $SCRIPT_DIR && source venv/bin/activate && python update_streamlit_data.py >> streamlit_update.log 2>&1"

echo "📝 Cron job to be added:"
echo "$CRON_JOB"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "update_streamlit_data.py"; then
    echo "⚠️  Cron job already exists"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
    
    # Remove old cron job
    crontab -l | grep -v "update_streamlit_data.py" | crontab -
    echo "✅ Removed old cron job"
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "📅 Schedule: Every weekday at 7:00 AM"
    echo "📊 Updates: Gemma AI picks + Recommendations"
    echo "📝 Log file: streamlit_update.log"
    echo ""
    echo "🔍 To view current cron jobs:"
    echo "   crontab -l"
    echo ""
    echo "🗑️  To remove this cron job:"
    echo "   crontab -e"
    echo "   (then delete the line with update_streamlit_data.py)"
    echo ""
    echo "✅ Setup complete!"
else
    echo "❌ Failed to add cron job"
    exit 1
fi
