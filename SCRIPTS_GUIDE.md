# 🚀 Scripts Guide - Complete Analysis & Alert System

## Overview

This guide explains all the shell scripts available and how to run the complete analysis pipeline.

---

## 🎯 Master Script (Recommended)

### `run_complete_analysis.sh` ⭐

**The ONE script to run everything!**

This master script runs the entire analysis pipeline in the correct order:

```bash
./run_complete_analysis.sh
```

**What it does:**

1. **🤖 Gemma AI Analysis** (~10 min)
   - Analyzes stocks using AI
   - Generates top 10 picks with reasoning
   - Output: `gemma_top_10_picks.json`

2. **💰 Dividend Stock Scanner** (~10 min)
   - Scans 600+ US & Canadian stocks
   - Finds dividend-paying opportunities
   - Output: `top_50_dividend_stocks.json`

3. **📈 Stock Recommendations**
   - Technical analysis on stock universe
   - Generates BUY and WATCH signals
   - Output: `last_recommendations.json`

4. **📊 Update Streamlit Data**
   - Creates summary for dashboard
   - Output: `streamlit_data_summary.json`

5. **📧 Send Email Alerts**
   - Comprehensive alert to masterai6612@gmail.com
   - Includes all analysis results

6. **📱 Send Telegram Notifications**
   - Real-time alerts to Telegram
   - Includes all analysis results

7. **🚀 Commit & Push to GitHub**
   - Auto-commits data files
   - Pushes to main branch
   - Triggers Streamlit Cloud auto-deploy

**Total Time:** ~20-25 minutes

**Output:**
```
✅ Gemma AI Picks: 10
✅ Dividend Stocks: 120
✅ BUY Signals: 15
✅ WATCH Signals: 25
✅ Email sent
✅ Telegram sent
✅ GitHub pushed
✅ Streamlit deploying
```

---

## 📋 Individual Scripts

### Analysis Scripts

#### 1. `gemma_market_analysis.py`
```bash
python gemma_market_analysis.py
```
- **Purpose:** AI-powered stock analysis
- **Time:** ~10 minutes
- **Output:** `gemma_top_10_picks.json`
- **Features:** AI reasoning, growth potential, technical analysis

#### 2. `dividend_stock_analyzer.py`
```bash
python dividend_stock_analyzer.py
```
- **Purpose:** Scan 600+ stocks for dividend opportunities
- **Time:** ~10 minutes
- **Output:** `top_50_dividend_stocks.json`
- **Features:** Income + growth analysis, 6 categories

#### 3. `current_stock_summary.py`
```bash
python current_stock_summary.py
```
- **Purpose:** Technical analysis and recommendations
- **Time:** ~5 minutes
- **Output:** `last_recommendations.json`
- **Features:** BUY/WATCH signals, RSI, MACD, volume

### Notification Scripts

#### 4. `send_comprehensive_test_email.py`
```bash
python send_comprehensive_test_email.py
```
- **Purpose:** Send test alert (Email + Telegram)
- **Time:** ~10 seconds
- **Includes:** All analysis results, system status
- **Channels:** Email + Telegram

#### 5. `scheduled_market_alerts.py`
```bash
python scheduled_market_alerts.py
```
- **Purpose:** 24/7 market monitoring and alerts
- **Time:** Runs continuously
- **Features:** Pre-market, regular hours, after-hours monitoring

### Update Scripts

#### 6. `update_streamlit_data.py`
```bash
python update_streamlit_data.py
```
- **Purpose:** Update all Streamlit data
- **Time:** ~20 minutes
- **Runs:** Gemma + Dividend + Recommendations
- **Output:** All JSON files + summary

#### 7. `update_and_push_streamlit.sh`
```bash
./update_and_push_streamlit.sh
```
- **Purpose:** Update data and push to GitHub
- **Time:** ~20 minutes
- **Features:** Auto-commit and push

### Setup Scripts

#### 8. `setup_gemma.sh`
```bash
./setup_gemma.sh
```
- **Purpose:** Setup Gemma AI environment
- **Time:** ~5 minutes
- **Features:** Install dependencies, configure API

#### 9. `setup_daily_streamlit_updates.sh`
```bash
./setup_daily_streamlit_updates.sh
```
- **Purpose:** Setup daily auto-updates
- **Time:** ~2 minutes
- **Features:** Configure cron job for daily runs

#### 10. `setup_mcp_agent.sh`
```bash
./setup_mcp_agent.sh
```
- **Purpose:** Setup MCP agent environment
- **Time:** ~5 minutes
- **Features:** Virtual environment, dependencies

### System Scripts

#### 11. `start_complete_system.sh`
```bash
./start_complete_system.sh
```
- **Purpose:** Start all system components
- **Time:** ~1 minute
- **Features:** MCP server, dashboard, alerts

#### 12. `stop_complete_system.sh`
```bash
./stop_complete_system.sh
```
- **Purpose:** Stop all system components
- **Time:** ~10 seconds
- **Features:** Clean shutdown of all services

#### 13. `start_stock_alerts.sh`
```bash
./start_stock_alerts.sh
```
- **Purpose:** Start stock alert monitoring
- **Time:** Runs continuously
- **Features:** 24/7 monitoring

