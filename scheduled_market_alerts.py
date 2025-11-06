#!/usr/bin/env python3
"""
Scheduled Market Alert System
Runs every hour but only sends emails when stock recommendations change
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
import hashlib
import sys
import requests
from dotenv import load_dotenv
sys.path.append('utils')
from stock_change_tracker import track_watchlist_changes, get_stock_status, format_stock_with_status

# Load environment variables
load_dotenv()

# Email settings
EMAIL_TO = "masterai6612@gmail.com"
EMAIL_FROM = os.getenv('EMAIL_FROM', 'masterai6612@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'svpq udbt cnsf awab')

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Tracking files
ALERTS_FILE = "sent_alerts.json"
RECOMMENDATIONS_FILE = "last_recommendations.json"
OVERNIGHT_ACTIONS_FILE = "overnight_actions.json"
LOG_FILE = "scheduled_alerts.log"

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

def load_last_recommendations():
    """Load last recommendations to detect changes"""
    if os.path.exists(RECOMMENDATIONS_FILE):
        try:
            with open(RECOMMENDATIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading recommendations: {e}")
    return {"buy_signals": [], "watch_signals": [], "timestamp": None}

def save_recommendations(recommendations):
    """Save current recommendations"""
    try:
        with open(RECOMMENDATIONS_FILE, 'w') as f:
            json.dump(recommendations, f, indent=2)
    except Exception as e:
        print(f"Error saving recommendations: {e}")

def log_message(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    
    # Print to console
    print(message)
    
    # Write to log file
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        print(f"Error writing to log file: {e}")

def load_overnight_actions():
    """Load overnight actions tracking"""
    if os.path.exists(OVERNIGHT_ACTIONS_FILE):
        try:
            with open(OVERNIGHT_ACTIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            log_message(f"Error loading overnight actions: {e}")
    return {"actions": [], "last_reset": None}

def save_overnight_actions(actions_data):
    """Save overnight actions tracking"""
    try:
        with open(OVERNIGHT_ACTIONS_FILE, 'w') as f:
            json.dump(actions_data, f, indent=2)
    except Exception as e:
        log_message(f"Error saving overnight actions: {e}")

def is_overnight_period():
    """Check if current time is in overnight period (8 PM to 7 AM)"""
    now = datetime.now()
    overnight_start = now.replace(hour=20, minute=0, second=0, microsecond=0)
    overnight_end = now.replace(hour=7, minute=0, second=0, microsecond=0)
    
    # Handle overnight period crossing midnight
    if now.hour >= 20 or now.hour < 7:
        return True
    return False

def track_overnight_action(action_type, details):
    """Track actions that happen during overnight period"""
    if not is_overnight_period():
        return
    
    actions_data = load_overnight_actions()
    
    action = {
        'timestamp': datetime.now().isoformat(),
        'type': action_type,
        'details': details,
        'session': get_market_session()
    }
    
    actions_data['actions'].append(action)
    save_overnight_actions(actions_data)
    
    log_message(f"📝 Overnight action tracked: {action_type} - {details}")

def reset_overnight_actions():
    """Reset overnight actions at 7 AM"""
    actions_data = {
        "actions": [],
        "last_reset": datetime.now().isoformat()
    }
    save_overnight_actions(actions_data)
    log_message("🔄 Overnight actions reset for new day")

def get_recommendations_hash(buy_signals, watch_signals):
    """Generate hash of current recommendations for change detection"""
    # Sort signals to ensure consistent hashing
    buy_sorted = sorted([s['symbol'] for s in buy_signals])
    watch_sorted = sorted([s['symbol'] for s in watch_signals])
    
    combined = f"{','.join(buy_sorted)}|{','.join(watch_sorted)}"
    return hashlib.md5(combined.encode()).hexdigest()

def detect_significant_changes(current_buy, current_watch):
    """Detect significant changes in recommendations with enhanced logic"""
    last_data = load_last_recommendations()
    
    # Get current symbols with scores
    current_buy_data = {s['symbol']: s['score'] for s in current_buy}
    current_watch_data = {s['symbol']: s['score'] for s in current_watch}
    
    # Get previous symbols with scores
    last_buy_data = {s['symbol']: s['score'] for s in last_data.get('buy_signals', [])}
    last_watch_data = {s['symbol']: s['score'] for s in last_data.get('watch_signals', [])}
    
    # Current and previous symbol sets
    current_buy_symbols = set(current_buy_data.keys())
    current_watch_symbols = set(current_watch_data.keys())
    last_buy_symbols = set(last_buy_data.keys())
    last_watch_symbols = set(last_watch_data.keys())
    
    # Detect symbol changes
    new_buy = current_buy_symbols - last_buy_symbols
    removed_buy = last_buy_symbols - current_buy_symbols
    new_watch = current_watch_symbols - last_watch_symbols
    removed_watch = last_watch_symbols - current_watch_symbols
    
    # Detect significant score changes (≥2 points) for existing stocks
    score_upgrades = []
    score_downgrades = []
    
    # Check BUY signals for score changes
    for symbol in current_buy_symbols & last_buy_symbols:
        current_score = current_buy_data[symbol]
        last_score = last_buy_data[symbol]
        if current_score - last_score >= 2:
            score_upgrades.append(f"{symbol} ({last_score}→{current_score})")
        elif last_score - current_score >= 2:
            score_downgrades.append(f"{symbol} ({last_score}→{current_score})")
    
    # Check WATCH signals for score changes
    for symbol in current_watch_symbols & last_watch_symbols:
        current_score = current_watch_data[symbol]
        last_score = last_watch_data[symbol]
        if current_score - last_score >= 2:
            score_upgrades.append(f"{symbol} ({last_score}→{current_score})")
        elif last_score - current_score >= 2:
            score_downgrades.append(f"{symbol} ({last_score}→{current_score})")
    
    # Check for promotions/demotions between BUY and WATCH
    promotions = []  # WATCH → BUY
    demotions = []   # BUY → WATCH
    
    for symbol in new_buy:
        if symbol in last_watch_symbols:
            promotions.append(symbol)
    
    for symbol in new_watch:
        if symbol in last_buy_symbols:
            demotions.append(symbol)
    
    # Determine if changes are significant enough to send email
    significant_changes = bool(
        new_buy or removed_buy or  # New/removed BUY signals always significant
        len(new_watch) >= 3 or len(removed_watch) >= 3 or  # Multiple WATCH changes
        score_upgrades or score_downgrades or  # Score changes ≥2 points
        promotions or demotions  # Promotions/demotions between categories
    )
    
    return {
        'has_changes': significant_changes,
        'new_buy': list(new_buy),
        'removed_buy': list(removed_buy),
        'new_watch': list(new_watch),
        'removed_watch': list(removed_watch),
        'score_upgrades': score_upgrades,
        'score_downgrades': score_downgrades,
        'promotions': promotions,
        'demotions': demotions,
        'last_update': last_data.get('timestamp'),
        'change_summary': get_change_summary(new_buy, removed_buy, new_watch, removed_watch, 
                                           score_upgrades, score_downgrades, promotions, demotions)
    }

def get_change_summary(new_buy, removed_buy, new_watch, removed_watch, 
                      score_upgrades, score_downgrades, promotions, demotions):
    """Generate a summary of changes for logging"""
    changes = []
    if new_buy:
        changes.append(f"+{len(new_buy)} BUY")
    if removed_buy:
        changes.append(f"-{len(removed_buy)} BUY")
    if new_watch:
        changes.append(f"+{len(new_watch)} WATCH")
    if removed_watch:
        changes.append(f"-{len(removed_watch)} WATCH")
    if score_upgrades:
        changes.append(f"{len(score_upgrades)} upgrades")
    if score_downgrades:
        changes.append(f"{len(score_downgrades)} downgrades")
    if promotions:
        changes.append(f"{len(promotions)} promotions")
    if demotions:
        changes.append(f"{len(demotions)} demotions")
    
    return ", ".join(changes) if changes else "No significant changes"

def is_market_day():
    """Check if it's a market day (weekday, not holiday)"""
    today = datetime.now().date()
    us_holidays = holidays.US(years=today.year)
    ca_holidays = holidays.CA(years=today.year)
    
    # Check if it's a weekday and not a holiday
    weekday_open = today.weekday() < 5
    holiday = today in us_holidays or today in ca_holidays
    
    return weekday_open and not holiday

