#!/usr/bin/env python3
"""
Test Email Alert System
Sends a test email to verify the alert system is working
"""

import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from enhanced_yahoo_client import EnhancedYahooClient
import pandas as pd
from stock_change_tracker import track_watchlist_changes, get_stock_status, format_stock_with_status

# Email settings
EMAIL_TO = "masterai6612@gmail.com"
EMAIL_FROM = "masterai6612@gmail.com"
EMAIL_PASSWORD = "svpq udbt cnsf awab"  # Gmail app password

def get_technical_indicators(symbol, period="3mo"):
    """Get technical indicators for a stock"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
        
        # Calculate technical indicators
        close = hist['Close']
        volume = hist['Volume']
        
        # Moving averages
        ma_20 = close.rolling(window=20).mean()
        ma_50 = close.rolling(window=50).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        
        # Bollinger Bands
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Current values
        current_price = close.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        
        # Trend analysis
        ma20_current = ma_20.iloc[-1]
        ma50_current = ma_50.iloc[-1]
        
        trend = "NEUTRAL"
        if current_price > ma20_current > ma50_current and current_rsi < 70:
            trend = "BULLISH"
        elif current_price < ma20_current < ma50_current and current_rsi > 30:
            trend = "BEARISH"
        
        # Support/Resistance levels
        recent_high = close.tail(20).max()
        recent_low = close.tail(20).min()
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'ma_20': ma20_current,
            'ma_50': ma50_current,
            'rsi': current_rsi,
            'macd': current_macd,
            'macd_signal': current_signal,
            'bb_upper': bb_upper.iloc[-1],
            'bb_lower': bb_lower.iloc[-1],
            'trend': trend,
            'support': recent_low,
            'resistance': recent_high,
            'volume_avg': volume.tail(20).mean()
        }
    except Exception as e:
        print(f"Error getting technical indicators for {symbol}: {e}")
        return None

def get_market_indices():
    """Get major market indices data"""
    indices = {
        'S&P 500': '^GSPC',
        'NASDAQ': '^IXIC',
        'TSX': '^GSPTSE',
        'Dow Jones': '^DJI',
        'VIX': '^VIX'
    }
    
    market_data = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change_pct = ((current - previous) / previous) * 100
                
                market_data[name] = {
                    'current': current,
                    'change_pct': change_pct,
                    'symbol': symbol
                }
        except Exception as e:
            print(f"Error getting {name} data: {e}")
    
    return market_data

def analyze_upward_trends(symbols):
    """Analyze stocks for upward trend potential"""
    upward_candidates = []
    
    for symbol in symbols[:20]:  # Limit to first 20 for testing
        tech_data = get_technical_indicators(symbol)
        if tech_data:
            # Criteria for upward trend potential
            score = 0
            signals = []
            
            # RSI in good range (not overbought)
            if 30 < tech_data['rsi'] < 70:
                score += 2
                signals.append("RSI in healthy range")
            
            # Price above moving averages
            if tech_data['current_price'] > tech_data['ma_20']:
                score += 2
                signals.append("Above 20-day MA")
            
            if tech_data['ma_20'] > tech_data['ma_50']:
                score += 1
                signals.append("20-day MA > 50-day MA")
            
            # MACD bullish
            if tech_data['macd'] > tech_data['macd_signal']:
                score += 2
                signals.append("MACD bullish crossover")
            
            # Near support level (potential bounce)
            price_to_support = (tech_data['current_price'] - tech_data['support']) / tech_data['support'] * 100
            if 0 < price_to_support < 5:
                score += 1
                signals.append("Near support level")
            
            # Overall trend
            if tech_data['trend'] == "BULLISH":
                score += 3
                signals.append("Overall bullish trend")
            
            if score >= 5:  # Minimum score for upward potential
                upward_candidates.append({
                    'symbol': symbol,
                    'score': score,
                    'signals': signals,
                    'tech_data': tech_data
                })
    
    # Sort by score
    upward_candidates.sort(key=lambda x: x['score'], reverse=True)
    return upward_candidates

def send_test_email():
    """Send a comprehensive test email"""
    print("🚀 Generating comprehensive market analysis...")
    
    # Get enhanced data
    client = EnhancedYahooClient()
    earnings = client.get_earnings_calendar(days_ahead=7)
    themes = client.get_investment_themes()
    
    # Get market indices
    market_data = get_market_indices()
    
    # Test symbols for upward trend analysis
    test_symbols = [
        "AAPL", "MSFT", "GOOGL", "NVDA", "AMD", "TSLA", "META", "AMZN",
        "SHOP", "TD", "BNS", "ENB", "SLF", "JPM", "BAC", "XOM", "CVX"
    ]
    
    # Track changes in test watchlist
    changes = track_watchlist_changes("test_watchlist", test_symbols)
    
    # Analyze upward trends
    upward_trends = analyze_upward_trends(test_symbols)
    
    # Create email content
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    
    # Add change indicator to subject if there are changes
    subject = f"🚀 Market Analysis & Upward Trend Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if changes['has_changes']:
        subject += " 🆕 WATCHLIST UPDATED"
    msg['Subject'] = subject
    
    # Email body
    body = f"""
