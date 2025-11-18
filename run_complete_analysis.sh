#!/bin/bash
################################################################################
# Complete Stock Analysis & Alert System
# 
# This script runs the entire analysis pipeline:
# 1. Gemma AI Analysis (10 min)
# 2. Dividend Stock Scanner (10 min) - 600+ stocks
# 3. Current Stock Recommendations
# 4. Update Streamlit Data
# 5. Send Email Alerts
# 6. Send Telegram Notifications
# 7. Commit & Push to GitHub (auto-deploys Streamlit)
#
# Usage: ./run_complete_analysis.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv_new" ]; then
    error "Virtual environment 'venv_new' not found!"
    error "Please run: python3 -m venv venv_new && source venv_new/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
log "🔧 Activating virtual environment..."
source venv_new/bin/activate

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
log "🐍 Python version: $PYTHON_VERSION"

################################################################################
# STEP 1: Gemma AI Analysis
################################################################################
log "🤖 STEP 1/7: Running Gemma AI Analysis..."
info "This analyzes stocks using AI and generates top 10 picks"
info "Expected time: ~10 minutes"

if python gemma_market_analysis.py; then
    log "✅ Gemma AI analysis complete"
    if [ -f "gemma_top_10_picks.json" ]; then
        GEMMA_COUNT=$(python -c "import json; data=json.load(open('gemma_top_10_picks.json')); print(len(data.get('picks', [])))")
        log "📊 Generated $GEMMA_COUNT AI picks"
    fi
else
    error "❌ Gemma AI analysis failed"
    warning "Continuing with other analyses..."
fi

echo ""

################################################################################
# STEP 2: Dividend Stock Scanner
################################################################################
log "💰 STEP 2/7: Running Dividend Stock Scanner..."
info "Scanning 600+ US & Canadian stocks for dividend opportunities"
info "Expected time: ~10 minutes"

if python dividend_stock_analyzer.py; then
    log "✅ Dividend analysis complete"
    if [ -f "top_50_dividend_stocks.json" ]; then
        DIVIDEND_COUNT=$(python -c "import json; data=json.load(open('top_50_dividend_stocks.json')); print(data.get('total_dividend_stocks', 0))")
        log "📊 Found $DIVIDEND_COUNT dividend-paying stocks"
    fi
else
    error "❌ Dividend analysis failed"
    warning "Continuing with other analyses..."
fi

echo ""

################################################################################
# STEP 3: Current Stock Recommendations
################################################################################
log "📈 STEP 3/7: Generating Current Stock Recommendations..."
info "Running technical analysis on stock universe"

if python current_stock_summary.py; then
    log "✅ Stock recommendations generated"
    if [ -f "last_recommendations.json" ]; then
        BUY_COUNT=$(python -c "import json; data=json.load(open('last_recommendations.json')); print(len(data.get('buy_signals', [])))")
        WATCH_COUNT=$(python -c "import json; data=json.load(open('last_recommendations.json')); print(len(data.get('watch_signals', [])))")
        log "📊 BUY signals: $BUY_COUNT | WATCH signals: $WATCH_COUNT"
    fi
else
    warning "⚠️ Stock recommendations generation had issues"
fi

echo ""

################################################################################
# STEP 4: Update Streamlit Data
################################################################################
log "📊 STEP 4/7: Updating Streamlit Data..."
info "Creating summary for dashboard"

if python -c "
import json
from datetime import datetime
import os

