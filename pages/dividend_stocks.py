"""
Dividend Stocks Page - Top 50 Dividend Stocks from 600+ Stock Universe
"""

import streamlit as st
import json
import os
from datetime import datetime

def show():
    st.title("💰 Top 50 Dividend Stocks")
    st.markdown("### Comprehensive scan of 600+ US & Canadian stocks")
    st.markdown("---")
    
    # Check if data exists
    if not os.path.exists('top_50_dividend_stocks.json'):
        st.warning("⚠️ No dividend stock analysis available yet")
        st.info("""
        **To generate Top 50 Dividend Stocks:**
        
        ```bash
        python dividend_stock_analyzer.py
        ```
        
        This will scan 600+ stocks and find the best dividend opportunities.
        Analysis takes approximately 5-10 minutes.
        """)
        return
    
    # Load data
    try:
        with open('top_50_dividend_stocks.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Stocks Scanned", data.get('total_scanned', 533))
    
    with col2:
        st.metric("💰 Dividend Stocks", data.get('total_dividend_stocks', 0))
    
    with col3:
        last_update = data.get('generated_at', 'Unknown')
        if last_update != 'Unknown':
            try:
                dt = datetime.fromisoformat(last_update)
                last_update = dt.strftime('%m-%d %H:%M')
            except:
                pass
        st.metric("🕐 Last Update", last_update)
    
    with col4:
        st.metric("🎯 Min Yield", "2.0%")
    
    st.markdown("---")
    
    # Get stocks
    top_50 = data.get('top_50_dividend_stocks', [])
    all_dividend_stocks = data.get('all_dividend_stocks', [])
    
    if not top_50:
        st.error("❌ No dividend stocks found in data")
        return
    
    # Analysis date
    analysis_date = data.get('generated_at', 'Unknown')
    try:
        dt = datetime.fromisoformat(analysis_date)
        formatted_date = dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_date = analysis_date
    
    st.success(f"📅 Analysis Date: {formatted_date}")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Category filter
        categories = ['All'] + sorted(list(set(s.get('category', 'Unknown') for s in top_50)))
        selected_category = st.selectbox("📂 Category", categories)
    
    with col2:
        # Sector filter
        sectors = ['All'] + sorted(list(set(s.get('sector', 'Unknown') for s in top_50)))
        selected_sector = st.selectbox("🏢 Sector", sectors)
    
    with col3:
        # Yield filter
        min_yield = st.slider("💰 Min Dividend Yield %", 2.0, 10.0, 2.0, 0.5)
    
    # Filter stocks
    filtered_stocks = top_50
    
    if selected_category != 'All':
        filtered_stocks = [s for s in filtered_stocks if s.get('category') == selected_category]
    
    if selected_sector != 'All':
        filtered_stocks = [s for s in filtered_stocks if s.get('sector') == selected_sector]
    
    filtered_stocks = [s for s in filtered_stocks if s.get('dividend_yield', 0) >= min_yield]
    
    st.info(f"📊 Showing {len(filtered_stocks)} stocks (filtered from {len(top_50)} top stocks)")
    
    # Display mode
    display_mode = st.radio("Display Mode", ["📋 Compact List", "📊 Detailed Cards"], horizontal=True)
    
    if display_mode == "📋 Compact List":
        # Compact table view
        st.markdown("### 📋 Dividend Stocks List")
        
        for i, stock in enumerate(filtered_stocks, 1):
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**#{i}**")
            
            with col2:
                st.markdown(f"**{stock['symbol']}**")
                st.caption(stock.get('category', 'N/A'))
            
            with col3:
                st.caption(stock.get('company_name', 'N/A')[:30])
                st.caption(stock.get('sector', 'N/A'))
            
            with col4:
                yield_val = stock.get('dividend_yield', 0)
                st.metric("Yield", f"{yield_val:.2f}%", label_visibility="collapsed")
            
            with col5:
                growth = stock.get('change_1m', 0)
                st.metric("Growth", f"{growth:+.1f}%", label_visibility="collapsed")
            
            with col6:
                score = stock.get('dividend_score', 0)
                st.metric("Score", f"{score:.0f}", label_visibility="collapsed")
            
            if i < len(filtered_stocks):
                st.markdown("---")
    
    else:
        # Detailed card view
        st.markdown("### 📊 Detailed Stock Cards")
        
        for i, stock in enumerate(filtered_stocks, 1):
            # Category emoji
            category = stock.get('category', 'N/A')
            if 'High Dividend' in category:
                emoji = "💎"
            elif 'Growth' in category and 'Dividend' in category:
                emoji = "🌟"
            elif 'Growth' in category:
                emoji = "📈"
            else:
                emoji = "💰"
            
            with st.expander(f"{emoji} #{i} - {stock['symbol']} - {category}", expanded=(i <= 3)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {stock.get('company_name', stock['symbol'])}")
                    st.markdown(f"**💵 Current Price:** ${stock['current_price']:.2f}")
                    st.markdown(f"**🏢 Sector:** {stock.get('sector', 'N/A')}")
                    st.markdown(f"**📊 Market Cap:** ${stock.get('market_cap', 0)/1e9:.2f}B")
                    
                    # Dividend info
                    st.markdown("#### 💰 Dividend Information")
                    dividend_yield = stock.get('dividend_yield', 0)
                    st.markdown(f"**Dividend Yield:** {dividend_yield:.2f}%")
                    
                    annual_dividend = stock['current_price'] * dividend_yield / 100
                    st.markdown(f"**Annual Dividend:** ${annual_dividend:.2f} per share")
                    
                    # Calculate potential income
                    shares_100 = 100
                    shares_1000 = 1000
                    income_100 = annual_dividend * shares_100
                    income_1000 = annual_dividend * shares_1000
                    
                    st.markdown(f"**Potential Annual Income:**")
                    st.markdown(f"- 100 shares: ${income_100:.2f}/year (${income_100/12:.2f}/month)")
                    st.markdown(f"- 1,000 shares: ${income_1000:.2f}/year (${income_1000/12:.2f}/month)")
                    
                    # Performance
                    st.markdown("#### 📈 Performance")
                    perf_col1, perf_col2, perf_col3 = st.columns(3)
                    with perf_col1:
                        st.metric("1 Week", f"{stock.get('change_1w', 0):+.2f}%")
                    with perf_col2:
                        st.metric("1 Month", f"{stock.get('change_1m', 0):+.2f}%")
                    with perf_col3:
                        price_pos = stock.get('price_position', 50)
                        st.metric("52W Position", f"{price_pos:.0f}%")
                    
                    # Technical indicators
                    st.markdown("#### 🎯 Technical Indicators")
                    tech_col1, tech_col2, tech_col3 = st.columns(3)
                    with tech_col1:
                        rsi = stock.get('rsi', 50)
                        st.metric("RSI", f"{rsi:.1f}")
                        if rsi < 30:
                            st.caption("🟢 Oversold")
                        elif rsi > 70:
                            st.caption("🔴 Overbought")
                        else:
                            st.caption("🟡 Neutral")
                    
                    with tech_col2:
                        vol_trend = stock.get('volume_trend', 0)
                        st.metric("Volume Trend", f"{vol_trend:+.1f}%")
                    
                    with tech_col3:
                        tech_score = stock.get('technical_score', 0)
                        st.metric("Technical Score", f"{tech_score:.1f}/10")
                
                with col2:
                    # Scores
                    st.markdown("#### 📊 Scores")
                    
                    # Dividend score
                    div_score = stock.get('dividend_score', 0)
                    st.metric("Dividend Score", f"{div_score:.1f}/100")
                    st.progress(min(div_score / 100, 1.0))
                    
                    # Technical score
                    tech_score = stock.get('technical_score', 0)
                    st.metric("Technical", f"{tech_score:.1f}/10")
                    st.progress(tech_score / 10)
                    
                    # Category badge
                    st.markdown("#### 🏷️ Category")
                    st.info(category)
                    
                    # Growth requirement
                    st.markdown("#### 📈 Growth Status")
                    if stock.get('meets_growth_requirement'):
                        st.success("✅ Meets 7% Growth")
                    else:
                        st.warning("⚠️ Below 7% Growth")
                    
                    # Quick stats
                    st.markdown("#### 📊 Quick Stats")
                    st.markdown(f"**Yield:** {dividend_yield:.2f}%")
                    st.markdown(f"**1M Growth:** {stock.get('change_1m', 0):+.2f}%")
                    st.markdown(f"**RSI:** {stock.get('rsi', 0):.1f}")
    
    # Summary statistics
    st.markdown("---")
    st.header("📊 Portfolio Summary")
    
    if filtered_stocks:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_yield = sum(s.get('dividend_yield', 0) for s in filtered_stocks) / len(filtered_stocks)
            st.metric("Avg Dividend Yield", f"{avg_yield:.2f}%")
        
        with col2:
            avg_growth = sum(s.get('change_1m', 0) for s in filtered_stocks) / len(filtered_stocks)
            st.metric("Avg 1M Growth", f"{avg_growth:.2f}%")
        
        with col3:
            growth_stocks = sum(1 for s in filtered_stocks if s.get('meets_growth_requirement'))
            st.metric("7%+ Growth", f"{growth_stocks}/{len(filtered_stocks)}")
        
        with col4:
            avg_score = sum(s.get('dividend_score', 0) for s in filtered_stocks) / len(filtered_stocks)
            st.metric("Avg Dividend Score", f"{avg_score:.1f}/100")
        
        # Category breakdown
        st.markdown("### 📊 Category Breakdown")
        categories_count = {}
        for stock in filtered_stocks:
            cat = stock.get('category', 'Unknown')
            categories_count[cat] = categories_count.get(cat, 0) + 1
        
        for cat, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(filtered_stocks)) * 100
            st.markdown(f"**{cat}:** {count} stocks ({percentage:.1f}%)")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        if st.button("▶️ Run New Analysis"):
            st.info("Run: `python dividend_stock_analyzer.py`")
    
    with col3:
        if os.path.exists('top_50_dividend_stocks.json'):
            with open('top_50_dividend_stocks.json', 'r') as f:
                json_data = f.read()
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"top_50_dividends_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # Info section
    st.markdown("---")
    st.header("ℹ️ About This Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 💰 Why Dividend Stocks?
        
        - **Income Generation:** Regular cash payments
        - **Lower Volatility:** Typically more stable
        - **Total Return:** Dividends + Capital appreciation
        - **Compounding:** Reinvest dividends for growth
        - **Inflation Hedge:** Growing dividends beat inflation
        
        ### 🎯 Our Criteria:
        
        - ✅ Dividend yield ≥ 2%
        - ✅ Scanned 600+ US & Canadian stocks
        - ✅ Strong technical indicators
        - ✅ Growth potential considered
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Scoring System:
        
        **Dividend Score (0-100):**
        - **50 points** - Technical analysis score
        - **30 points** - Dividend yield (up to 10%)
        - **20 points** - Growth potential (1-month)
        
        ### 🏆 Categories:
        
        - **Growth + High Dividend:** 10%+ growth, 4%+ yield
        - **Dividend + Growth:** 7%+ growth, 4%+ yield
        - **Growth:** 10%+ growth
        - **High Dividend:** 4%+ yield
        - **Growth + Dividend:** 7%+ growth, 2%+ yield
        - **Dividend:** 2%+ yield
        """)
    
    # Disclaimer
    st.markdown("---")
    st.caption("""
    ⚠️ **Disclaimer:** This analysis is for informational purposes only. 
    Not financial advice. Dividend payments are not guaranteed and can be reduced or eliminated.
    Past performance does not guarantee future results.
    Always do your own research and consult with a financial advisor before investing.
    """)

