"""
Market Analysis Page
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def show():
    st.title("📊 Market Analysis")
    
    # Market indices
    st.header("📈 Major Indices")
    
    indices = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'NASDAQ',
        '^RUT': 'Russell 2000'
    }
    
    cols = st.columns(len(indices))
    
    for i, (symbol, name) in enumerate(indices.items()):
        with cols[i]:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d')
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[0]
                    change = ((current - previous) / previous) * 100
                    st.metric(name, f"{current:.2f}", f"{change:+.2f}%")
            except:
                st.metric(name, "N/A")
    
    st.markdown("---")
    
    # Sector performance
    st.header("🏭 Sector Performance")
    
    sector_etfs = {
        'XLK': 'Technology',
        'XLF': 'Financial',
        'XLV': 'Healthcare',
        'XLE': 'Energy',
        'XLI': 'Industrial',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLB': 'Materials'
    }
    
    sector_data = []
    for etf, sector in sector_etfs.items():
        try:
            ticker = yf.Ticker(etf)
            hist = ticker.history(period='5d')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[0]
                change = ((current - previous) / previous) * 100
                sector_data.append({
                    'Sector': sector,
                    'ETF': etf,
                    'Price': f"${current:.2f}",
                    '5D Change': f"{change:+.2f}%",
                    'Change': change
                })
        except:
            continue
    
    if sector_data:
        df = pd.DataFrame(sector_data)
        df = df.sort_values('Change', ascending=False)
        df = df.drop('Change', axis=1)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Stock lookup
    st.header("🔍 Stock Lookup")
    
    symbol = st.text_input("Enter stock symbol (e.g., AAPL, NVDA)", "AAPL")
    
    if st.button("Analyze"):
        with st.spinner(f"Analyzing {symbol}..."):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period='3mo')
                
                if not hist.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader(f"{info.get('longName', symbol)}")
                        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                        
                        current_price = hist['Close'].iloc[-1]
                        st.metric("Current Price", f"${current_price:.2f}")
                        
                        # Performance
                        price_1w = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
                        price_1m = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100 if len(hist) >= 20 else 0
                        
                        st.metric("1 Week", f"{price_1w:+.2f}%")
                        st.metric("1 Month", f"{price_1m:+.2f}%")
                    
                    with col2:
                        st.subheader("Key Metrics")
                        st.write(f"**Market Cap:** ${info.get('marketCap', 0):,.0f}")
                        st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
                        st.write(f"**52W High:** ${info.get('fiftyTwoWeekHigh', 0):.2f}")
                        st.write(f"**52W Low:** ${info.get('fiftyTwoWeekLow', 0):.2f}")
                        st.write(f"**Volume:** {info.get('volume', 0):,}")
                        st.write(f"**Avg Volume:** {info.get('averageVolume', 0):,}")
                    
                    # Chart
                    st.subheader("📈 Price Chart (3 Months)")
                    chart_data = hist['Close'].reset_index()
                    chart_data.columns = ['Date', 'Price']
                    st.line_chart(chart_data.set_index('Date'))
                    
                    # Growth check
                    if price_1w >= 7 or price_1m >= 7:
                        st.success(f"✅ Meets 7% growth requirement ({max(price_1w, price_1m):.2f}%)")
                    else:
                        st.warning(f"⚠️ Below 7% growth requirement ({max(price_1w, price_1m):.2f}%)")
                
                else:
                    st.error(f"No data available for {symbol}")
            
            except Exception as e:
                st.error(f"Error analyzing {symbol}: {e}")
