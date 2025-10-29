#!/usr/bin/env python3
"""
Scheduled Market Alert System
Runs alerts at 7:30 AM and monitors for upward trends throughout the day
"""

import schedule
import time
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import holidays
from enhanced_yahoo_client import EnhancedYahooClient
import json
import os
from stock_change_tracker import track_watchlist_changes, get_stock_status, format_stock_with_status

# Email settings
EMAIL_TO = "masterai6612@gmail.com"
EMAIL_FROM = "masterai6612@gmail.com"
EMAIL_PASSWORD = "svpq udbt cnsf awab"

# Tracking file for sent alerts
ALERTS_FILE = "sent_alerts.json"

def load_sent_alerts():
    """Load previously sent alerts to avoid duplicates"""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_sent_alerts(alerts):
    """Save sent alerts to file"""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

def is_market_open():
    """Check if market is open"""
    today = datetime.now().date()
    us_holidays = holidays.US(years=today.year)
    ca_holidays = holidays.CA(years=today.year)
    
    # Check if it's a weekday and not a holiday
    weekday_open = today.weekday() < 5
    holiday = today in us_holidays or today in ca_holidays
    
    return weekday_open and not holiday

def is_trading_hours():
    """Check if it's during trading hours (9:30 AM - 4:00 PM EST)"""
    now = datetime.now()
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close and is_market_open()

def is_pre_market():
    """Check if it's pre-market hours (7:30 AM - 9:30 AM EST)"""
    now = datetime.now()
    pre_market_start = now.replace(hour=7, minute=30, second=0, microsecond=0)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    
    return pre_market_start <= now < market_open and is_market_open()

def get_technical_score(symbol):
    """Get technical analysis score for a stock"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        
        if hist.empty:
            return None
        
        close = hist['Close']
        volume = hist['Volume']
        
        # Technical indicators
        ma_20 = close.rolling(window=20).mean().iloc[-1]
        ma_50 = close.rolling(window=50).mean().iloc[-1]
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd = (exp1 - exp2).iloc[-1]
        signal = macd.ewm(span=9).mean().iloc[-1]
        
        current_price = close.iloc[-1]
        
        # Scoring system
        score = 0
        signals = []
        
        # Price momentum
        if current_price > ma_20:
            score += 2
            signals.append("Above 20-day MA")
        
        if ma_20 > ma_50:
            score += 1
            signals.append("20-day > 50-day MA")
        
        # RSI conditions
        if 40 < rsi < 70:
            score += 2
            signals.append(f"RSI healthy ({rsi:.1f})")
        elif rsi < 30:
            score += 1
            signals.append(f"RSI oversold ({rsi:.1f})")
        
        # MACD
        if macd > signal:
            score += 2
            signals.append("MACD bullish")
        
        # Volume analysis
        avg_volume = volume.tail(20).mean()
        recent_volume = volume.iloc[-1]
        if recent_volume > avg_volume * 1.2:
            score += 1
            signals.append("High volume")
        
        return {
            'symbol': symbol,
            'score': score,
            'signals': signals,
            'current_price': current_price,
            'rsi': rsi,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'macd': macd
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def morning_market_alert():
    """Send morning market analysis"""
    if not is_market_open():
        print("Market closed today - skipping morning alert")
        return
    
    print("🌅 Sending morning market alert...")
    
    # Get market data
    client = EnhancedYahooClient()
    earnings = client.get_earnings_calendar(days_ahead=7)
    themes = client.get_investment_themes()
    
    # Import comprehensive stock universe
    from stock_universe import get_comprehensive_stock_list
    
    # Get expanded stock list but limit for morning analysis (performance)
    all_stocks = get_comprehensive_stock_list()
    
    # For morning alerts, focus on top 120 most liquid stocks for faster processing
    key_stocks = all_stocks[:120]  # Top 120 from comprehensive list
    
    # Track changes in watchlist
    changes = track_watchlist_changes("morning_watchlist", key_stocks)
    
    strong_candidates = []
    for symbol in key_stocks:
        analysis = get_technical_score(symbol)
        if analysis and analysis['score'] >= 5:
            strong_candidates.append(analysis)
    
    # Sort by score
    strong_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Create email
    subject = f"🌅 Morning Market Alert - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Add change indicator to subject if there are changes
    if changes['has_changes']:
        subject += " 🆕 WATCHLIST UPDATED"
    
    body = f"""
🌅 MORNING MARKET ALERT
======================
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST
"""
    
    # Add watchlist changes section if there are changes
    if changes['has_changes']:
        body += f"""

🔄 WATCHLIST CHANGES
===================
"""
        if changes['added']:
            body += f"🆕 NEWLY ADDED: {', '.join(changes['added'])}\n"
        if changes['removed']:
            body += f"❌ REMOVED: {', '.join(changes['removed'])}\n"
        body += "\n"
    
    body += f"""
