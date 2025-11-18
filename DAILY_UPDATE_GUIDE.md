# 📅 Daily Streamlit Update Guide

## 🎯 Three Ways to Auto-Update Daily

Your Streamlit Cloud app can be updated automatically using any of these methods:

### ✅ Option 1: GitHub Actions (Recommended for Cloud)

**Status:** Already configured! ✅

**How it works:**
- Runs every weekday at 7 AM EST (12 PM UTC)
- Updates Gemma AI picks
- Commits to GitHub
- Streamlit Cloud auto-deploys

**Manual trigger:**
1. Go to: https://github.com/masterai6612/mcp-stock-alert/actions
2. Click "Update Streamlit Data"
3. Click "Run workflow"
4. Select branch: `enhanced-stock-alerts_kiro`
5. Click "Run workflow"

**Configuration file:** `.github/workflows/update-streamlit-data.yml`

### ✅ Option 2: Local Cron Job (Recommended for Local)

**Setup:**
```bash
./setup_daily_streamlit_updates.sh
```

**What it does:**
- Runs daily at 7 AM on your Mac
- Updates data locally
- Commits and pushes to GitHub
- Triggers Streamlit Cloud deploy

**View logs:**
```bash
tail -f streamlit_update.log
```

**Check cron jobs:**
```bash
crontab -l
```

### ✅ Option 3: MCP Tool (Manual/On-Demand)

**Setup MCP Server:**

Add to `.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "streamlit-updater": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/mcp_streamlit_updater.py"],
      "disabled": false
    }
  }
}
```

**Available MCP Tools:**
1. `update_streamlit_data` - Update data immediately
2. `get_streamlit_status` - Check current data status
3. `trigger_github_workflow` - Trigger GitHub Actions

## 📊 What Gets Updated

Each update refreshes:
- ✅ `gemma_top_10_picks.json` - AI-powered Top 10 picks
- ✅ `streamlit_data_summary.json` - Update timestamp and stats
- ✅ `last_recommendations.json` - Latest BUY/WATCH signals

## 🔄 Update Flow

```
Daily at 7 AM:
1. Run gemma_market_analysis.py
2. Generate Top 10 picks with AI scoring
3. Update JSON files
4. Commit to GitHub
5. Push to remote
6. Streamlit Cloud detects change
7. Auto-redeploys app (2-5 minutes)
8. Users see fresh data
```

## 🚀 Quick Commands

### Manual Update (Local):
```bash
python update_streamlit_data.py
git add gemma_top_10_picks.json streamlit_data_summary.json
git commit -m "Update data"
git push
```

### Check Last Update:
```bash
cat streamlit_data_summary.json
```

### View GitHub Actions Status:
```bash
gh run list --workflow=update-streamlit-data.yml
```

## 📅 Schedule Comparison

| Method | Frequency | Requires | Auto-Push | Best For |
|--------|-----------|----------|-----------|----------|
| GitHub Actions | Daily 7 AM EST | GitHub repo | ✅ Yes | Cloud deployment |
| Local Cron | Daily 7 AM | Mac running | ✅ Yes | Local development |
| MCP Tool | On-demand | MCP setup | ❌ Manual | Testing/debugging |

## 🔧 Troubleshooting

### GitHub Actions not running:
1. Check: https://github.com/masterai6612/mcp-stock-alert/actions
2. Verify workflow file exists
3. Check branch is `enhanced-stock-alerts_kiro` or `main`
4. Manually trigger workflow

### Local cron not working:
```bash
# Check if cron job exists
crontab -l

# View logs
tail -f streamlit_update.log

# Test script manually
./update_and_push_streamlit.sh
```

### Streamlit Cloud not updating:
1. Check GitHub has new commits
2. Wait 2-5 minutes for auto-deploy
3. Check Streamlit Cloud logs
4. Try manual reboot in Streamlit dashboard

## 📱 Monitoring

### Check if updates are working:
1. Visit: https://mcp-stock-alert-kiro-enhanced.streamlit.app/
2. Look at "Last Updated" timestamp
3. Should show current date

### GitHub Actions logs:
https://github.com/masterai6612/mcp-stock-alert/actions

### Local logs:
```bash
tail -f streamlit_update.log
```

## ✅ Recommended Setup

**For Production (Streamlit Cloud):**
- ✅ Use GitHub Actions (already configured)
- ✅ Runs automatically every weekday
- ✅ No local machine needed

**For Development (Local):**
- ✅ Use local cron job
- ✅ Keeps your local data fresh
- ✅ Auto-pushes to GitHub

**For Testing:**
- ✅ Use MCP tool or manual commands
- ✅ Update on-demand
- ✅ Test before committing

## 🎉 Current Status

✅ **GitHub Actions:** Configured and ready  
✅ **Update Script:** `update_streamlit_data.py` working  
✅ **Data Files:** All present and updated  
✅ **Streamlit Cloud:** Deployed and accessible  

**Your app will update automatically every weekday at 7 AM EST!** 🚀

## 📝 Next Steps

1. **Verify GitHub Actions:**
   - Go to Actions tab
   - Check if workflow is enabled
   - Manually trigger once to test

2. **Optional - Setup Local Cron:**
   ```bash
   ./setup_daily_streamlit_updates.sh
   ```

3. **Monitor:**
   - Check Streamlit app daily
   - Verify "Last Updated" timestamp
   - Review GitHub Actions logs

**Everything is ready for daily auto-updates!** 🎉