def get_market_session():
    """Get current market session type"""
    now = datetime.now()
    
    # Market session times (EST)
    pre_market_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
    regular_market_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
    regular_market_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
    after_hours_end = now.replace(hour=20, minute=0, second=0, microsecond=0)
    
    if not is_market_day():
        return "CLOSED"
    
    if pre_market_start <= now < regular_market_start:
        return "PRE_MARKET"
    elif regular_market_start <= now <= regular_market_end:
        return "REGULAR_HOURS"
    elif regular_market_end < now <= after_hours_end:
        return "AFTER_HOURS"
    else:
        return "CLOSED"

def is_trading_session():
    """Check if it's any trading session (pre-market, regular, or after-hours)"""
    session = get_market_session()
    return session in ["PRE_MARKET", "REGULAR_HOURS", "AFTER_HOURS"]

def should_run_analysis():
    """Determine if analysis should run based on current time and session"""
    session = get_market_session()
    now = datetime.now()
    
    # Always run during market days in trading sessions
    if session in ["PRE_MARKET", "REGULAR_HOURS", "AFTER_HOURS"]:
        return True
    
    # Run limited analysis on weekends for international markets and crypto-related stocks
    if now.weekday() >= 5:  # Weekend
        # Run analysis at 8 AM and 8 PM on weekends for international exposure
        if now.hour in [8, 20]:
            return True
    
    return False

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
        macd_line = exp1 - exp2
        macd = macd_line.iloc[-1]
        signal = macd_line.ewm(span=9).mean().iloc[-1]
        
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

