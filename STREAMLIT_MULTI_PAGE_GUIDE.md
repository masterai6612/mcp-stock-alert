# 📱 Streamlit Multi-Page Dashboard Guide

## 🎯 Overview

Your new Streamlit dashboard has **4 pages** with auto-updating data:

1. **🏠 Dashboard** - Real-time stock monitoring
2. **🤖 Gemma AI Top 10** - AI-powered daily picks
3. **📊 Market Analysis** - Indices, sectors, stock lookup
4. **⚙️ Settings** - Configuration and system status

## 🚀 Quick Start

### Run Locally:
```bash
cd "/Users/monie/Desktop/kiro/mcp-stock-alert copy"
source venv/bin/activate
streamlit run streamlit_app.py
```

Open: http://localhost:8501

### Deploy to Streamlit Cloud:
1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Select repository: `masterai6612/mcp-stock-alert`
4. Main file: `streamlit_app.py`
5. Deploy!

## 📅 Auto-Update Setup

### Option 1: Automated Daily Updates (Recommended)

Run the setup script:
```bash
./setup_daily_updates.sh
```

This will:
- ✅ Run Gemma AI analysis every weekday at 7 AM
- ✅ Update recommendations automatically
- ✅ Create daily summary
- ✅ Log all updates to `streamlit_update.log`

### Option 2: Manual Updates

Update data anytime:
```bash
python update_streamlit_data.py
```

### Option 3: GitHub Actions (For Cloud Deployment)

Create `.github/workflows/update-data.yml`:
```yaml
name: Update Streamlit Data

on:
  schedule:
    - cron: '0 7 * * 1-5'  # 7 AM weekdays
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Update data
        run: python update_streamlit_data.py
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add gemma_top_10_picks.json last_recommendations.json streamlit_data_summary.json
          git commit -m "Auto-update data" || exit 0
          git push
```

## 📊 Page Details

### 1. 🏠 Dashboard Page

**Features:**
- Market status (OPEN/CLOSED)
- System health check
- Recent BUY/WATCH signals
- Top stocks performance table
- Manual refresh button

**Data Source:**
- `last_recommendations.json` - From scheduled alerts
- Real-time Yahoo Finance data

**Updates:**
- Automatically when you refresh
- Data from scheduled_market_alerts.py

### 2. 🤖 Gemma AI Top 10 Page

**Features:**
- Top 10 AI-selected picks
- AI scores (0-100)
- Detailed analysis for each pick
- Growth potential metrics
- Performance statistics
- Run analysis button
- Download JSON

**Data Source:**
- `gemma_top_10_picks.json` - From Gemma analysis

**Updates:**
- Daily at 7 AM (if cron is set up)
- Manual: Click "Run Analysis Now"
- Or run: `python gemma_market_analysis.py`

### 3. 📊 Market Analysis Page

**Features:**
- Major indices (S&P 500, Dow, NASDAQ, Russell 2000)
- Sector performance (8 sectors)
- Stock lookup tool
- 3-month price charts
- Growth requirement check

**Data Source:**
- Real-time Yahoo Finance API

**Updates:**
- Real-time on page load
- No caching needed

### 4. ⚙️ Settings Page

**Features:**
- System status monitoring
- Email configuration
- Growth filter settings
- Data management (download JSON files)
- System information
- Quick actions
- Documentation links

**Data Source:**
- System files and processes

## 🔄 Data Flow

```
Daily at 7 AM:
1. update_streamlit_data.py runs
2. Executes gemma_market_analysis.py
3. Updates gemma_top_10_picks.json
4. Checks last_recommendations.json
5. Creates streamlit_data_summary.json
6. Logs to streamlit_update.log

Streamlit Dashboard:
1. Reads JSON files
2. Fetches real-time data from Yahoo Finance
3. Displays in multi-page interface
4. Users can manually refresh or run analysis
```

## 📁 File Structure

```
mcp-stock-alert/
├── streamlit_app.py              # Main entry point
├── pages/
│   ├── __init__.py
│   ├── dashboard.py              # Dashboard page
│   ├── gemma_picks.py            # Gemma AI page
│   ├── market_analysis.py        # Market analysis page
│   └── settings.py               # Settings page
├── update_streamlit_data.py      # Auto-update script
├── setup_daily_updates.sh        # Cron setup
├── gemma_top_10_picks.json       # Gemma AI data
├── last_recommendations.json     # Alert system data
├── streamlit_data_summary.json   # Daily summary
└── streamlit_update.log          # Update logs
```

## 🌐 Deployment Options

### Local (Development):
```bash
streamlit run streamlit_app.py
```
- ✅ Full features
- ✅ Can run analysis
- ✅ Access to local files

### Streamlit Cloud (Production):
1. Push to GitHub
2. Deploy on share.streamlit.io
3. Set up GitHub Actions for auto-updates
4. ⚠️ Cannot run local analysis (use GitHub Actions)

### Heroku/AWS/GCP:
- Deploy as container
- Set up cron jobs
- Configure environment variables

## 🔧 Configuration

### Update Frequency:
Edit `setup_daily_updates.sh`:
```bash
# Change from 7 AM to 9 AM:
0 9 * * 1-5 cd $SCRIPT_DIR && ...

# Run twice daily (7 AM and 2 PM):
0 7,14 * * 1-5 cd $SCRIPT_DIR && ...
```

### Email Alerts:
Already configured in `.env`:
- EMAIL_FROM
- EMAIL_PASSWORD
- EMAIL_TO

### Growth Filter:
Currently hardcoded to 7%
- Modify in `current_stock_summary.py`
- Modify in `scheduled_market_alerts.py`

## 🐛 Troubleshooting

### Issue: Pages not loading
**Solution:** Check if `pages/` directory exists with all files

### Issue: No Gemma data
**Solution:** Run `python gemma_market_analysis.py` manually

### Issue: Cron not working
**Solution:** 
- Check: `crontab -l`
- View logs: `tail -f streamlit_update.log`
- Verify paths in cron job

### Issue: Streamlit Cloud can't run analysis
**Solution:** Use GitHub Actions to update data, then commit to repo

## 📊 Monitoring

### Check Update Logs:
```bash
tail -f streamlit_update.log
```

### Check Cron Status:
```bash
crontab -l
```

### Check Data Files:
```bash
ls -lh gemma_top_10_picks.json last_recommendations.json
```

### Test Update Script:
```bash
python update_streamlit_data.py
```

## 🎯 Best Practices

1. **Run updates before market opens** (7 AM)
2. **Check logs daily** for errors
3. **Backup JSON files** periodically
4. **Monitor system resources** if running locally
5. **Use GitHub Actions** for cloud deployment

## 🆘 Support

### Common Commands:
```bash
# Start Streamlit
streamlit run streamlit_app.py

# Update data manually
python update_streamlit_data.py

# Setup auto-updates
./setup_daily_updates.sh

# View logs
tail -f streamlit_update.log

# Test Gemma
python test_gemma_system.py
```

### Files to Check:
- `streamlit_update.log` - Update logs
- `gemma_top_10_picks.json` - AI picks
- `last_recommendations.json` - Alert data
- `streamlit_data_summary.json` - Summary

## 🎉 Success!

Your multi-page Streamlit dashboard is ready with:
- ✅ 4 interactive pages
- ✅ Auto-updating data
- ✅ Gemma AI integration
- ✅ Real-time market data
- ✅ Daily cron jobs
- ✅ Cloud deployment ready

Access it at: http://localhost:8501 (local) or your Streamlit Cloud URL!