🎯 STRONG TECHNICAL CANDIDATES ({len(strong_candidates)} found)
========================================================
"""
    
    for candidate in strong_candidates[:8]:
        # Add status indicator for newly added stocks
        symbol_display = format_stock_with_status(candidate['symbol'], "morning_watchlist")
        
        body += f"""
📈 {symbol_display} - Score: {candidate['score']}/10
   💰 Price: ${candidate['current_price']:.2f}
   🎯 RSI: {candidate['rsi']:.1f}
   📊 20-day MA: ${candidate['ma_20']:.2f}
   
   Signals: {', '.join(candidate['signals'])}
"""
    
    body += f"""

📅 TODAY'S EARNINGS TO WATCH
============================
"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    todays_earnings = [e for e in earnings if e.get('date') == today] if earnings else []
    
    if todays_earnings:
        for earning in todays_earnings[:5]:
            body += f"📅 {earning.get('symbol', 'N/A')}: {earning.get('company', 'N/A')}\n"
    else:
        body += "No major earnings today\n"
    
    body += f"""

🎯 HOT THEMES TODAY
==================
"""
    
    if themes and themes.get('themes'):
        for theme in themes['themes'][:3]:
            body += f"🔥 {theme['theme']}: {theme['avg_change_percent']:+.2f}%\n"
    
    body += f"""

⏰ TRADING SCHEDULE
==================
📍 Pre-Market: 4:00 AM - 9:30 AM EST
📍 Regular Hours: 9:30 AM - 4:00 PM EST
📍 After-Hours: 4:00 PM - 8:00 PM EST

Good luck trading today! 🚀
"""
    
    send_email(subject, body)

def check_upward_trends():
    """Check for new upward trend opportunities during trading hours"""
    if not is_trading_hours():
        return
    
    print("🔍 Checking for upward trends...")
    
    # Load previously sent alerts
    sent_alerts = load_sent_alerts()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today not in sent_alerts:
        sent_alerts[today] = []
    
    # Import comprehensive stock universe
    from stock_universe import get_comprehensive_stock_list
    
    # Monitor expanded stock list but limit for intraday analysis (performance)
    all_stocks = get_comprehensive_stock_list()
    
    # For intraday monitoring, use top 180 stocks for balance of coverage vs performance
    monitor_stocks = all_stocks[:180]
    
    # Track changes in monitoring list
    changes = track_watchlist_changes("trend_monitoring", monitor_stocks)
    
    new_opportunities = []
    
    for symbol in monitor_stocks:
        if symbol in sent_alerts[today]:
            continue  # Already sent alert for this stock today
        
        analysis = get_technical_score(symbol)
        if analysis and analysis['score'] >= 7:  # Higher threshold for intraday alerts
            new_opportunities.append(analysis)
            sent_alerts[today].append(symbol)
    
    if new_opportunities:
        # Sort by score
        new_opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        subject = f"🚀 Upward Trend Alert - {datetime.now().strftime('%H:%M')}"
        
        # Add change indicator if any of the opportunities are newly added stocks
        newly_added_in_opportunities = any(get_stock_status(opp['symbol'], "trend_monitoring") for opp in new_opportunities)
        if newly_added_in_opportunities:
            subject += " 🆕 NEW STOCKS"
        
        body = f"""
🚀 UPWARD TREND OPPORTUNITY DETECTED
===================================
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST

"""
        
        for opp in new_opportunities:
            # Add status indicator for newly added stocks
            symbol_display = format_stock_with_status(opp['symbol'], "trend_monitoring")
            
            body += f"""
📈 {symbol_display} - Strong Signal (Score: {opp['score']}/10)
   💰 Current Price: ${opp['current_price']:.2f}
   🎯 RSI: {opp['rsi']:.1f}
   📊 Above 20-day MA: ${opp['ma_20']:.2f}
   
   🔍 Technical Signals:
"""
            for signal in opp['signals']:
                body += f"      ✅ {signal}\n"
            
            body += "\n"
        
        body += """
⚠️  This is an automated alert based on technical analysis.
    Always do your own research before making investment decisions.

🔔 You will only receive one alert per stock per day to avoid spam.
"""
        
        send_email(subject, body)
        save_sent_alerts(sent_alerts)
        print(f"📧 Sent upward trend alert for {len(new_opportunities)} stocks")

def send_email(subject, body):
    """Send email alert"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent: {subject}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def main():
    """Main scheduler function"""
    print("🚀 Starting Scheduled Market Alert System")
    print("=" * 50)
    
    # Schedule morning alert
    schedule.every().day.at("07:30").do(morning_market_alert)
    
    # Schedule upward trend checks every 30 minutes during trading hours
    schedule.every(30).minutes.do(check_upward_trends)
    
    print("📅 Scheduled Jobs:")
    print("   🌅 Morning Alert: 7:30 AM EST (weekdays)")
    print("   🔍 Trend Monitoring: Every 30 minutes during trading hours")
    print("   📧 Email alerts to:", EMAIL_TO)
    print()
    print("🔄 System running... Press Ctrl+C to stop")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopping alert system...")
        print("System stopped successfully!")