def analyze_market_24x7():
    """24/7 market analysis with session-aware monitoring"""
    now = datetime.now()
    session = get_market_session()
    
    if not should_run_analysis():
        log_message(f"⏰ {now.strftime('%H:%M')} - Outside monitoring hours, skipping analysis")
        return
    
    log_message(f"🔍 Running {session} analysis at {now.strftime('%H:%M')} ({now.strftime('%A')})")
    
    # Get market data (with error handling for off-hours)
    try:
        client = EnhancedYahooClient()
        earnings = client.get_earnings_calendar(days_ahead=7)
        themes = client.get_investment_themes()
    except Exception as e:
        print(f"⚠️ Market data unavailable: {e}")
        earnings = None
        themes = None
    
    # Import comprehensive stock universe
    from stock_universe import get_comprehensive_stock_list
    all_stocks = get_comprehensive_stock_list()
    
    # Adjust stock coverage based on session - NOW USING FULL UNIVERSE!
    if session == "REGULAR_HOURS":
        monitor_stocks = all_stocks  # FULL 600+ stock universe during regular hours
        buy_threshold = 7
        watch_threshold = 5
    elif session in ["PRE_MARKET", "AFTER_HOURS"]:
        monitor_stocks = all_stocks[:400]  # 400 stocks during extended hours (US + top Canadian)
        buy_threshold = 8  # Higher threshold for extended hours
        watch_threshold = 6
    else:  # Weekend/off-hours
        monitor_stocks = all_stocks[:200]   # 200 stocks for international exposure
        buy_threshold = 8
        watch_threshold = 6
    
    log_message(f"📊 Analyzing {len(monitor_stocks)} stocks (thresholds: BUY≥{buy_threshold}, WATCH≥{watch_threshold})")
    
    # Analyze stocks with progress tracking
    buy_signals = []
    watch_signals = []
    analyzed_count = 0
    
    for i, symbol in enumerate(monitor_stocks):
        try:
            analysis = get_technical_score(symbol)
            if analysis:
                if analysis['score'] >= buy_threshold:
                    buy_signals.append(analysis)
                elif analysis['score'] >= watch_threshold:
                    watch_signals.append(analysis)
            analyzed_count += 1
            
            # Progress update every 25 stocks
            if (i + 1) % 25 == 0:
                log_message(f"   📈 Analyzed {i + 1}/{len(monitor_stocks)} stocks...")
                
        except Exception as e:
            log_message(f"⚠️ Error analyzing {symbol}: {e}")
            continue
    
    # Sort by score
    buy_signals.sort(key=lambda x: x['score'], reverse=True)
    watch_signals.sort(key=lambda x: x['score'], reverse=True)
    
    # Check for significant changes
    changes = detect_significant_changes(buy_signals, watch_signals)
    
    log_message(f"📊 Analysis complete: {len(buy_signals)} BUY, {len(watch_signals)} WATCH signals")
    log_message(f"🔄 Changes: {changes['change_summary']}")
    
    # Track overnight actions if applicable
    if is_overnight_period() and changes['has_changes']:
        track_overnight_action("significant_changes", {
            'buy_signals': len(buy_signals),
            'watch_signals': len(watch_signals),
            'changes': changes['change_summary'],
            'new_buy': changes['new_buy'],
            'removed_buy': changes['removed_buy'],
            'promotions': changes['promotions'],
            'demotions': changes['demotions']
        })
    
    if changes['has_changes']:
        log_message("🚨 Significant changes detected - sending email alert!")
        send_enhanced_alert(buy_signals, watch_signals, changes, earnings, themes, session)
        
        # Save current recommendations
        save_recommendations({
            'buy_signals': buy_signals,
            'watch_signals': watch_signals,
            'timestamp': now.isoformat(),
            'session': session,
            'analyzed_stocks': analyzed_count
        })
    else:
        log_message("✅ No significant changes - no email sent")
        log_message(f"   Current: {len(buy_signals)} BUY, {len(watch_signals)} WATCH")
        
        # Still update timestamp to track last analysis
        last_data = load_last_recommendations()
        last_data['timestamp'] = now.isoformat()
        last_data['session'] = session
        save_recommendations(last_data)