🚀 COMPREHENSIVE MARKET ANALYSIS & ALERTS
=========================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Add watchlist changes section if there are changes
    if changes['has_changes']:
        body += f"""

🔄 WATCHLIST CHANGES (Last 24 Hours)
===================================
"""
        if changes['added']:
            body += f"🆕 NEWLY ADDED STOCKS: {', '.join(changes['added'])}\n"
        if changes['removed']:
            body += f"❌ REMOVED STOCKS: {', '.join(changes['removed'])}\n"
        body += f"📊 Total stocks monitored: {len(test_symbols)}\n"
    
    body += f"""

📊 MAJOR MARKET INDICES
=======================
"""
    
    for name, data in market_data.items():
        trend_emoji = "📈" if data['change_pct'] > 0 else "📉" if data['change_pct'] < 0 else "➡️"
        body += f"{trend_emoji} {name}: {data['current']:.2f} ({data['change_pct']:+.2f}%)\n"
    
    body += f"""

🎯 UPWARD TREND CANDIDATES ({len(upward_trends)} found)
=====================================================
"""
    
    for i, candidate in enumerate(upward_trends[:10], 1):
        tech = candidate['tech_data']
        
        # Add status indicator for newly added stocks
        symbol_display = format_stock_with_status(candidate['symbol'], "test_watchlist")
        
        body += f"""
{i}. {symbol_display} - Score: {candidate['score']}/10
   💰 Price: ${tech['current_price']:.2f}
   📈 Trend: {tech['trend']}
   🎯 RSI: {tech['rsi']:.1f}
   📊 20-day MA: ${tech['ma_20']:.2f}
   📊 50-day MA: ${tech['ma_50']:.2f}
   🔄 MACD: {tech['macd']:.3f} / Signal: {tech['macd_signal']:.3f}
   📍 Support: ${tech['support']:.2f} | Resistance: ${tech['resistance']:.2f}
   
   🔍 Signals:
"""
        for signal in candidate['signals']:
            body += f"      ✅ {signal}\n"
    
    body += f"""

📅 UPCOMING EARNINGS (Next 7 Days)
==================================
"""
    
    if earnings:
        for earning in earnings[:10]:
            body += f"📅 {earning.get('symbol', 'N/A')}: {earning.get('company', 'N/A')} - {earning.get('date', 'N/A')}\n"
    else:
        body += "No earnings data available\n"
    
    body += f"""

🎯 TOP INVESTMENT THEMES
========================
"""
    
    if themes and themes.get('themes'):
        for theme in themes['themes'][:5]:
            body += f"🎯 {theme['theme']}: {theme['avg_change_percent']:+.2f}%\n"
    
    body += f"""

📈 TOP PERFORMING SECTORS
=========================
"""
    
    if themes and themes.get('trending_sectors'):
        for sector in themes['trending_sectors'][:5]:
            body += f"📈 {sector['sector']}: {sector['change_percent_5d']:+.2f}%\n"
    
    body += f"""

⏰ TRADING SCHEDULE REMINDER
============================
📍 Pre-Market: 4:00 AM - 9:30 AM EST
📍 Regular Hours: 9:30 AM - 4:00 PM EST  
📍 After-Hours: 4:00 PM - 8:00 PM EST

🔔 ALERT SETTINGS
=================
✅ Morning alerts: 7:30 AM - 9:30 AM EST
✅ Upward trend detection: Active
✅ Technical analysis: RSI, MACD, Moving Averages
✅ Multi-market coverage: NYSE, NASDAQ, TSX

📊 TECHNICAL ANALYSIS CRITERIA
==============================
• RSI between 30-70 (healthy range)
• Price above 20-day moving average
• MACD bullish crossover
• Overall bullish trend confirmation
• Support/resistance level analysis

This is a test email to verify the alert system is working correctly.
Next scheduled alert: Tomorrow at 7:30 AM EST
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        print(f"📧 Sent to: {EMAIL_TO}")
        print(f"📊 Found {len(upward_trends)} upward trend candidates")
        print(f"📅 Found {len(earnings) if earnings else 0} upcoming earnings")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    send_test_email()