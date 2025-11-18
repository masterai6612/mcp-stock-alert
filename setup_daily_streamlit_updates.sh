#!/bin/bash

# Setup Daily Streamlit Data Updates
# Configures cron to update Streamlit data daily and push to GitHub

echo "📅 Setting up daily Streamlit data updates"
echo "=" * 60

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📁 Project directory: $SCRIPT_DIR"
echo ""

# Create update and push script
cat > "$SCRIPT_DIR/update_and_push_streamlit.sh" << 'EOF'
#!/bin/bash

# Update Streamlit data and push to GitHub
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run update
python update_streamlit_data.py

# Check if there are changes
if git diff --quiet gemma_top_10_picks.json streamlit_data_summary.json; then
    echo "No changes to commit"
    exit 0
fi

# Commit and push
git add gemma_top_10_picks.json streamlit_data_summary.json last_recommendations.json
git commit -m "🤖 Auto-update Streamlit data - $(date '+%Y-%m-%d %H:%M')"
git push origin enhanced-stock-alerts_kiro

echo "✅ Data updated and pushed to GitHub"
EOF

chmod +x "$SCRIPT_DIR/update_and_push_streamlit.sh"

echo "✅ Created update_and_push_streamlit.sh"
echo ""

# Create cron job
CRON_JOB="0 7 * * * cd $SCRIPT_DIR && ./update_and_push_streamlit.sh >> streamlit_update.log 2>&1"

echo "📝 Cron job to be added:"
echo "$CRON_JOB"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "update_and_push_streamlit.sh"; then
    echo "⚠️  Cron job already exists"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
    
    # Remove old cron job
    crontab -l | grep -v "update_and_push_streamlit.sh" | crontab -
    echo "✅ Removed old cron job"
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "📅 Schedule: Every day at 7:00 AM"
    echo "📊 Updates: Gemma AI picks + Recommendations"
    echo "🚀 Auto-push: To GitHub (triggers Streamlit Cloud deploy)"
    echo "📝 Log file: streamlit_update.log"
    echo ""
    echo "🔍 To view current cron jobs:"
    echo "   crontab -l"
    echo ""
    echo "📊 To view update logs:"
    echo "   tail -f streamlit_update.log"
    echo ""
    echo "🗑️  To remove this cron job:"
    echo "   crontab -e"
    echo "   (then delete the line with update_and_push_streamlit.sh)"
    echo ""
    echo "✅ Setup complete!"
else
    echo "❌ Failed to add cron job"
    exit 1
fi
