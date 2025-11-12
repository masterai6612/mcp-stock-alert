"""
Dashboard Page - Real-time stock monitoring
"""

import streamlit as st
import json
import os
from datetime import datetime
import yfinance as yf
import pandas as pd

def show():
    st.title("🏠 Real-Time Dashboard")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        market_status = "CLOSED" if datetime.now().hour < 9 or datetime.now().hour >= 16 else "OPEN"
        st.metric("Market Status", market_status, 
                 "Trading" if market_status == "OPEN" else "After Hours")
    
    with col2:
        st.metric("Stocks Monitored", "529", "Comprehensive Universe")
    
    with col3:
        st.metric("Growth Filter", "7%+", "Required for BUY")
    
    with col4:
        # Check if scheduler is running
        import subprocess
        try:
            result = subprocess.run(['pgrep', '-f', 'scheduled_market_alerts'], 
                                  capture_output=True, text=True)
            scheduler_status = "✅ Running" if result.returncode == 0 else "⚠️ Stopped"
        except:
            scheduler_status = "Unknown"
        st.metric("Alert System", scheduler_status)
    
    st.markdown("---")
    
    # Recent recommendations
    st.header("🎯 Recent Recommendations")
    
    if os.path.exists('last_recommendations.json'):
        try:
            with open('last_recommendations.json', 'r') as f:
                recommendations = json.load(f)
            
            buy_signals = recommendations.get('buy_signals', [])
            watch_signals = recommendations.get('watch_signals', [])
            timestamp = recommendations.get('timestamp', 'Unknown')
            
            st.info(f"📅 Last updated: {timestamp}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🚀 BUY Signals ({len(buy_signals)})")
                if buy_signals:
                    for signal in buy_signals[:10]:
                        with st.expander(f"**{signal['symbol']}** - Score: {signal['score']}"):
                            st.write(f"💰 Price: ${signal['current_price']:.2f}")
                            st.write(f"📊 RSI: {signal['rsi']:.1f}")
                            st.write(f"📈 MACD: {signal['macd']:.3f}")
                            if signal.get('signals'):
                                st.write(f"🔍 Signals: {', '.join(signal['signals'][:3])}")
                else:
                    st.info("No BUY signals currently")
            
            with col2:
                st.subheader(f"👀 WATCH Signals ({len(watch_signals)})")
                if watch_signals:
                    for signal in watch_signals[:10]:
                        with st.expander(f"**{signal['symbol']}** - Score: {signal['score']}"):
                            st.write(f"💰 Price: ${signal['current_price']:.2f}")
                            st.write(f"📊 RSI: {signal['rsi']:.1f}")
                            st.write(f"📈 MACD: {signal['macd']:.3f}")
                            if signal.get('signals'):
                                st.write(f"🔍 Signals: {', '.join(signal['signals'][:3])}")
                else:
                    st.info("No WATCH signals currently")
        
        except Exception as e:
            st.error(f"Error loading recommendations: {e}")
    else:
        st.warning("No recommendations data available. Run the stock alert system to generate data.")
    
    st.markdown("---")
    
    # Top stocks table
    st.header("📈 Top Stocks Performance")
    
    with st.spinner("Loading stock data..."):
        top_symbols = ['AAPL', 'NVDA', 'GOOGL', 'MSFT', 'TSLA', 'META', 'AMZN', 'AMD']
        
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
    
    # Auto-refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.rerun()