---

## 🔄 Recommended Workflows

### Daily Analysis (Automated)

**Option 1: Use Master Script**
```bash
./run_complete_analysis.sh
```
This is the easiest and most comprehensive option.

**Option 2: Use Update Script**
```bash
python update_streamlit_data.py
```
This runs Gemma + Dividend + Recommendations.

### Quick Test

**Test Email + Telegram:**
```bash
python send_comprehensive_test_email.py
```

### Manual Analysis

**Run specific analyses:**
```bash
# Gemma AI only
python gemma_market_analysis.py

# Dividend stocks only
python dividend_stock_analyzer.py

# Recommendations only
python current_stock_summary.py
```

### Update Dashboard

**Update and deploy:**
```bash
./update_and_push_streamlit.sh
```

---

## 📊 Script Comparison

| Script | Time | Email | Telegram | GitHub | Streamlit |
|--------|------|-------|----------|--------|-----------|
| `run_complete_analysis.sh` | 20-25 min | ✅ | ✅ | ✅ | ✅ |
| `update_streamlit_data.py` | 20 min | ❌ | ❌ | ❌ | ❌ |
| `update_and_push_streamlit.sh` | 20 min | ❌ | ❌ | ✅ | ✅ |
| `send_comprehensive_test_email.py` | 10 sec | ✅ | ✅ | ❌ | ❌ |
| `gemma_market_analysis.py` | 10 min | ❌ | ❌ | ❌ | ❌ |
| `dividend_stock_analyzer.py` | 10 min | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 Use Cases

### I want to run everything
```bash
./run_complete_analysis.sh
```

### I want to test notifications
```bash
python send_comprehensive_test_email.py
```

### I want to update just Gemma AI
```bash
python gemma_market_analysis.py
```

### I want to update just dividend stocks
```bash
python dividend_stock_analyzer.py
```

### I want to update Streamlit without notifications
```bash
python update_streamlit_data.py
git add *.json
git commit -m "Update data"
git push origin main
```

### I want to run 24/7 monitoring
```bash
./start_complete_system.sh
```

---

## 🔧 Prerequisites

### Before Running Any Script

1. **Virtual Environment:**
```bash
source venv_new/bin/activate
```

2. **Environment Variables:**
Ensure `.env` file has:
```
EMAIL_FROM=masterai6612@gmail.com
EMAIL_PASSWORD=your_app_password
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

3. **Dependencies:**
```bash
pip install -r requirements.txt
```

---

## 📁 Output Files

All scripts generate these files:

| File | Generated By | Purpose |
|------|--------------|---------|
| `gemma_top_10_picks.json` | Gemma AI | AI stock picks |
| `top_50_dividend_stocks.json` | Dividend Scanner | Dividend stocks |
| `last_recommendations.json` | Stock Summary | BUY/WATCH signals |
| `streamlit_data_summary.json` | Update Scripts | Dashboard summary |

---

## 🚨 Troubleshooting

### Script won't run
```bash
chmod +x script_name.sh
```

### Virtual environment not found
```bash
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
```

### Email not sending
- Check `.env` file has `EMAIL_PASSWORD`
- Verify Gmail app password is correct
- Check internet connection

### Telegram not sending
- Check `.env` file has `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Verify bot token is valid
- Check internet connection

### Analysis taking too long
- Normal: Gemma (10 min) + Dividend (10 min) = 20 min
- Check internet connection
- Verify yfinance API is accessible

---

## ⏰ Scheduling

### Daily Auto-Run (Recommended)

**Using cron (macOS/Linux):**
```bash
crontab -e
```

Add this line to run daily at 9 AM:
```
0 9 * * * cd /path/to/mcp-stock-alert && ./run_complete_analysis.sh >> logs/daily_run.log 2>&1
```

**Using GitHub Actions:**
Already configured! Runs automatically daily.

---

## 📊 Monitoring

### Check if scripts are running
```bash
ps aux | grep python
```

### View logs
```bash
tail -f scheduled_alerts.log
```

### Check output files
```bash
ls -lh *.json
```

---

## 🎉 Quick Start

**First time setup:**
```bash
# 1. Setup environment
./setup_mcp_agent.sh

# 2. Setup Gemma
./setup_gemma.sh

# 3. Run complete analysis
./run_complete_analysis.sh
```

**Daily use:**
```bash
./run_complete_analysis.sh
```

That's it! 🚀

---

## 📚 Related Documentation

- `README.md` - Main documentation
- `SYSTEM_STATUS.md` - Current system status
- `DIVIDEND_STOCKS_GUIDE.md` - Dividend feature guide
- `GEMMA_SETUP_GUIDE.md` - Gemma AI setup
- `QUICK_START.md` - Quick start guide

---

## 💡 Tips

1. **Run master script daily** for best results
2. **Test notifications** before relying on them
3. **Monitor logs** for errors
4. **Check Streamlit** after each run
5. **Keep .env secure** - never commit it

---

**Last Updated:** November 18, 2025
**Version:** 1.0
**Status:** ✅ All scripts operational
