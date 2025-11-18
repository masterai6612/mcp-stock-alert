# 🚀 Deploy to Streamlit Cloud

## 📋 Files Needed for Deployment

1. **Main App:** `streamlit_dashboard.py`
2. **Requirements:** `requirements_streamlit.txt`
3. **Optional:** `last_recommendations.json` (for showing recent signals)

## 🌐 Deployment Steps

### Step 1: Push to GitHub
Make sure these files are in your GitHub repository:
```bash
git add streamlit_dashboard.py requirements_streamlit.txt
git commit -m "Add Streamlit dashboard for cloud deployment"
git push
```

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `masterai6612/mcp-stock-alert`
5. Branch: `enhanced-stock-alerts_kiro` (or your main branch)
6. Main file path: `streamlit_dashboard.py`
7. Click "Deploy"

### Step 3: Configuration (Optional)

If you want to show live recommendations, you can:
1. Upload `last_recommendations.json` to your repo
2. The dashboard will automatically read it

## 📊 What the Dashboard Shows

### On Streamlit Cloud:
- ✅ Top stocks with real-time prices
- ✅ 7% growth filter status
- ✅ Market status
- ✅ Stock performance metrics
- ⚠️ Recent recommendations (if JSON file exists)

### Limitations on Cloud:
- ❌ Cannot check if local scheduler is running
- ❌ Cannot send emails directly
- ❌ No real-time monitoring (data updates on refresh)

### On Local Machine:
- ✅ All cloud features PLUS:
- ✅ Check scheduler status
- ✅ Real-time monitoring
- ✅ Recent recommendations from local files

## 🔧 Local Testing

Before deploying, test locally:
```bash
cd "/Users/monie/Desktop/kiro/mcp-stock-alert copy"
source venv/bin/activate
pip install streamlit
streamlit run streamlit_dashboard.py
```

Open: http://localhost:8501

## 📝 Environment Variables (Optional)

If you want to add email configuration on Streamlit Cloud:
1. Go to your app settings
2. Add secrets in "Secrets" section:
```toml
EMAIL_TO = "masterai6612@gmail.com"
EMAIL_FROM = "masterai6612@gmail.com"
```

## 🎯 Repository Structure

```
mcp-stock-alert/
├── streamlit_dashboard.py          # Main Streamlit app
├── requirements_streamlit.txt      # Dependencies for cloud
├── last_recommendations.json       # Optional: recent signals
├── STREAMLIT_DEPLOYMENT.md        # This file
└── ... (other files for local monitoring)
```

## 🌟 Features

- 📊 Real-time stock prices from Yahoo Finance
- 📈 7% growth filter visualization
- 🎯 Top stocks monitoring
- 💹 Performance metrics (1W, 1M changes)
- ✅ Growth requirement indicators
- 🔄 Manual refresh button

## 🆘 Troubleshooting

### Issue: Module not found
**Solution:** Make sure `requirements_streamlit.txt` includes all dependencies

### Issue: No data showing
**Solution:** Check if Yahoo Finance API is accessible from Streamlit Cloud

### Issue: Recommendations not showing
**Solution:** Upload `last_recommendations.json` to your repo

## 📧 Support

For issues or questions:
- Check Streamlit Cloud logs
- Verify all files are pushed to GitHub
- Test locally first before deploying

## 🎉 Success!

Once deployed, you'll get a URL like:
`https://your-app-name.streamlit.app`

Share this URL to access your dashboard from anywhere! 🌍
