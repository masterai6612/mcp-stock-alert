

# 🤖 Gemma AI Market Analysis Setup Guide

## Overview

This guide helps you set up Gemma AI for advanced market analysis that generates **Top 10 Daily Stock Picks** using artificial intelligence.

## 🎯 What Gemma Adds

### Without Gemma (Current System):
- ✅ Technical analysis (RSI, MACD, etc.)
- ✅ 7% growth filter
- ✅ Rule-based scoring

### With Gemma AI:
- ✅ **All of the above PLUS:**
- 🤖 Deep contextual analysis of each stock
- 🧠 AI-powered ranking and selection
- 📊 Comprehensive AI scoring (0-100)
- 💡 Natural language insights for each pick
- 🎯 Top 10 daily picks with AI reasoning

## 📋 Prerequisites

1. **Kaggle Account** (free)
   - Sign up at https://www.kaggle.com
   - Go to Settings → API → Create New Token
   - Download `kaggle.json`

2. **System Requirements**
   - Python 3.9+
   - 8GB+ RAM
   - GPU recommended (but not required)
   - Mac M1/M2 will use Metal acceleration

## 🚀 Installation Steps

### Step 1: Set Kaggle Credentials

```bash
# Set environment variables
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_api_key"

# Or add to your .env file
echo "KAGGLE_USERNAME=your_username" >> .env
echo "KAGGLE_KEY=your_api_key" >> .env
```

### Step 2: Download Gemma Model

```bash
cd "/Users/monie/Desktop/kiro/mcp-stock-alert copy"
./setup_gemma.sh
```

This will:
- Download Gemma 1.1 Instruct 2B model (~5GB)
- Extract to `models/gemma/`
- Takes 5-10 minutes depending on internet speed

### Step 3: Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements_gemma.txt
```

For Mac M1/M2 (GPU acceleration):
```bash
pip install tensorflow-metal
```

### Step 4: Test the Setup

```bash
python gemma_market_analysis.py
```

## 📊 How It Works

### 1. Stock Screening
- Analyzes 100+ priority stocks
- Filters for 7% growth requirement
- Gets technical indicators

### 2. AI Analysis
For each qualifying stock, Gemma AI:
- Analyzes technical setup
- Evaluates growth potential
- Assesses risk/reward
- Generates natural language insights

### 3. AI Scoring (0-100)
- **40 points:** Technical score
- **20 points:** Growth requirement met
- **15 points:** Growth potential
- **10 points:** RSI optimization
- **10 points:** Volume confirmation
- **5 points:** Sector bonus

### 4. Top 10 Selection
- Ranks all stocks by AI score
- Selects top 10
- Sends email with detailed analysis

## 📧 Email Format

You'll receive:
```
🤖 GEMMA AI-POWERED DAILY STOCK PICKS
📅 Monday, November 11, 2025

🎯 TOP 10 PICKS FOR TODAY

1. 🚀 NVDA - AI Score: 95/100
   💰 Price: $145.23
   📈 Performance: 1W: +9.9% | 1M: +5.7%
   🎯 Technical: RSI: 58.3 | MACD: 0.234
   📊 Growth Potential: 15.6% (confidence: 60%)
   
   🤖 AI Analysis:
   Strong momentum with excellent technical setup. 
   High growth potential supported by volume confirmation.
   
   🔍 Key Signals: Above 20-day MA, MACD bullish, High volume
```

## 🔄 Running Options

### Option 1: Manual Run (Anytime)
```bash
source venv/bin/activate
python gemma_market_analysis.py
```

### Option 2: Scheduled Daily (Recommended)
Add to crontab for daily 7 AM run:
```bash
crontab -e

# Add this line:
0 7 * * 1-5 cd /Users/monie/Desktop/kiro/mcp-stock-alert\ copy && source venv/bin/activate && python gemma_market_analysis.py
```

### Option 3: Add to Existing Scheduler
Modify `scheduled_market_alerts.py` to include Gemma analysis.

## 🎛️ Configuration

### Adjust Stock Universe
Edit `gemma_market_analysis.py`:
```python
priority_symbols = [
    'AAPL', 'NVDA', 'GOOGL',  # Add your favorites
    # ... more symbols
]
```

### Change Number of Picks
```python
top_10 = analyst.rank_stocks_with_ai(analyzed_stocks)[:10]  # Change 10 to any number
```

### Adjust AI Scoring Weights
Edit `_calculate_ai_score()` method to change weights.

## 🐛 Troubleshooting

### Issue: "Gemma not available"
**Solution:** The system will use enhanced rule-based analysis as fallback. Still works great!

### Issue: Model download fails
**Solution:** 
- Check Kaggle credentials
- Verify internet connection
- Try manual download from Kaggle

### Issue: Out of memory
**Solution:**
- Use smaller batch size
- Reduce number of stocks analyzed
- Close other applications

### Issue: Slow performance
**Solution:**
- Use GPU if available
- Reduce stock universe
- Use float16 precision (already enabled)

## 📈 Performance

### Without Gemma (Fallback Mode):
- ✅ Still works perfectly
- ✅ Enhanced rule-based analysis
- ✅ Fast execution (~2 minutes)
- ✅ All features except AI insights

### With Gemma AI:
- ✅ Deep AI analysis
- ✅ Natural language insights
- ⏱️ Slower (~10-15 minutes)
- 🎯 More nuanced recommendations

## 💡 Tips

1. **Run in the morning** (7-8 AM) before market opens
2. **Review AI insights** - they provide context beyond numbers
3. **Combine with your research** - AI is a tool, not a replacement
4. **Track performance** - See which AI picks perform best
5. **Adjust weights** - Customize scoring to your strategy

## 🔐 Security

- Kaggle credentials stored in environment variables
- Model runs locally (no data sent to cloud)
- Email credentials use existing .env setup

## 📊 Output Files

- `gemma_top_10_picks.json` - Daily picks in JSON format
- Email sent to: masterai6612@gmail.com
- Logs in console output

## 🎯 Next Steps

1. Run setup: `./setup_gemma.sh`
2. Test: `python gemma_market_analysis.py`
3. Schedule daily runs
4. Review and refine based on results

## 🆘 Support

If you encounter issues:
1. Check this guide
2. Verify all prerequisites
3. Try fallback mode (works without Gemma)
4. Review error messages

## 🎉 Success!

Once set up, you'll receive daily AI-powered stock picks with:
- ✅ 7% growth requirement enforced
- ✅ AI scoring and ranking
- ✅ Natural language insights
- ✅ Top 10 best opportunities

Happy trading! 🚀
