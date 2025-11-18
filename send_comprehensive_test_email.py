#!/usr/bin/env python3
"""
Send Comprehensive Test Email
Includes: Current analysis, trends, dividends, and Streamlit update
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load .env file manually
def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

env_vars = load_env()

# Email settings
EMAIL_TO = 'masterai6612@gmail.com'
EMAIL_FROM = env_vars.get('EMAIL_FROM', os.getenv('EMAIL_FROM', 'masterai6612@gmail.com'))
EMAIL_PASSWORD = env_vars.get('EMAIL_PASSWORD', os.getenv('EMAIL_PASSWORD'))

# Telegram settings
TELEGRAM_BOT_TOKEN = env_vars.get('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN'))
TELEGRAM_CHAT_ID = env_vars.get('TELEGRAM_CHAT_ID', os.getenv('TELEGRAM_CHAT_ID'))

def load_json_file(filename, default=None):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading {filename}: {e}")
    return default or {}

def create_comprehensive_email():
    """Create comprehensive test email with all features"""
    
    # Load all data
    gemma_data = load_json_file('gemma_top_10_picks.json')
    dividend_data = load_json_file('top_50_dividend_stocks.json')
    recommendations = load_json_file('last_recommendations.json')
    streamlit_summary = load_json_file('streamlit_data_summary.json')
    
    # Email subject
    subject = f"🧪 Comprehensive Test Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Create email body
    body = f"""
