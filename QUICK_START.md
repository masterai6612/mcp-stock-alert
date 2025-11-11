# 🚀 Quick Start - Stock Alert System

## Simple Command to Run After Laptop Restart

Open Terminal and run:

```bash
cd "/Users/monie/Desktop/kiro/mcp-stock-alert copy"
./start_stock_alerts.sh
```

That's it! The system will:
- ✅ Monitor 600+ stocks continuously
- ✅ Send email alerts to masterai6612@gmail.com
- ✅ Only alert on significant changes (no spam)
- ✅ Run 24/7 during market hours

## Alternative: Run in Background

If you want it to run in the background and keep working even if you close Terminal:

```bash
cd "/Users/monie/Desktop/kiro/mcp-stock-alert copy"
nohup ./start_stock_alerts.sh > stock_alerts.log 2>&1 &
```

To stop it later:
```bash
pkill -f scheduled_market_alerts.py
```

## One-Time Analysis (Get Immediate Email)

If you just want a quick analysis right now:

```bash
cd "/Users/monie/Desktop/kiro/mcp-stock-alert copy"
source venv/bin/activate
python current_stock_summary.py
```

This will analyze all stocks and send you an email immediately.

## Check if System is Running

```bash
ps aux | grep scheduled_market_alerts.py
```

If you see a process, it's running!

## View Logs

```bash
tail -f scheduled_alerts.log
```

## Email Configuration

Your email is already configured in `.env`:
- **To:** masterai6612@gmail.com
- **From:** masterai6612@gmail.com
- **Password:** Already set ✅

## What Gets Monitored

- 🇺🇸 300+ US stocks (NASDAQ/NYSE)
- 🇨🇦 300+ Canadian stocks (TSX)
- 📊 Technical indicators (RSI, MACD, Volume)
- 📰 News sentiment
- 📅 Earnings calendar

## Alert Logic

You get emails when:
- ✅ New BUY signals appear
- ✅ BUY signals are removed
- ✅ Stock scores change by ≥2 points
- ✅ Stocks get promoted/demoted between BUY/WATCH
- ✅ Multiple WATCH signals change (≥3 stocks)

**No spam!** Only significant changes trigger emails.