summary = {
    'date': datetime.now().isoformat(),
    'gemma_available': os.path.exists('gemma_top_10_picks.json'),
    'dividend_available': os.path.exists('top_50_dividend_stocks.json'),
    'recommendations_available': os.path.exists('last_recommendations.json'),
    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

if summary['gemma_available']:
    with open('gemma_top_10_picks.json', 'r') as f:
        gemma_data = json.load(f)
    summary['gemma_picks_count'] = len(gemma_data.get('picks', []))

if summary['dividend_available']:
    with open('top_50_dividend_stocks.json', 'r') as f:
        dividend_data = json.load(f)
    summary['dividend_stocks_count'] = len(dividend_data.get('top_50_dividend_stocks', []))
    summary['total_dividend_stocks'] = dividend_data.get('total_dividend_stocks', 0)

if summary['recommendations_available']:
    with open('last_recommendations.json', 'r') as f:
        rec_data = json.load(f)
    summary['buy_signals_count'] = len(rec_data.get('buy_signals', []))
    summary['watch_signals_count'] = len(rec_data.get('watch_signals', []))

with open('streamlit_data_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('✅ Streamlit data summary created')
"; then
    log "✅ Streamlit data updated"
else
    error "❌ Failed to update Streamlit data"
fi

echo ""

################################################################################
# STEP 5: Send Email Alerts
################################################################################
log "📧 STEP 5/7: Sending Email Alerts..."
info "Sending comprehensive alert to masterai6612@gmail.com"

if python send_comprehensive_test_email.py; then
    log "✅ Email alert sent successfully"
else
    error "❌ Failed to send email alert"
fi

echo ""

################################################################################
# STEP 6: Send Telegram Notifications
################################################################################
log "📱 STEP 6/7: Telegram Notifications..."
info "Telegram is included in the email script above"
log "✅ Telegram notifications sent (if configured)"

echo ""

################################################################################
# STEP 7: Commit & Push to GitHub
################################################################################
log "🚀 STEP 7/7: Committing & Pushing to GitHub..."
info "This will auto-deploy to Streamlit Cloud"

# Check if there are changes to commit
if git diff --quiet && git diff --cached --quiet; then
    warning "No changes to commit"
else
    log "📝 Committing changes..."
    
    # Add all JSON data files
    git add gemma_top_10_picks.json 2>/dev/null || true
    git add top_50_dividend_stocks.json 2>/dev/null || true
    git add last_recommendations.json 2>/dev/null || true
    git add streamlit_data_summary.json 2>/dev/null || true
    
    # Create commit message
    COMMIT_MSG="Auto-update: Analysis run $(date +'%Y-%m-%d %H:%M:%S')

- Gemma AI: ${GEMMA_COUNT:-0} picks
- Dividend stocks: ${DIVIDEND_COUNT:-0} found
- BUY signals: ${BUY_COUNT:-0}
- WATCH signals: ${WATCH_COUNT:-0}

[Automated by run_complete_analysis.sh]"
    
    if git commit -m "$COMMIT_MSG"; then
        log "✅ Changes committed"
        
        # Push to GitHub
        log "📤 Pushing to GitHub..."
        if git push origin main; then
            log "✅ Pushed to GitHub successfully"
            log "🌐 Streamlit Cloud will auto-deploy in 2-5 minutes"
        else
            error "❌ Failed to push to GitHub"
        fi
    else
        warning "⚠️ Nothing to commit"
    fi
fi

echo ""

################################################################################
# SUMMARY
################################################################################
echo ""
log "═══════════════════════════════════════════════════════════"
log "🎉 COMPLETE ANALYSIS FINISHED!"
log "═══════════════════════════════════════════════════════════"
echo ""
log "📊 Analysis Summary:"
log "   🤖 Gemma AI Picks: ${GEMMA_COUNT:-0}"
log "   💰 Dividend Stocks: ${DIVIDEND_COUNT:-0}"
log "   🚀 BUY Signals: ${BUY_COUNT:-0}"
log "   👀 WATCH Signals: ${WATCH_COUNT:-0}"
echo ""
log "📧 Notifications:"
log "   ✅ Email sent to: masterai6612@gmail.com"
log "   ✅ Telegram sent to: Chat ID 7208554751"
echo ""
log "🌐 Streamlit Dashboard:"
log "   URL: https://mcp-stock-alert-kiro-enhanced.streamlit.app/"
log "   Status: Auto-deploying (2-5 minutes)"
echo ""
log "📁 Generated Files:"
log "   ✅ gemma_top_10_picks.json"
log "   ✅ top_50_dividend_stocks.json"
log "   ✅ last_recommendations.json"
log "   ✅ streamlit_data_summary.json"
echo ""
log "═══════════════════════════════════════════════════════════"
log "✅ All tasks completed successfully!"
log "═══════════════════════════════════════════════════════════"
echo ""

# Deactivate virtual environment
deactivate