🧪 COMPREHENSIVE STOCK ALERT TEST
{'=' * 60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST

This is a test email showing all integrated features:
✅ Gemma AI Top 10 Picks
✅ Top Dividend Stocks (600+ stocks scanned)
✅ Current Market Recommendations
✅ Streamlit Dashboard Status

{'=' * 60}

🤖 GEMMA AI TOP 10 PICKS
{'=' * 60}
"""
    
    # Add Gemma picks
    gemma_picks = gemma_data.get('picks', [])
    if gemma_picks:
        for i, pick in enumerate(gemma_picks[:10], 1):
            body += f"""
{i}. 📈 {pick['symbol']} - AI Score: {pick.get('ai_score', 0):.0f}/100
   💰 Price: ${pick['current_price']:.2f}
   📊 Growth: {pick.get('growth_potential', 0):.1f}% | RSI: {pick.get('rsi', 0):.1f}
   🎯 {pick.get('company_name', pick['symbol'])[:50]}
   💡 {pick.get('ai_reasoning', 'N/A')[:80]}
"""
        body += f"\n📅 Gemma Analysis Date: {gemma_data.get('analysis_date', 'N/A')[:10]}\n"
    else:
        body += "⚠️ No Gemma picks available. Run: python gemma_market_analysis.py\n"
    
    body += f"""

{'=' * 60}

💰 TOP DIVIDEND STOCKS (Income + Growth)
{'=' * 60}
"""
    
    # Add dividend stocks
    top_dividends = dividend_data.get('top_50_dividend_stocks', [])[:10]
    if top_dividends:
        for i, stock in enumerate(top_dividends, 1):
            body += f"""
{i}. 💎 {stock['symbol']} - {stock.get('category', 'Dividend')}
   💰 Price: ${stock['current_price']:.2f} | Yield: {stock['dividend_yield']:.2f}%
   📈 1M Growth: {stock['change_1m']:+.2f}% | Score: {stock['dividend_score']:.0f}/100
   🏢 {stock.get('company_name', stock['symbol'])[:50]}
   📊 Sector: {stock.get('sector', 'N/A')}
"""
        
        body += f"""
📊 Dividend Analysis Summary:
   • Total stocks scanned: {dividend_data.get('total_scanned', 533)}
   • Dividend stocks found: {dividend_data.get('total_dividend_stocks', 0)}
   • Last updated: {dividend_data.get('generated_at', 'N/A')[:10]}
"""
    else:
        body += "⚠️ No dividend data available. Run: python dividend_stock_analyzer.py\n"
    
    body += f"""

{'=' * 60}

🚀 CURRENT MARKET RECOMMENDATIONS
{'=' * 60}
"""
    
    # Add current recommendations
    buy_signals = recommendations.get('buy_signals', [])
    watch_signals = recommendations.get('watch_signals', [])
    
    if buy_signals:
        body += f"\n🚀 BUY Signals: {len(buy_signals)} stocks\n\n"
        for i, signal in enumerate(buy_signals[:5], 1):
            body += f"{i}. 📈 {signal['symbol']} - Score: {signal.get('score', 0)}/10\n"
            body += f"   💰 ${signal.get('current_price', 0):.2f} | RSI: {signal.get('rsi', 0):.1f}\n"
    else:
        body += "⚠️ No BUY signals currently\n"
    
    if watch_signals:
        body += f"\n👀 WATCH Signals: {len(watch_signals)} stocks\n"
        watch_list = [f"{s['symbol']}({s.get('score', 0)})" for s in watch_signals[:10]]
        body += f"   {', '.join(watch_list)}\n"
    
    body += f"""

{'=' * 60}

📊 STREAMLIT DASHBOARD STATUS
{'=' * 60}
"""
    
    # Add Streamlit status
    if streamlit_summary:
        body += f"""
✅ Dashboard: https://mcp-stock-alert-kiro-enhanced.streamlit.app/

📱 Available Pages:
   1. 🏠 Dashboard - Main overview
   2. 🤖 Gemma AI Top 10 - AI-powered picks
   3. 💰 Top 50 Dividends - Income + growth stocks
   4. 📊 Market Analysis - Technical analysis
   5. ⚙️ Settings - Configuration

📊 Data Status:
   • Gemma picks: {'✅ Available' if streamlit_summary.get('gemma_available') else '❌ Not available'}
   • Dividend stocks: {'✅ Available' if streamlit_summary.get('dividend_available') else '❌ Not available'}
   • Recommendations: {'✅ Available' if streamlit_summary.get('recommendations_available') else '❌ Not available'}
   • Last update: {streamlit_summary.get('last_update', 'N/A')}
"""
    else:
        body += "⚠️ Streamlit summary not available\n"
    
    body += f"""

{'=' * 60}

🔄 SYSTEM STATUS
{'=' * 60}

✅ Email alerts: Active
✅ Telegram notifications: Configured
✅ Daily auto-updates: Scheduled via GitHub Actions
✅ Streamlit Cloud: Auto-deploy on push

📋 Data Files Status:
   • gemma_top_10_picks.json: {'✅' if os.path.exists('gemma_top_10_picks.json') else '❌'}
   • top_50_dividend_stocks.json: {'✅' if os.path.exists('top_50_dividend_stocks.json') else '❌'}
   • last_recommendations.json: {'✅' if os.path.exists('last_recommendations.json') else '❌'}
   • streamlit_data_summary.json: {'✅' if os.path.exists('streamlit_data_summary.json') else '❌'}

{'=' * 60}

⚠️  NEXT STEPS
{'=' * 60}

To generate fresh data, run:

1. Gemma AI Analysis (10 min):
   python gemma_market_analysis.py

2. Dividend Analysis (5-10 min):
   python dividend_stock_analyzer.py

3. Update Streamlit Data:
   python update_streamlit_data.py

4. Or run all at once:
   python update_streamlit_data.py

{'=' * 60}

🤖 Generated by Agentic Stock Alert System
📊 Dashboard: https://mcp-stock-alert-kiro-enhanced.streamlit.app/
🔧 GitHub: https://github.com/masterai6612/mcp-stock-alert

⚠️ Disclaimer: This is for informational purposes only. Not financial advice.
Always do your own research before investing.
"""
    
    return subject, body

def send_telegram_message(message):
    """Send message to Telegram using urllib"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not configured")
        return False
    
    try:
        import urllib.request
        import urllib.parse
        
        # Split message if too long (Telegram limit: 4096 chars)
        max_length = 4000
        messages = []
        
        if len(message) <= max_length:
            messages = [message]
        else:
            # Split by sections
            parts = message.split('=' * 60)
            current_msg = ""
            
            for part in parts:
                if len(current_msg) + len(part) + 60 < max_length:
                    current_msg += '=' * 60 + part
                else:
                    if current_msg:
                        messages.append(current_msg)
                    current_msg = '=' * 60 + part
            
            if current_msg:
                messages.append(current_msg)
        
        # Send each part
        base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        for i, msg_part in enumerate(messages, 1):
            # URL encode the message (no parse_mode for plain text)
            params = urllib.parse.urlencode({
                'chat_id': TELEGRAM_CHAT_ID,
                'text': msg_part
            })
            
            url = f"{base_url}?{params}"
            
            try:
                response = urllib.request.urlopen(url)
                if response.status == 200:
                    print(f"✅ Telegram message sent (part {i}/{len(messages)})")
                else:
                    print(f"❌ Telegram error (part {i}): {response.status}")
                    return False
            except Exception as e:
                print(f"❌ Telegram error (part {i}): {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def send_email(subject, body):
    """Send email via Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        print(f"📧 Connecting to Gmail SMTP...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            print(f"🔐 Logging in as {EMAIL_FROM}...")
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            print(f"📤 Sending email to {EMAIL_TO}...")
            server.send_message(msg)
        
        print(f"✅ Email sent successfully!")
        print(f"📧 Check your inbox at {EMAIL_TO}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def main():
    """Main function"""
    print("🧪 COMPREHENSIVE TEST ALERT (Email + Telegram)")
    print("=" * 60)
    print(f"📧 Email From: {EMAIL_FROM}")
    print(f"📧 Email To: {EMAIL_TO}")
    print(f"🔐 Email Password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'NOT SET'}")
    print(f"📱 Telegram Bot: {'*' * 20 if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
    print(f"📱 Telegram Chat: {TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else 'NOT SET'}")
    print("=" * 60)
    
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD not set in .env file")
        return
    
    print("\n📝 Creating comprehensive alert...")
    subject, body = create_comprehensive_email()
    
    print(f"\n📋 Alert Preview:")
    print(f"Subject: {subject}")
    print(f"Body length: {len(body)} characters")
    print("\n" + "=" * 60)
    print(body[:500] + "...")
    print("=" * 60)
    
    # Send email
    print("\n📤 Sending email...")
    email_success = send_email(subject, body)
    
    # Send Telegram (without Markdown to avoid parsing errors)
    print("\n📱 Sending Telegram message...")
    telegram_body = f"{subject}\n\n{body}"
    telegram_success = send_telegram_message(telegram_body)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DELIVERY SUMMARY")
    print("=" * 60)
    print(f"📧 Email: {'✅ Sent' if email_success else '❌ Failed'}")
    print(f"📱 Telegram: {'✅ Sent' if telegram_success else '❌ Failed'}")
    
    if email_success or telegram_success:
        print("\n✅ TEST ALERT SENT!")
        if email_success:
            print(f"📧 Check your inbox at {EMAIL_TO}")
        if telegram_success:
            print(f"📱 Check your Telegram chat: {TELEGRAM_CHAT_ID}")
    else:
        print("\n❌ Failed to send test alert")

if __name__ == "__main__":
    main()
