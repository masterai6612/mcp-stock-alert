#!/usr/bin/env python3
"""
Test script to show email and Telegram format without sending actual notifications
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_email_format():
    """Show how the email will look"""
    print("📧 EMAIL FORMAT PREVIEW")
    print("=" * 50)
    
    # Sample email content
    subject = "🌞 Market Hours Alert - Significant Changes (14:30) [🚀2NEW ⬆️1UP]"
    
    body = """
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
    
    print(f"SUBJECT: {subject}")
    print("\nBODY:")
    print(body)
    
    return subject, body

def show_telegram_format(subject, body):
    """Show how the Telegram message will look"""
    print("\n" + "=" * 50)
    print("📱 TELEGRAM FORMAT PREVIEW")
    print("=" * 50)
    
    # Convert to Telegram format
    telegram_msg = f"*{subject}*\n\n"
    
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
    
    print("TELEGRAM MESSAGE:")
    print(telegram_msg)
    
    # Check message length
    print(f"\nMessage length: {len(telegram_msg)} characters")
    if len(telegram_msg) > 4000:
        print("⚠️  Message will be split into multiple parts (Telegram 4096 char limit)")
    else:
        print("✅ Message fits in single Telegram message")
    
    return telegram_msg

def show_morning_consolidation_format():
    """Show morning consolidation email format"""
    print("\n" + "=" * 50)
    print("🌅 MORNING CONSOLIDATION EMAIL PREVIEW")
    print("=" * 50)
    
    subject = "🌅 Morning Market Brief - Overnight Summary (2024-10-31) | 3 Overnight Events"
    
    body = """
🌅 MORNING MARKET BRIEF - OVERNIGHT CONSOLIDATION
================================================
2024-10-31 07:00:00 EST | Thursday

🌙 OVERNIGHT ACTIVITY SUMMARY (8 PM - 7 AM)
===========================================
📊 Total overnight events: 3

🚨 SIGNIFICANT CHANGES OVERNIGHT:
================================
⏰ 21:15 (AFTER_HOURS):
   📊 +2 BUY, -1 BUY, 1 promotion
   🚀 New BUY: AAPL, MSFT
   ❌ Removed BUY: TSLA
   ⬆️ Promoted: GOOGL

⏰ 23:30 (CLOSED):
   📊 +1 BUY, 2 upgrades
   🚀 New BUY: NVDA
   📈 Score upgrades: AMD (6→8), INTC (5→7)

⏰ 05:45 (PRE_MARKET):
   📊 -1 BUY, +2 WATCH
   ❌ Removed BUY: META
   👀 New WATCH: CRM, NFLX

📋 OVERNIGHT NET CHANGES:
========================
🚀 Net New BUY Signals: AAPL, MSFT, GOOGL, NVDA
❌ Net Removed BUY Signals: TSLA, META
⬆️ Net Promotions to BUY: GOOGL

🌅 CURRENT PRE-MARKET STATUS (7:00 AM)
=====================================
🚀 BUY Signals: 8 stocks (Score ≥8)
👀 WATCH Signals: 15 stocks (Score ≥6)

🚀 TOP PRE-MARKET BUY SIGNALS
============================

1. 📈 AAPL - Score: 9/10
   💰 Price: $150.25 | RSI: 65.2
   🎯 Signals: Above 20-day MA, MACD bullish

2. 📈 MSFT - Score: 8/10
   💰 Price: $285.75 | RSI: 58.4
   🎯 Signals: Above 20-day MA, RSI healthy

3. 📈 GOOGL - Score: 8/10
   💰 Price: $125.80 | RSI: 62.1
   🎯 Signals: RSI healthy, High volume

📅 TODAY'S EARNINGS CALENDAR
===========================
📅 AMZN: Amazon.com Inc
📅 META: Meta Platforms Inc
📅 PYPL: PayPal Holdings Inc

🔥 HOT INVESTMENT THEMES
=======================
🔥 Artificial Intelligence: +2.5%
🔥 Cloud Computing: +1.8%
🔥 Electric Vehicles: -0.3%

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
    
    print(f"SUBJECT: {subject}")
    print("\nBODY:")
    print(body)

def check_telegram_config():
    """Check Telegram configuration"""
    print("\n" + "=" * 50)
    print("🔧 TELEGRAM CONFIGURATION CHECK")
    print("=" * 50)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token:
        # Mask the token for security
        masked_token = bot_token[:10] + "..." + bot_token[-10:] if len(bot_token) > 20 else "***"
        print(f"✅ Bot Token: {masked_token}")
    else:
        print("❌ Bot Token: Not configured")
    
    if chat_id:
        print(f"✅ Chat ID: {chat_id}")
    else:
        print("❌ Chat ID: Not configured")
    
    if bot_token and chat_id:
        print("\n✅ Telegram configuration is complete!")
        print("📱 Messages will be sent to both email and Telegram")
    else:
        print("\n⚠️  Telegram configuration incomplete")
        print("📧 Only email notifications will be sent")

def test_actual_notifications():
    """Test sending actual notifications"""
    print("\n" + "=" * 50)
    print("🧪 ACTUAL NOTIFICATION TEST")
    print("=" * 50)
    
    response = input("Send actual test notifications to email and Telegram? (y/N): ")
    if response.lower() != 'y':
        print("Skipped actual notification test")
        return
    
    try:
        from scheduled_market_alerts import send_test_notifications
        print("🚀 Sending test notifications...")
        success = send_test_notifications()
        
        if success:
            print("✅ Test notifications sent successfully!")
            print("📧 Check your email: masterai6612@gmail.com")
            print("📱 Check your Telegram chat")
        else:
            print("❌ Failed to send test notifications")
            
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")

if __name__ == "__main__":
    print("📧 EMAIL & TELEGRAM FORMAT PREVIEW")
    print("=" * 60)
    
    # Show email format
    subject, body = show_email_format()
    
    # Show Telegram format
    show_telegram_format(subject, body)
    
    # Show morning consolidation format
    show_morning_consolidation_format()
    
    # Check Telegram configuration
    check_telegram_config()
    
    # Offer to send actual test
    test_actual_notifications()
    
    print("\n🎉 Format Preview Complete!")
    print("\n📋 Summary:")
    print("   ✅ Email format: Professional, detailed analysis")
    print("   ✅ Telegram format: Markdown formatted, mobile-friendly")
    print("   ✅ Morning consolidation: Complete overnight summary")
    print("   ✅ Dual notifications: Email + Telegram")
    print("   ✅ No webhook secrets exposed")
    
    print("\n🚀 The system will send notifications to:")
    print("   📧 Email: masterai6612@gmail.com")
    print("   📱 Telegram: Chat ID 7208554751")
    print("   🔄 Both channels get the same information")
    print("   📊 Messages automatically formatted for each platform")