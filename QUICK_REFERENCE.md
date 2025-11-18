# 🚀 Quick Reference Card

## ONE Command to Rule Them All

```bash
./run_complete_analysis.sh
```

**This runs EVERYTHING:**
- ✅ Gemma AI Analysis
- ✅ Dividend Stock Scanner (600+ stocks)
- ✅ Stock Recommendations
- ✅ Email Alerts
- ✅ Telegram Notifications
- ✅ GitHub Push (auto-deploys Streamlit)

**Time:** 20-25 minutes

---

## Quick Commands

### Run Complete Analysis
```bash
./run_complete_analysis.sh
```

### Test Notifications
```bash
python send_comprehensive_test_email.py
```

### Update Gemma AI Only
```bash
python gemma_market_analysis.py
```

### Update Dividend Stocks Only
```bash
python dividend_stock_analyzer.py
```

### Update All Data (No Notifications)
```bash
python update_streamlit_data.py
```

---

## What Gets Generated

| File | Contains |
|------|----------|
| `gemma_top_10_picks.json` | AI stock picks |
| `top_50_dividend_stocks.json` | Dividend stocks |
| `last_recommendations.json` | BUY/WATCH signals |
| `streamlit_data_summary.json` | Dashboard data |

---

## Where Things Go

- **📧 Email:** masterai6612@gmail.com
- **📱 Telegram:** Chat ID 7208554751
- **🌐 Streamlit:** https://mcp-stock-alert-kiro-enhanced.streamlit.app/
- **💻 GitHub:** https://github.com/masterai6612/mcp-stock-alert

---

## Troubleshooting

### Script won't run
```bash
chmod +x run_complete_analysis.sh
```

### Need virtual environment
```bash
source venv_new/bin/activate
```

### Check if it worked
```bash
ls -lh *.json
```

---

## Daily Workflow

**Morning:**
```bash
./run_complete_analysis.sh
```

**Check results:**
1. Check email
2. Check Telegram
3. Visit Streamlit dashboard

**Done!** 🎉

---

## Full Documentation

- `SCRIPTS_GUIDE.md` - Complete scripts guide
- `SYSTEM_STATUS.md` - System status
- `DIVIDEND_STOCKS_GUIDE.md` - Dividend feature
- `README.md` - Main documentation

---

**Last Updated:** November 18, 2025
