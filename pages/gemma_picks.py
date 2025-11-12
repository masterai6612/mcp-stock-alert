"""
Gemma AI Top 10 Picks Page
"""

import streamlit as st
import json
import os
from datetime import datetime
import subprocess

def show():
    st.title("🤖 Gemma AI - Top 10 Daily Picks")
    
    # Header info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("AI Model", "Gemma 1.1", "Instruct 2B")
    
    with col2:
        st.metric("Analysis Mode", "Advanced", "AI + Technical")
    
    with col3:
        st.metric("Growth Filter", "7%+", "Enforced")
    
    st.markdown("---")
    
    # Check if Gemma picks exist
    if os.path.exists('gemma_top_10_picks.json'):
        try:
            with open('gemma_top_10_picks.json', 'r') as f:
                data = json.load(f)
            
            picks = data.get('picks', [])
            analysis_date = data.get('date', 'Unknown')
            
            # Parse date
            try:
                dt = datetime.fromisoformat(analysis_date)
                formatted_date = dt.strftime('%A, %B %d, %Y at %I:%M %p')
            except:
                formatted_date = analysis_date
            
            st.success(f"📅 Analysis Date: {formatted_date}")
            
            if picks:
                st.header(f"🎯 Top {len(picks)} AI-Selected Picks")
                
                # Display each pick
                for i, pick in enumerate(picks, 1):
                    with st.expander(f"#{i} - {pick['symbol']} - AI Score: {pick.get('ai_score', 0):.0f}/100", expanded=(i <= 3)):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"### 💰 ${pick['current_price']:.2f}")
                            st.markdown(f"**🏢 Sector:** {pick.get('sector', 'N/A')}")
                            
                            # Performance metrics
                            st.markdown("#### 📈 Performance")
                            perf_col1, perf_col2, perf_col3 = st.columns(3)
                            with perf_col1:
                                st.metric("1 Day", f"{pick.get('change_1d', 0):+.2f}%")
                            with perf_col2:
                                st.metric("1 Week", f"{pick.get('change_1w', 0):+.2f}%")
                            with perf_col3:
                                st.metric("1 Month", f"{pick.get('change_1m', 0):+.2f}%")
                            
                            # Technical indicators
                            st.markdown("#### 🎯 Technical Indicators")
                            tech_col1, tech_col2, tech_col3 = st.columns(3)
                            with tech_col1:
                                st.metric("RSI", f"{pick.get('rsi', 0):.1f}")
                            with tech_col2:
                                st.metric("MACD", f"{pick.get('macd', 0):.3f}")
                            with tech_col3:
                                st.metric("Volume", f"{pick.get('volume_ratio', 0):.1f}x")
                        
                        with col2:
                            # AI Score visualization
                            ai_score = pick.get('ai_score', 0)
                            st.markdown("#### 🤖 AI Score")
                            st.progress(ai_score / 100)
                            st.markdown(f"**{ai_score:.0f}/100**")
                            
                            # Growth metrics
                            st.markdown("#### 📊 Growth")
                            growth_pot = pick.get('growth_potential', 0)
                            growth_conf = pick.get('growth_confidence', 0) * 100
                            st.metric("Potential", f"{growth_pot:.1f}%")
                            st.metric("Confidence", f"{growth_conf:.0f}%")
                            
                            # Growth requirement
                            if pick.get('meets_growth_requirement'):
                                st.success("✅ Meets 7% Growth")
                            else:
                                st.warning("⚠️ Below 7% Growth")
                        
                        # AI Analysis
                        st.markdown("#### 🤖 AI Analysis")
                        ai_analysis = pick.get('ai_analysis', 'No analysis available')
                        st.info(ai_analysis)
                        
                        # Key signals
                        if pick.get('signals'):
                            st.markdown("#### 🔍 Key Signals")
                            signals_text = ", ".join(pick['signals'][:5])
                            st.markdown(f"_{signals_text}_")
                        
                        # Buy reasons
                        if pick.get('buy_reasons'):
                            st.markdown("#### 🚀 Buy Reasons")
                            for reason in pick['buy_reasons'][:3]:
                                st.markdown(f"• {reason}")
                
                # Summary statistics
                st.markdown("---")
                st.header("📊 Summary Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_score = sum(p.get('ai_score', 0) for p in picks) / len(picks)
                    st.metric("Avg AI Score", f"{avg_score:.1f}/100")
                
                with col2:
                    avg_growth = sum(p.get('growth_potential', 0) for p in picks) / len(picks)
                    st.metric("Avg Growth Potential", f"{avg_growth:.1f}%")
                
                with col3:
                    meets_growth = sum(1 for p in picks if p.get('meets_growth_requirement'))
                    st.metric("Meet 7% Growth", f"{meets_growth}/{len(picks)}")
                
                with col4:
                    avg_rsi = sum(p.get('rsi', 0) for p in picks) / len(picks)
                    st.metric("Avg RSI", f"{avg_rsi:.1f}")
            
            else:
                st.warning("No picks available in the data file")
        
        except Exception as e:
            st.error(f"Error loading Gemma picks: {e}")
    
    else:
        st.warning("⚠️ No Gemma AI analysis available yet")
        st.info("""
        **To generate Gemma AI picks:**
        
        1. Run the analysis:
        ```bash
        python gemma_market_analysis.py
        ```
        
        2. Or schedule daily runs:
        ```bash
        # Add to crontab for 7 AM daily
        0 7 * * 1-5 cd /path/to/project && python gemma_market_analysis.py
        ```
        
        3. Refresh this page after analysis completes
        """)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        if st.button("▶️ Run Analysis Now"):
            with st.spinner("Running Gemma AI analysis... This may take 2-5 minutes..."):
                try:
                    result = subprocess.run(
                        ['python', 'gemma_market_analysis.py'],
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minute timeout
                    )
                    if result.returncode == 0:
                        st.success("✅ Analysis complete! Refresh the page to see results.")
                    else:
                        st.error(f"❌ Analysis failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("❌ Analysis timed out")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with col3:
        if os.path.exists('gemma_top_10_picks.json'):
            with open('gemma_top_10_picks.json', 'r') as f:
                data = f.read()
            st.download_button(
                label="📥 Download JSON",
                data=data,
                file_name=f"gemma_picks_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # Disclaimer
    st.markdown("---")
    st.caption("""
    ⚠️ **Disclaimer:** This analysis is for informational purposes only. 
    Not financial advice. Always do your own research and consult with a financial advisor.
    """)
