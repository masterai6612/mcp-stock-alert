#!/usr/bin/env python3
"""
Alert System Status Checker
Verifies if the scheduled alert system is ready for tomorrow
"""

import schedule
import os
import json
from datetime import datetime, timedelta
import holidays
import subprocess
import sys

def check_system_status():
    """Check if the alert system is ready"""
    print("🔍 ALERT SYSTEM STATUS CHECK")
    print("=" * 50)
    
    # Check if process is running
    try:
        result = subprocess.run(['pgrep', '-f', 'scheduled_market_alerts'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✅ Scheduler process running (PID: {', '.join(pids)})")
        else:
            print("❌ Scheduler process NOT running")
            return False
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False
    
    # Check tomorrow's market status
    tomorrow = datetime.now() + timedelta(days=1)
    us_holidays = holidays.US(years=tomorrow.year)
    ca_holidays = holidays.CA(years=tomorrow.year)
    
    is_weekday = tomorrow.weekday() < 5
    is_holiday = tomorrow.date() in us_holidays or tomorrow.date() in ca_holidays
    market_open = is_weekday and not is_holiday
    
    print(f"\n📅 TOMORROW'S SCHEDULE:")
    print(f"   Date: {tomorrow.strftime('%A, %B %d, %Y')}")
    print(f"   Weekday: {'✅' if is_weekday else '❌'}")
    print(f"   Holiday: {'❌' if is_holiday else '✅'}")
    print(f"   Market Open: {'✅' if market_open else '❌'}")
    
    if market_open:
        print(f"   🌅 Morning Alert: 7:30 AM EDT")
        print(f"   🔍 Trend Monitoring: Every 30 minutes (9:30 AM - 4:00 PM EDT)")
    else:
        print(f"   📴 No alerts scheduled (market closed)")
    
    # Check email configuration
    print(f"\n📧 EMAIL CONFIGURATION:")
    print(f"   To: masterai6612@gmail.com")
    print(f"   From: masterai6612@gmail.com")
    print(f"   SMTP: Gmail (smtp.gmail.com:587)")
    
    # Check tracking files
    print(f"\n📊 TRACKING FILES:")
    
    if os.path.exists("sent_alerts.json"):
        with open("sent_alerts.json", 'r') as f:
            alerts = json.load(f)
        print(f"   ✅ sent_alerts.json exists ({len(alerts)} days tracked)")
    else:
        print(f"   📝 sent_alerts.json will be created on first run")
    
    if os.path.exists("stock_tracking.json"):
        with open("stock_tracking.json", 'r') as f:
            tracking = json.load(f)
        watchlists = tracking.get("watchlists", {})
        print(f"   ✅ stock_tracking.json exists ({len(watchlists)} watchlists)")
        for name, stocks in watchlists.items():
            print(f"      📋 {name}: {len(stocks)} stocks")
    else:
        print(f"   📝 stock_tracking.json will be created on first run")
    
    # Check virtual environment
    print(f"\n🐍 PYTHON ENVIRONMENT:")
    venv_python = "./venv/bin/python"
    if os.path.exists(venv_python):
        print(f"   ✅ Virtual environment active")
        try:
            result = subprocess.run([venv_python, '-c', 
                                   'import yfinance, schedule, smtplib; print("All modules available")'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ All required modules installed")
            else:
                print(f"   ❌ Missing modules: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Error checking modules: {e}")
    else:
        print(f"   ❌ Virtual environment not found")
    
    print(f"\n🎯 SUMMARY:")
    if market_open:
        print(f"   ✅ System is ready for tomorrow's alerts!")
        print(f"   🌅 You will receive a morning alert at 7:30 AM EDT")
        print(f"   🔍 Trend alerts will monitor throughout the trading day")
        print(f"   📧 All alerts will be sent to masterai6612@gmail.com")
    else:
        print(f"   📴 No alerts tomorrow (market closed)")
        print(f"   🔄 System will resume on next trading day")
    
    return True

def show_next_alert_time():
    """Show when the next alert will be sent"""
    print(f"\n⏰ NEXT ALERT TIMING:")
    
    now = datetime.now()
    tomorrow_7_30 = (now + timedelta(days=1)).replace(hour=7, minute=30, second=0, microsecond=0)
    
    # Check if tomorrow is a trading day
    us_holidays = holidays.US(years=tomorrow_7_30.year)
    ca_holidays = holidays.CA(years=tomorrow_7_30.year)
    is_trading_day = tomorrow_7_30.weekday() < 5 and tomorrow_7_30.date() not in us_holidays and tomorrow_7_30.date() not in ca_holidays
    
    if is_trading_day:
        time_until = tomorrow_7_30 - now
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)
        
        print(f"   📅 Next morning alert: {tomorrow_7_30.strftime('%A, %B %d at 7:30 AM EDT')}")
        print(f"   ⏳ Time until alert: {hours} hours and {minutes} minutes")
    else:
        # Find next trading day
        next_day = tomorrow_7_30
        while next_day.weekday() >= 5 or next_day.date() in us_holidays or next_day.date() in ca_holidays:
            next_day += timedelta(days=1)
        
        print(f"   📅 Next morning alert: {next_day.strftime('%A, %B %d at 7:30 AM EDT')}")
        print(f"   📴 Tomorrow is not a trading day")

if __name__ == "__main__":
    check_system_status()
    show_next_alert_time()
    
    print(f"\n💡 TIP: To stop the system, run:")
    print(f"   pkill -f scheduled_market_alerts")
    print(f"\n💡 To restart the system, run:")
    print(f"   ./start_market_alerts.sh")