def send_enhanced_alert(buy_signals, watch_signals, changes, earnings=None, themes=None, session="REGULAR_HOURS"):
    """Send enhanced email alert with session-aware formatting"""
    now = datetime.now()
    
    # Determine alert type based on session and time
    session_icons = {
        "PRE_MARKET": "🌅",
        "REGULAR_HOURS": "🌞" if now.hour < 14 else "🌆",
        "AFTER_HOURS": "🌙",
        "CLOSED": "💤"
    }
    
    session_names = {
        "PRE_MARKET": "Pre-Market",
        "REGULAR_HOURS": "Market Hours",
        "AFTER_HOURS": "After-Hours",
        "CLOSED": "Off-Hours"
    }
    
    icon = session_icons.get(session, "📊")
    session_name = session_names.get(session, "Market")
    
    subject = f"{icon} {session_name} Alert - Significant Changes ({now.strftime('%H:%M')})"
    
    # Enhanced subject with change summary
    change_parts = []
    if changes['new_buy']:
        change_parts.append(f"🚀{len(changes['new_buy'])}NEW")
    if changes['removed_buy']:
        change_parts.append(f"❌{len(changes['removed_buy'])}OUT")
    if changes['promotions']:
        change_parts.append(f"⬆️{len(changes['promotions'])}UP")
    if changes['demotions']:
        change_parts.append(f"⬇️{len(changes['demotions'])}DOWN")
    
    if change_parts:
        subject += f" [{' '.join(change_parts)}]"
    
    body = f"""
{icon} {session_name.upper()} STOCK ALERT - SIGNIFICANT CHANGES
{'=' * 60}
{now.strftime('%Y-%m-%d %H:%M:%S')} EST | {now.strftime('%A')}
Session: {session_name} | Monitoring: 24/7

🔄 SIGNIFICANT CHANGES DETECTED
===============================
"""
    
    if changes['last_update']:
        last_time = datetime.fromisoformat(changes['last_update'])
        time_diff = now - last_time
        hours_ago = int(time_diff.total_seconds() / 3600)
        minutes_ago = int((time_diff.total_seconds() % 3600) / 60)
        if hours_ago > 0:
            body += f"⏰ Last update: {hours_ago}h {minutes_ago}m ago\n\n"
        else:
            body += f"⏰ Last update: {minutes_ago} minutes ago\n\n"
    
    # Enhanced change reporting
    if changes['new_buy']:
        body += f"🚀 NEW BUY SIGNALS ({len(changes['new_buy'])}): {', '.join(changes['new_buy'])}\n"
    if changes['removed_buy']:
        body += f"❌ REMOVED BUY SIGNALS ({len(changes['removed_buy'])}): {', '.join(changes['removed_buy'])}\n"
    if changes['promotions']:
        body += f"⬆️ PROMOTED TO BUY ({len(changes['promotions'])}): {', '.join(changes['promotions'])}\n"
    if changes['demotions']:
        body += f"⬇️ DEMOTED TO WATCH ({len(changes['demotions'])}): {', '.join(changes['demotions'])}\n"
    if changes['score_upgrades']:
        body += f"📈 SCORE UPGRADES ({len(changes['score_upgrades'])}): {', '.join(changes['score_upgrades'])}\n"
    if changes['score_downgrades']:
        body += f"📉 SCORE DOWNGRADES ({len(changes['score_downgrades'])}): {', '.join(changes['score_downgrades'])}\n"
    if changes['new_watch']:
        body += f"👀 NEW WATCH SIGNALS ({len(changes['new_watch'])}): {', '.join(changes['new_watch'])}\n"
    if changes['removed_watch']:
        body += f"📉 REMOVED WATCH SIGNALS ({len(changes['removed_watch'])}): {', '.join(changes['removed_watch'])}\n"
    
    body += f"""

🚀 CURRENT BUY SIGNALS ({len(buy_signals)} stocks)
===============================================
"""
    
    for signal in buy_signals[:10]:  # Top 10 buy signals
        is_new = signal['symbol'] in changes['new_buy']
        new_indicator = " 🆕 NEW!" if is_new else ""
        
        body += f"""
📈 {signal['symbol']}{new_indicator} - Score: {signal['score']}/10
   💰 Price: ${signal['current_price']:.2f}
   🎯 RSI: {signal['rsi']:.1f}
   📊 20-day MA: ${signal['ma_20']:.2f}
   
   Signals: {', '.join(signal['signals'])}
"""
    
    if len(buy_signals) > 10:
        remaining_buy = [s['symbol'] for s in buy_signals[10:]]
        body += f"\n📋 Additional BUY signals: {', '.join(remaining_buy)}\n"
    
    body += f"""

👀 CURRENT WATCH SIGNALS ({len(watch_signals)} stocks)
==================================================
"""
    
    for signal in watch_signals[:8]:  # Top 8 watch signals
        is_new = signal['symbol'] in changes['new_watch']
        new_indicator = " 🆕 NEW!" if is_new else ""
        
        body += f"""
📊 {signal['symbol']}{new_indicator} - Score: {signal['score']}/10
   💰 Price: ${signal['current_price']:.2f} | RSI: {signal['rsi']:.1f}
   Signals: {', '.join(signal['signals'][:2])}  # Limit signals for watch list
"""
    
    if len(watch_signals) > 8:
        remaining_watch = [s['symbol'] for s in watch_signals[8:]]
        body += f"\n📋 Additional WATCH signals: {', '.join(remaining_watch)}\n"
    
    # Add earnings if it's morning or if there are relevant earnings
    if earnings and (now.hour < 12 or any(e.get('date') == now.strftime('%Y-%m-%d') for e in earnings)):
        body += f"""

📅 TODAY'S EARNINGS TO WATCH
============================
"""
        today = now.strftime('%Y-%m-%d')
        todays_earnings = [e for e in earnings if e.get('date') == today] if earnings else []
        
        if todays_earnings:
            for earning in todays_earnings[:5]:
                body += f"📅 {earning.get('symbol', 'N/A')}: {earning.get('company', 'N/A')}\n"
        else:
            body += "No major earnings today\n"
    
    # Session-specific notes
    body += f"""

⚠️  IMPORTANT NOTES
==================
• Alert triggered by SIGNIFICANT changes only
• 24/7 monitoring: Pre-market (4AM-9:30AM), Regular (9:30AM-4PM), After-hours (4PM-8PM)
• {session_name} analysis with enhanced thresholds
• Weekend monitoring for international exposure
• Always do your own research before investing

📊 Next analysis: {(now + timedelta(hours=1)).strftime('%H:%M')} EST
🔄 Monitoring status: ACTIVE 24/7 during market days
"""
    
    # Add session-specific footer
    if session == "PRE_MARKET":
        body += "\n💡 Pre-market signals may have higher volatility - confirm at market open"
    elif session == "AFTER_HOURS":
        body += "\n💡 After-hours signals based on extended trading - verify volume and liquidity"
    elif session == "REGULAR_HOURS":
        body += "\n💡 Regular hours analysis with full market data and volume"
    
    send_email(subject, body)

