#!/usr/bin/env python3
"""
Stock Alert System - Multi-Page Streamlit App
Main entry point with navigation
"""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Stock Alert System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">📊 Stock Alert System</div>', unsafe_allow_html=True)
st.markdown("---")

# Navigation
st.sidebar.title("📱 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard", "🤖 Gemma AI Top 10", "📊 Market Analysis", "⚙️ Settings"]
)

# Footer in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📧 Email Alerts")
st.sidebar.text("masterai6612@gmail.com")
st.sidebar.markdown("### 🔄 Last Updated")
try:
    from timezone_utils import get_local_now_str
    st.sidebar.text(get_local_now_str())
except:
    st.sidebar.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S EST"))

# Page routing
if page == "🏠 Dashboard":
    import pages.dashboard as dashboard
    dashboard.show()
elif page == "🤖 Gemma AI Top 10":
    import pages.gemma_picks as gemma_picks
    gemma_picks.show()
elif page == "📊 Market Analysis":
    import pages.market_analysis as market_analysis
    market_analysis.show()
elif page == "⚙️ Settings":
    import pages.settings as settings
    settings.show()
