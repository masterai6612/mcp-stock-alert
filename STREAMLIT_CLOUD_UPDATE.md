# 🌐 Streamlit Cloud Update Instructions

## Your App URL
https://mcp-stock-alert-kiro-enhanced.streamlit.app/

## ✅ What Was Updated

### New Multi-Page App Structure:
1. **🏠 Dashboard** - Real-time stock monitoring
2. **🤖 Gemma AI Top 10** - AI-powered daily picks
3. **📊 Market Analysis** - Market indices and stock lookup
4. **⚙️ Settings** - Configuration and downloads

### Files Pushed to GitHub:
- ✅ `streamlit_app.py` - New main entry point
- ✅ `pages/` directory - All 4 pages
- ✅ `gemma_top_10_picks.json` - Sample Gemma data
- ✅ `requirements_streamlit.txt` - Dependencies
- ✅ `.streamlit/config.toml` - App configuration

## 🔄 Streamlit Cloud Will Auto-Update

Your app should automatically redeploy when it detects the new commits. This usually takes 2-5 minutes.

## 🎯 Update Streamlit Cloud Settings

Go to: https://share.streamlit.io/

1. **Find your app:** mcp-stock-alert
2. **Click Settings (⚙️)**
3. **Update these settings:**

### Main File Path:
Change from: `streamlit_dashboard.py`  
Change to: **`streamlit_app.py`**

### Python Version:
**3.9** or higher

### Requirements File:
**`requirements_streamlit.txt`**

## 📊 Data Updates for Cloud

Since Streamlit Cloud can't run local scripts, you have two options:

### Option 1: GitHub Actions (Recommended)

Create `.github/workflows/update-data.yml`:

```yaml
name: Update Streamlit Data

on:
  schedule:
    - cron: '0 7 * * 1-5'  # 7 AM weekdays EST
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install yfinance pandas python-dotenv
      
      - name: Update Gemma data
        env:
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: |
          python gemma_market_analysis.py || echo "Gemma analysis skipped"
      
      - name: Commit and push
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add gemma_top_10_picks.json last_recommendations.json streamlit_data_summary.json || true
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto-update data [skip ci]"
          git push || true
```

### Option 2: Manual Updates

Run locally and push:
```bash
python update_streamlit_data.py
git add gemma_top_10_picks.json last_recommendations.json
git commit -m "Update data"
git push
```

## 🔐 Add Secrets (Optional)

In Streamlit Cloud settings, add secrets:

```toml
# .streamlit/secrets.toml format
EMAIL_FROM = "masterai6612@gmail.com"
EMAIL_PASSWORD = "your_password"
```

## ✅ Verify Deployment

1. Wait 2-5 minutes for auto-deploy
2. Visit: https://mcp-stock-alert-kiro-enhanced.streamlit.app/
3. You should see the new multi-page app
4. Navigate between pages using the sidebar

## 🐛 Troubleshooting

### Issue: App shows old version
**Solution:** 
- Go to Streamlit Cloud dashboard
- Click "Reboot app"
- Or change main file to `streamlit_app.py` in settings

### Issue: Import errors
**Solution:**
- Check `requirements_streamlit.txt` is being used
- Verify all dependencies are listed

### Issue: No Gemma data showing
**Solution:**
- The `gemma_top_10_picks.json` file is included
- Set up GitHub Actions for automatic updates
- Or manually update and push

### Issue: Pages not loading
**Solution:**
- Verify `pages/` directory is in GitHub
- Check all page files are committed
- Reboot the app

## 📱 App Features on Cloud

### ✅ Works on Cloud:
- Dashboard with real-time data
- Market analysis
- Stock lookup
- Display Gemma picks (from JSON)
- Settings page
- Manual refresh

### ⚠️ Limited on Cloud:
- Cannot run Gemma analysis directly
- Cannot check local scheduler status
- Use GitHub Actions for data updates

## 🎉 Success Checklist

- [ ] Main file changed to `streamlit_app.py`
- [ ] App auto-deployed (wait 2-5 minutes)
- [ ] Can access all 4 pages
- [ ] Gemma AI page shows data
- [ ] Dashboard shows recommendations
- [ ] Market analysis works
- [ ] (Optional) GitHub Actions set up

## 📧 Support

If you need help:
1. Check Streamlit Cloud logs
2. Verify GitHub commits are pushed
3. Try rebooting the app
4. Check main file path in settings

Your app should be live at:
**https://mcp-stock-alert-kiro-enhanced.streamlit.app/**

Enjoy your new multi-page dashboard! 🚀