def send_daily_summary():
    """Send comprehensive end-of-day summary"""
    if get_market_session() != "REGULAR_HOURS":
        return
    
    print("📊 Sending comprehensive daily summary...")
    
    # Get final recommendations for the day
    from stock_universe import get_comprehensive_stock_list
    all_stocks = get_comprehensive_stock_list()
    monitor_stocks = all_stocks[:250]  # Comprehensive end-of-day analysis
    
    buy_signals = []
    watch_signals = []
    
    for symbol in monitor_stocks:
        analysis = get_technical_score(symbol)
        if analysis:
            if analysis['score'] >= 7:
                buy_signals.append(analysis)
            elif analysis['score'] >= 5:
                watch_signals.append(analysis)
    
    buy_signals.sort(key=lambda x: x['score'], reverse=True)
    watch_signals.sort(key=lambda x: x['score'], reverse=True)
    
    # Get today's change statistics
    last_data = load_last_recommendations()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    subject = f"📊 Daily Market Summary - {datetime.now().strftime('%Y-%m-%d')} | 24/7 Monitoring"
    
    body = f"""
📊 END-OF-DAY COMPREHENSIVE SUMMARY
===================================
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST

🎯 FINAL RECOMMENDATIONS (24/7 MONITORING)
==========================================
🚀 BUY Signals: {len(buy_signals)} stocks (Score ≥7)
👀 WATCH Signals: {len(watch_signals)} stocks (Score ≥5)
📊 Total Analyzed: {len(monitor_stocks)} stocks

🚀 TOP BUY RECOMMENDATIONS
=========================
"""
    
    for i, signal in enumerate(buy_signals[:8], 1):
        body += f"""
{i}. 📈 {signal['symbol']} - Score: {signal['score']}/10
   💰 Price: ${signal['current_price']:.2f} | RSI: {signal['rsi']:.1f}
   📊 MA20: ${signal['ma_20']:.2f} | MACD: {signal['macd']:.3f}
   🎯 Signals: {', '.join(signal['signals'][:3])}
"""
    
    if len(buy_signals) > 8:
        remaining = [f"{s['symbol']}({s['score']})" for s in buy_signals[8:]]
        body += f"\n📋 Additional BUY signals: {', '.join(remaining)}\n"
    
    body += f"""

👀 TOP WATCH LIST (Potential Upgrades)
=====================================
"""
    
    for i, signal in enumerate(watch_signals[:10], 1):
        body += f"{i}. 📊 {signal['symbol']} (Score: {signal['score']}) - ${signal['current_price']:.2f} | RSI: {signal['rsi']:.1f}\n"
    
    if len(watch_signals) > 10:
        remaining = [f"{s['symbol']}({s['score']})" for s in watch_signals[10:]]
        body += f"\n📋 Additional WATCH: {', '.join(remaining)}\n"
    
    body += f"""

🌙 AFTER-HOURS & TOMORROW'S PLAN
================================
• 24/7 monitoring continues through after-hours (4PM-8PM EST)
• Pre-market analysis resumes at 4AM EST
• Email alerts ONLY for significant changes
• Higher thresholds during extended hours (BUY≥8, WATCH≥6)
• Weekend monitoring for international exposure

📊 MONITORING SCHEDULE
=====================
🌅 Pre-Market: 4:00 AM - 9:30 AM EST (Focused analysis)
🌞 Regular Hours: 9:30 AM - 4:00 PM EST (Full coverage)
🌙 After-Hours: 4:00 PM - 8:00 PM EST (Extended trading)
💤 Overnight: 8:00 PM - 4:00 AM EST (Paused)
🌍 Weekends: Limited international exposure monitoring

⚠️  SMART ALERT SYSTEM
======================
✅ Significant changes only (no spam)
✅ Score changes ≥2 points
✅ New/removed BUY signals
✅ Promotions/demotions between categories
✅ Multiple WATCH signal changes (≥3)

Good luck with after-hours and tomorrow's trading! 🚀
"""
    
    send_email(subject, body)

def send_weekend_summary():
    """Send weekend summary with international market exposure"""
    if datetime.now().weekday() < 5:  # Only on weekends
        return
        
    print("🌍 Sending weekend international exposure summary...")
    
    # Focus on international exposure stocks
    from stock_universe import get_comprehensive_stock_list
    all_stocks = get_comprehensive_stock_list()
    
    # Filter for stocks with international exposure
    international_symbols = [s for s in all_stocks if s in [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',  # Global tech
        'JPM', 'BAC', 'GS', 'MS',  # Global banks
        'XOM', 'CVX', 'COP',  # Energy with global operations
        'JNJ', 'PFE', 'UNH',  # Healthcare multinationals
        'KO', 'PEP', 'MCD', 'SBUX',  # Global consumer brands
        'DIS', 'NFLX', 'CMCSA'  # Global media
    ]][:30]  # Top 30 international exposure stocks
    
    buy_signals = []
    watch_signals = []
    
    for symbol in international_symbols:
        analysis = get_technical_score(symbol)
        if analysis:
            if analysis['score'] >= 8:  # Higher weekend threshold
                buy_signals.append(analysis)
            elif analysis['score'] >= 6:
                watch_signals.append(analysis)
    
    if not buy_signals and not watch_signals:
        return  # No weekend summary if no signals
    
    subject = f"🌍 Weekend International Exposure - {datetime.now().strftime('%Y-%m-%d')}"
    
    body = f"""
🌍 WEEKEND INTERNATIONAL MARKET EXPOSURE
=======================================
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST | {datetime.now().strftime('%A')}

📊 GLOBAL EXPOSURE ANALYSIS
===========================
🚀 Strong Signals: {len(buy_signals)} stocks (Score ≥8)
👀 Watch Signals: {len(watch_signals)} stocks (Score ≥6)
🌍 Focus: International exposure during Asian/European trading

"""
    
    if buy_signals:
        body += "🚀 STRONG INTERNATIONAL SIGNALS\n"
        body += "================================\n"
        for signal in buy_signals:
            body += f"📈 {signal['symbol']} - Score: {signal['score']}/10 | ${signal['current_price']:.2f}\n"
        body += "\n"
    
    if watch_signals:
        body += "👀 WATCH FOR MONDAY\n"
        body += "==================\n"
        for signal in watch_signals:
            body += f"📊 {signal['symbol']} - Score: {signal['score']}/10 | ${signal['current_price']:.2f}\n"
        body += "\n"
    
    body += """
📅 MONDAY PREPARATION
====================
• Pre-market analysis resumes Monday 4:00 AM EST
• Watch for gap ups/downs based on international news
• Focus on earnings calendar for the week
• Monitor geopolitical developments over weekend

🔄 System Status: Limited weekend monitoring active
"""
    
    send_email(subject, body)

