"""
Settings Page
"""

import streamlit as st
import os
import subprocess
from datetime import datetime

def show():
    st.title("⚙️ Settings & Configuration")
    
    # System status
    st.header("🔧 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alert System")
        try:
            result = subprocess.run(['pgrep', '-f', 'scheduled_market_alerts'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Running")
                pids = result.stdout.strip().split('\n')
                st.info(f"PID: {pids[0]}")
            else:
                st.warning("⚠️ Stopped")
                if st.button("Start Alert System"):
                    st.info("Run: ./start_stock_alerts.sh")
        except:
            st.error("Cannot check status")
    
    with col2:
        st.subheader("Gemma AI")
        if os.path.exists('models/gemma'):
            st.success("✅ Model Downloaded")
            st.info("Ready for AI analysis")
        else:
            st.warning("⚠️ Model Not Downloaded")
            st.info("Run: ./setup_gemma.sh")
    
    st.markdown("---")
    
    # Configuration
    st.header("📧 Email Configuration")
    
    email_to = st.text_input("Email Address", "masterai6612@gmail.com", disabled=True)
    st.caption("Email alerts are sent to this address")
    
    st.markdown("---")
    
    # Growth filter settings
    st.header("📊 Growth Filter Settings")
    
    growth_threshold = st.slider("Growth Requirement (%)", 5, 15, 7)
    st.info(f"Current: {growth_threshold}% growth required for BUY signals")
    st.caption("⚠️ Changing this requires code modification")
    
    st.markdown("---")
    
    # Data management
    st.header("💾 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if os.path.exists('last_recommendations.json'):
            st.success("✅ Recommendations")
            with open('last_recommendations.json', 'r') as f:
                data = f.read()
            st.download_button(
                "📥 Download",
                data,
                "recommendations.json",
                "application/json"
            )
        else:
            st.warning("⚠️ No recommendations")
    
    with col2:
        if os.path.exists('gemma_top_10_picks.json'):
            st.success("✅ Gemma Picks")
            with open('gemma_top_10_picks.json', 'r') as f:
                data = f.read()
            st.download_button(
                "📥 Download",
                data,
                "gemma_picks.json",
                "application/json"
            )
        else:
            st.warning("⚠️ No Gemma picks")
    
    with col3:
        if os.path.exists('sent_alerts.json'):
            st.success("✅ Alert History")
            with open('sent_alerts.json', 'r') as f:
                data = f.read()
            st.download_button(
                "📥 Download",
                data,
                "alert_history.json",
                "application/json"
            )
        else:
            st.warning("⚠️ No alert history")
    
    st.markdown("---")
    
    # System info
    st.header("ℹ️ System Information")
    
    info_data = {
        "Python Version": subprocess.run(['python', '--version'], capture_output=True, text=True).stdout.strip(),
        "Working Directory": os.getcwd(),
        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST"),
        "Stocks Monitored": "529",
        "Growth Filter": "7%+",
        "Email Alerts": "Enabled"
    }
    
    for key, value in info_data.items():
        st.text(f"{key}: {value}")
    
    st.markdown("---")
    
    # Quick actions
    st.header("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh All Data"):
            st.rerun()
    
    with col2:
        if st.button("📧 Test Email"):
            st.info("Run: python test_email_now.py")
    
    with col3:
        if st.button("🧪 Test System"):
            st.info("Run: python test_gemma_system.py")
    
    st.markdown("---")
    
    # Documentation links
    st.header("📚 Documentation")
    
    docs = {
        "Quick Start": "QUICK_START.md",
        "Gemma Setup": "GEMMA_SETUP_GUIDE.md",
        "Growth Filter": "GROWTH_FILTER_IMPLEMENTATION.md",
        "Streamlit Deployment": "STREAMLIT_DEPLOYMENT.md"
    }
    
    for name, file in docs.items():
        if os.path.exists(file):
            st.markdown(f"• [{name}]({file})")
        else:
            st.markdown(f"• {name} (not found)")
