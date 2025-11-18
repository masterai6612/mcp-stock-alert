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