def send_telegram_message(message, parse_mode='Markdown'):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log_message("⚠️ Telegram credentials not configured")
        return False
    
    try:
        # Split long messages (Telegram has 4096 character limit)
        max_length = 4000  # Leave some buffer
        
        if len(message) <= max_length:
            messages = [message]
        else:
            # Split message into chunks
            messages = []
            current_msg = ""
            lines = message.split('\n')
            
            for line in lines:
                if len(current_msg + line + '\n') <= max_length:
                    current_msg += line + '\n'
                else:
                    if current_msg:
                        messages.append(current_msg.strip())
                    current_msg = line + '\n'
            
            if current_msg:
                messages.append(current_msg.strip())
        
        # Send each message part
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        for i, msg_part in enumerate(messages):
            if i > 0:
                msg_part = f"📄 *Part {i+1}/{len(messages)}*\n\n{msg_part}"
            
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': msg_part,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                log_message(f"✅ Telegram message sent (part {i+1}/{len(messages)})")
            else:
                log_message(f"❌ Telegram error (part {i+1}): {response.status_code} - {response.text}")
                return False
            
            # Small delay between parts
            if len(messages) > 1 and i < len(messages) - 1:
                time.sleep(1)
        
        return True
        
    except Exception as e:
        log_message(f"❌ Error sending Telegram message: {e}")
        return False

def format_for_telegram(subject, body):
    """Format email content for Telegram with Markdown"""
    # Convert email format to Telegram Markdown
    telegram_msg = f"*{subject}*\n\n"
    
    # Process body line by line
    lines = body.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            telegram_msg += '\n'
            continue
        
        # Convert formatting
        if line.startswith('='):
            continue  # Skip separator lines
        elif '🔄' in line or '📊' in line or '🚀' in line or '👀' in line:
            telegram_msg += f"*{line}*\n"
        elif line.startswith('📈') or line.startswith('📊'):
            telegram_msg += f"`{line}`\n"
        elif line.startswith('   '):
            telegram_msg += f"  _{line.strip()}_\n"
        else:
            telegram_msg += f"{line}\n"
    
    return telegram_msg

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
        
        log_message(f"✅ Email sent: {subject}")
        
        # Also send to Telegram
        telegram_msg = format_for_telegram(subject, body)
        send_telegram_message(telegram_msg)
        
    except Exception as e:
        log_message(f"❌ Error sending email: {e}")

def send_test_notifications():
    """Send test email and Telegram message to show format"""
    log_message("🧪 Sending test notifications...")
    
    # Create a sample alert
    test_subject = "🌞 Market Hours Alert - Significant Changes (14:30) [🚀2NEW ⬆️1UP]"
    
    test_body = """
🌞 MARKET HOURS STOCK ALERT - SIGNIFICANT CHANGES
============================================================
2024-10-31 14:30:00 EST | Thursday
Session: Market Hours | Monitoring: 24/7

🔄 SIGNIFICANT CHANGES DETECTED
===============================
⏰ Last update: 1h 15m ago

🚀 NEW BUY SIGNALS (2): AAPL, MSFT
⬆️ PROMOTED TO BUY (1): GOOGL
📈 SCORE UPGRADES (1): NVDA (7→9)

🚀 CURRENT BUY SIGNALS (8 stocks)
===============================================

📈 AAPL 🆕 NEW! - Score: 9/10
   💰 Price: $150.25
   🎯 RSI: 65.2
   📊 20-day MA: $148.50
   
   Signals: Above 20-day MA, RSI healthy (65.2), MACD bullish

📈 MSFT 🆕 NEW! - Score: 8/10
   💰 Price: $285.75
   🎯 RSI: 58.4
   📊 20-day MA: $282.10
   
   Signals: Above 20-day MA, 20-day > 50-day MA, MACD bullish

📈 GOOGL - Score: 8/10
   💰 Price: $125.80
   🎯 RSI: 62.1
   📊 20-day MA: $124.20
   
   Signals: Above 20-day MA, RSI healthy (62.1), High volume

👀 CURRENT WATCH SIGNALS (12 stocks)
==================================================

📊 TSLA - Score: 6/10
   💰 Price: $195.50 | RSI: 45.2
   Signals: RSI healthy, MACD bullish

📊 AMD - Score: 6/10
   💰 Price: $88.25 | RSI: 52.8
   Signals: Above 20-day MA, High volume

📋 Additional WATCH signals: INTC, CRM, NFLX, DIS, BA, CAT, JPM, GS, XOM

📅 TODAY'S EARNINGS TO WATCH
============================
📅 META: Meta Platforms Inc
📅 AMZN: Amazon.com Inc
📅 PYPL: PayPal Holdings Inc

⚠️  IMPORTANT NOTES
==================
• Alert triggered by SIGNIFICANT changes only
• 24/7 monitoring: Pre-market (4AM-9:30AM), Regular (9:30AM-4PM), After-hours (4PM-8PM)
• Market Hours analysis with enhanced thresholds
• Weekend monitoring for international exposure
• Always do your own research before investing

📊 Next analysis: 15:30 EST
🔄 Monitoring status: ACTIVE 24/7 during market days

💡 Regular hours analysis with full market data and volume
"""
    
    # Send test email
    try:
        send_email(test_subject, test_body)
        log_message("✅ Test notifications sent successfully!")
        return True
    except Exception as e:
        log_message(f"❌ Error sending test notifications: {e}")
        return False

