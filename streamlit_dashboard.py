#!/usr/bin/env python3
"""
Stock Alert System - Streamlit Dashboard
Real-time monitoring for Streamlit Cloud deployment
"""

import streamlit as st
import json
import os
from datetime import datetime
import yfinance as yf
import pandas as pd
import time

st.set_page_config(
    page_title="Stock Alert System",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Stock Alert System Dashboard")
st.markdown("Real-time stock monitoring with 7% growth filter")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    
    # Check if running locally or on cloud
    if os.path.exists('scheduled_market_alerts.py'):
        st.success("✅ Running Locally")
        
        # Check if scheduler is running
        import subprocess
        try:
            result = subprocess.run(['pgrep', '-f', 'scheduled_market_alerts'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Scheduler Running")
            else:
                st.warning("⚠️ Scheduler Stopped")
        except:
            st.info("ℹ️ Cannot check scheduler status")
    else:
        st.info("☁️ Running on Streamlit Cloud")
        st.warning("⚠️ Live monitoring not available on cloud")
    
    st.markdown("---")
    st.markdown("### 📧 Email Alerts")
    st.text("masterai6612@gmail.com")
    
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Market Status", "CLOSED" if datetime.now().hour < 9 or datetime.now().hour >= 16 else "OPEN")

with col2:
    st.metric("Stocks Monitored", "529")

with col3:
    st.metric("Growth Filter", "7%+ Required")

st.markdown("---")

# Top stocks section
st.header("📈 Top Stocks")

# Sample stocks to display
top_symbols = ['AAPL', 'NVDA', 'GOOGL', 'MSFT', 'TSLA', 'META', 'AMZN']

with st.spinner("Loading stock data..."):
    stocks_data = []
    
    for symbol in top_symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1mo')
            info = ticker.info
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                price_1w = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
                price_1m = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                
                stocks_data.append({
                    'Symbol': symbol,
                    'Price': f"${current_price:.2f}",
                    '1W Change': f"{price_1w:+.2f}%",
                    '1M Change': f"{price_1m:+.2f}%",
                    'Growth ≥7%': '✅' if price_1w >= 7 or price_1m >= 7 else '❌',
                    'Sector': info.get('sector', 'N/A')
                })
        except:
            continue
    
    if stocks_data:
        df = pd.DataFrame(stocks_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error("Unable to load stock data")

st.markdown("---")

# Recent recommendations
st.header("🎯 Recent Recommendations")

if os.path.exists('last_recommendations.json'):
    try:
        with open('last_recommendations.json', 'r') as f:
            recommendations = json.load(f)
        
        buy_signals = recommendations.get('buy_signals', [])
        watch_signals = recommendations.get('watch_signals', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🚀 BUY Signals ({len(buy_signals)})")
            if buy_signals:
                for signal in buy_signals[:5]:
                    st.markdown(f"**{signal['symbol']}** - Score: {signal['score']}")
            else:
                st.info("No BUY signals")
        
        with col2:
            st.subheader(f"👀 WATCH Signals ({len(watch_signals)})")
            if watch_signals:
                for signal in watch_signals[:5]:
                    st.markdown(f"**{signal['symbol']}** - Score: {signal['score']}")
            else:
                st.info("No WATCH signals")
    except:
        st.warning("No recommendations data available")
else:
    st.info("Run the stock alert system locally to see recommendations")

st.markdown("---")

# Footer
st.markdown("""
### 📝 About
This dashboard monitors stock alerts with a **7% growth filter**. 

**Features:**
- ✅ Hard 7% growth requirement for BUY signals
- 📊 Growth potential calculator
- 📧 Email alerts for significant changes
- 🔄 24/7 monitoring during market hours

**To run locally:**
```bash
cd "mcp-stock-alert copy"
./start_stock_alerts.sh
```
""")

# Footer with timestamp
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Click 'Refresh Data' in the sidebar to update")