def send_morning_consolidation():
    """Send morning email consolidating all overnight actions (8 PM to 7 AM)"""
    now = datetime.now()
    
    # Only send at 7 AM on market days
    if now.hour != 7 or not is_market_day():
        return
    
    log_message("🌅 Preparing morning consolidation email...")
    
    # Load overnight actions
    actions_data = load_overnight_actions()
    overnight_actions = actions_data.get('actions', [])
    
    # Get current market state for morning
    try:
        client = EnhancedYahooClient()
        earnings = client.get_earnings_calendar(days_ahead=7)
        themes = client.get_investment_themes()
    except Exception as e:
        log_message(f"⚠️ Market data unavailable for morning email: {e}")
        earnings = None
        themes = None
    
    # Get current recommendations for morning context
    from stock_universe import get_comprehensive_stock_list
    all_stocks = get_comprehensive_stock_list()
    monitor_stocks = all_stocks[:100]  # Morning pre-market analysis
    
    buy_signals = []
    watch_signals = []
    
    for symbol in monitor_stocks:
        analysis = get_technical_score(symbol)
        if analysis:
            if analysis['score'] >= 8:  # Pre-market threshold
                buy_signals.append(analysis)
            elif analysis['score'] >= 6:
                watch_signals.append(analysis)
    
    buy_signals.sort(key=lambda x: x['score'], reverse=True)
    watch_signals.sort(key=lambda x: x['score'], reverse=True)
    
    subject = f"🌅 Morning Market Brief - Overnight Summary ({now.strftime('%Y-%m-%d')})"
    
    # Add overnight activity indicator to subject
    if overnight_actions:
        subject += f" | {len(overnight_actions)} Overnight Events"
    
    body = f"""
🌅 MORNING MARKET BRIEF - OVERNIGHT CONSOLIDATION
================================================
{now.strftime('%Y-%m-%d %H:%M:%S')} EST | {now.strftime('%A')}

🌙 OVERNIGHT ACTIVITY SUMMARY (8 PM - 7 AM)
===========================================
"""
    
    if overnight_actions:
        body += f"📊 Total overnight events: {len(overnight_actions)}\n\n"
        
        # Group actions by type
        significant_changes = [a for a in overnight_actions if a['type'] == 'significant_changes']
        
        if significant_changes:
            body += "🚨 SIGNIFICANT CHANGES OVERNIGHT:\n"
            body += "================================\n"
            
            for action in significant_changes:
                action_time = datetime.fromisoformat(action['timestamp'])
                details = action['details']
                
                body += f"⏰ {action_time.strftime('%H:%M')} ({action['session']}):\n"
                body += f"   📊 {details['changes']}\n"
                
                if details.get('new_buy'):
                    body += f"   🚀 New BUY: {', '.join(details['new_buy'])}\n"
                if details.get('removed_buy'):
                    body += f"   ❌ Removed BUY: {', '.join(details['removed_buy'])}\n"
                if details.get('promotions'):
                    body += f"   ⬆️ Promoted: {', '.join(details['promotions'])}\n"
                if details.get('demotions'):
                    body += f"   ⬇️ Demoted: {', '.join(details['demotions'])}\n"
                body += "\n"
        
        # Summary of overnight impact
        all_new_buy = set()
        all_removed_buy = set()
        all_promotions = set()
        all_demotions = set()
        
        for action in significant_changes:
            details = action['details']
            all_new_buy.update(details.get('new_buy', []))
            all_removed_buy.update(details.get('removed_buy', []))
            all_promotions.update(details.get('promotions', []))
            all_demotions.update(details.get('demotions', []))
        
        if any([all_new_buy, all_removed_buy, all_promotions, all_demotions]):
            body += "📋 OVERNIGHT NET CHANGES:\n"
            body += "========================\n"
            if all_new_buy:
                body += f"🚀 Net New BUY Signals: {', '.join(all_new_buy)}\n"
            if all_removed_buy:
                body += f"❌ Net Removed BUY Signals: {', '.join(all_removed_buy)}\n"
            if all_promotions:
                body += f"⬆️ Net Promotions to BUY: {', '.join(all_promotions)}\n"
            if all_demotions:
                body += f"⬇️ Net Demotions to WATCH: {', '.join(all_demotions)}\n"
            body += "\n"
    else:
        body += "💤 No significant changes detected overnight\n"
        body += "   System monitored after-hours session (4 PM - 8 PM)\n"
        body += "   Overnight period (8 PM - 7 AM) was quiet\n\n"
    
    body += f"""
🌅 CURRENT PRE-MARKET STATUS (7:00 AM)
=====================================
🚀 BUY Signals: {len(buy_signals)} stocks (Score ≥8)
👀 WATCH Signals: {len(watch_signals)} stocks (Score ≥6)

🚀 TOP PRE-MARKET BUY SIGNALS
============================
"""
    
    for i, signal in enumerate(buy_signals[:5], 1):
        body += f"""
{i}. 📈 {signal['symbol']} - Score: {signal['score']}/10
   💰 Price: ${signal['current_price']:.2f} | RSI: {signal['rsi']:.1f}
   🎯 Signals: {', '.join(signal['signals'][:2])}
"""
    
    if len(buy_signals) > 5:
        remaining = [f"{s['symbol']}({s['score']})" for s in buy_signals[5:]]
        body += f"\n📋 Additional BUY signals: {', '.join(remaining)}\n"
    
    # Add earnings for today
    if earnings:
        body += f"""

📅 TODAY'S EARNINGS CALENDAR
===========================
"""
        today = now.strftime('%Y-%m-%d')
        todays_earnings = [e for e in earnings if e.get('date') == today] if earnings else []
        
        if todays_earnings:
            for earning in todays_earnings[:8]:
                body += f"📅 {earning.get('symbol', 'N/A')}: {earning.get('company', 'N/A')}\n"
        else:
            body += "No major earnings scheduled for today\n"
    
    # Add themes if available
    if themes and themes.get('themes'):
        body += f"""

🔥 HOT INVESTMENT THEMES
=======================
"""
        for theme in themes['themes'][:3]:
            body += f"🔥 {theme['theme']}: {theme['avg_change_percent']:+.2f}%\n"
    
    body += f"""

📊 TODAY'S TRADING PLAN
======================
• Pre-market monitoring: 4:00 AM - 9:30 AM EST
• Regular hours analysis: 9:30 AM - 4:00 PM EST  
• After-hours tracking: 4:00 PM - 8:00 PM EST
• Email alerts ONLY for significant changes
• Next consolidation: Tomorrow 7:00 AM EST

🎯 FOCUS AREAS FOR TODAY
=======================
• Monitor pre-market gaps and volume
• Watch for earnings reactions
• Track theme momentum
• Look for breakout confirmations at market open

Good luck with today's trading! 🚀
"""
    
    send_email(subject, body)
    
    # Reset overnight actions after sending morning email
    reset_overnight_actions()

def main():
    """Main 24/7 scheduler function"""
    print("🚀 Starting 24/7 Enhanced Market Alert System")
    print("=" * 60)
    
    # Schedule 24/7 hourly analysis
    schedule.every().hour.do(analyze_market_24x7)
    
    # Schedule morning consolidation email (7:00 AM)
    schedule.every().day.at("07:00").do(send_morning_consolidation)
    
    # Schedule daily summary at market close
    schedule.every().day.at("16:05").do(send_daily_summary)
    
    # Schedule weekend summary (Saturday 8 AM)
    schedule.every().saturday.at("08:00").do(send_weekend_summary)
    
    print("📅 24/7 MONITORING SCHEDULE:")
    print("=" * 40)
    print("🌅 Pre-Market:    4:00 AM - 9:30 AM EST (Hourly)")
    print("🌞 Regular Hours: 9:30 AM - 4:00 PM EST (Hourly)")
    print("🌙 After-Hours:   4:00 PM - 8:00 PM EST (Hourly)")
    print("💤 Overnight:     8:00 PM - 4:00 AM EST (Paused)")
    print("🌍 Weekends:      Limited international monitoring")
    print("📧 Morning Brief: 7:00 AM EST (Overnight consolidation)")
    print()
    print("📧 SMART EMAIL ALERTS:")
    print("=" * 25)
    print("✅ ONLY significant changes trigger emails")
    print("✅ New/removed BUY signals (always sent)")
    print("✅ Score changes ≥2 points")
    print("✅ Promotions/demotions between BUY/WATCH")
    print("✅ Multiple WATCH changes (≥3 stocks)")
    print("✅ Session-aware thresholds")
    print("✅ Morning consolidation (overnight summary)")
    print()
    print("🎯 COMPREHENSIVE ANALYSIS COVERAGE:")
    print("=" * 35)
    print("📊 Regular Hours: 600+ stocks - FULL UNIVERSE (BUY≥7, WATCH≥5)")
    print("   🇺🇸 300+ US NASDAQ/NYSE stocks")
    print("   🇨🇦 300+ Canadian TSX stocks")
    print("🌅 Pre/After Hours: 400 stocks (BUY≥8, WATCH≥6)")
    print("🌍 Weekends: 200 international stocks (BUY≥8, WATCH≥6)")
    print()
    print(f"📧 Email alerts to: {EMAIL_TO}")
    print("🔄 System Status: ACTIVE 24/7")
    print()
    
    # Run initial analysis to establish baseline
    current_session = get_market_session()
    print(f"🚀 Current session: {current_session}")
    
    if should_run_analysis():
        print("🚀 Running initial analysis to establish baseline...")
        analyze_market_24x7()
    else:
        print("⏰ Outside monitoring hours - system will activate automatically")
    
    print("\n🔄 System running... Press Ctrl+C to stop")
    print("📊 Next scheduled analysis: Top of next hour")
    
    # Initialize log file
    log_message("🚀 24/7 Enhanced Market Alert System started")
    log_message(f"📧 Email alerts configured for: {EMAIL_TO}")
    log_message(f"📊 Log file: {LOG_FILE}")
    
    while True:
        schedule.run_pending()
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopping alert system...")
        print("System stopped successfully!")