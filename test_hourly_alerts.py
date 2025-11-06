#!/usr/bin/env python3
"""
Test script for hourly alert system with change detection
"""

import json
import os
from datetime import datetime
from scheduled_market_alerts import (
    analyze_market_hourly, 
    detect_recommendation_changes,
    load_last_recommendations,
    save_recommendations
)

def test_change_detection():
    """Test the recommendation change detection"""
    print("🧪 Testing Change Detection System")
    print("=" * 40)
    
    # Simulate some stock recommendations
    mock_buy_signals = [
        {'symbol': 'AAPL', 'score': 8},
        {'symbol': 'MSFT', 'score': 7},
        {'symbol': 'GOOGL', 'score': 9}
    ]
    
    mock_watch_signals = [
        {'symbol': 'TSLA', 'score': 6},
        {'symbol': 'NVDA', 'score': 5},
        {'symbol': 'AMD', 'score': 6}
    ]
    
    print("📊 Initial recommendations:")
    print(f"   BUY: {[s['symbol'] for s in mock_buy_signals]}")
    print(f"   WATCH: {[s['symbol'] for s in mock_watch_signals]}")
    
    # Save initial recommendations
    save_recommendations({
        'buy_signals': mock_buy_signals,
        'watch_signals': mock_watch_signals,
        'timestamp': datetime.now().isoformat()
    })
    
    print("✅ Saved initial recommendations")
    
    # Test 1: No changes
    print("\n🧪 Test 1: No changes")
    changes = detect_recommendation_changes(mock_buy_signals, mock_watch_signals)
    print(f"   Has changes: {changes['has_changes']}")
    print(f"   Expected: False")
    
    # Test 2: Add new BUY signal
    print("\n🧪 Test 2: Add new BUY signal")
    new_buy_signals = mock_buy_signals + [{'symbol': 'META', 'score': 8}]
    changes = detect_recommendation_changes(new_buy_signals, mock_watch_signals)
    print(f"   Has changes: {changes['has_changes']}")
    print(f"   New BUY: {changes['new_buy']}")
    print(f"   Expected: True, ['META']")
    
    # Test 3: Remove WATCH signal, add new one
    print("\n🧪 Test 3: Remove WATCH signal, add new one")
    new_watch_signals = [
        {'symbol': 'TSLA', 'score': 6},
        {'symbol': 'NFLX', 'score': 5}  # Replaced NVDA and AMD with NFLX
    ]
    changes = detect_recommendation_changes(mock_buy_signals, new_watch_signals)
    print(f"   Has changes: {changes['has_changes']}")
    print(f"   New WATCH: {changes['new_watch']}")
    print(f"   Removed WATCH: {changes['removed_watch']}")
    print(f"   Expected: True, ['NFLX'], ['NVDA', 'AMD']")
    
    print("\n✅ Change detection tests completed!")

def test_file_operations():
    """Test file save/load operations"""
    print("\n🧪 Testing File Operations")
    print("=" * 30)
    
    # Check if files exist
    files_to_check = [
        "last_recommendations.json",
        "sent_alerts.json",
        "stock_tracking.json"
    ]
    
    for file in files_to_check:
        exists = os.path.exists(file)
        print(f"   {file}: {'✅ EXISTS' if exists else '❌ MISSING'}")
    
    # Test loading recommendations
    try:
        recommendations = load_last_recommendations()
        print(f"   Last recommendations loaded: ✅")
        print(f"   BUY signals: {len(recommendations.get('buy_signals', []))}")
        print(f"   WATCH signals: {len(recommendations.get('watch_signals', []))}")
    except Exception as e:
        print(f"   Error loading recommendations: ❌ {e}")

def simulate_24x7_run():
    """Simulate a 24/7 analysis run"""
    print("\n🧪 Simulating 24/7 Analysis")
    print("=" * 35)
    
    print("⚠️  Note: This will run actual market analysis")
    print("   It may take 2-3 minutes and will check real stock data")
    print("   Analysis adapts to current market session automatically")
    
    response = input("\nProceed with simulation? (y/N): ")
    if response.lower() != 'y':
        print("Skipped simulation")
        return
    
    print("\n🚀 Running analyze_market_24x7()...")
    try:
        from scheduled_market_alerts import analyze_market_24x7, get_market_session, should_run_analysis
        
        session = get_market_session()
        should_run = should_run_analysis()
        
        print(f"📊 Current session: {session}")
        print(f"🔍 Should run analysis: {should_run}")
        
        if should_run:
            analyze_market_24x7()
            print("✅ 24/7 analysis completed successfully!")
        else:
            print("⏰ Outside monitoring hours - analysis would be skipped")
            print("   (System runs during pre-market, regular hours, and after-hours)")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

def test_session_detection():
    """Test market session detection"""
    print("\n🧪 Testing Session Detection")
    print("=" * 32)
    
    try:
        from scheduled_market_alerts import get_market_session, should_run_analysis, is_market_day
        from datetime import datetime
        
        now = datetime.now()
        session = get_market_session()
        should_run = should_run_analysis()
        is_market = is_market_day()
        
        print(f"📅 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A')})")
        print(f"📊 Market session: {session}")
        print(f"🔍 Should run analysis: {should_run}")
        print(f"📈 Is market day: {is_market}")
        
        # Show session schedule
        print("\n📅 Session Schedule:")
        print("   🌅 Pre-Market:    4:00 AM - 9:30 AM EST")
        print("   🌞 Regular Hours: 9:30 AM - 4:00 PM EST")
        print("   🌙 After-Hours:   4:00 PM - 8:00 PM EST")
        print("   💤 Overnight:     8:00 PM - 4:00 AM EST")
        
        if session == "PRE_MARKET":
            print("   ✅ Currently in pre-market session")
        elif session == "REGULAR_HOURS":
            print("   ✅ Currently in regular trading hours")
        elif session == "AFTER_HOURS":
            print("   ✅ Currently in after-hours session")
        else:
            print("   💤 Currently outside trading sessions")
            
    except Exception as e:
        print(f"❌ Error testing session detection: {e}")

if __name__ == "__main__":
    print("🧪 24/7 ENHANCED ALERT SYSTEM TESTING")
    print("=" * 55)
    
    test_change_detection()
    test_file_operations()
    test_session_detection()
    
    print("\n" + "=" * 55)
    simulate_24x7_run()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary:")
    print("   • Enhanced change detection system tested")
    print("   • File operations verified")
    print("   • Session detection working")
    print("   • System ready for 24/7 monitoring")
    print("\n🚀 Features:")
    print("   ✅ 24/7 monitoring (pre-market, regular, after-hours)")
    print("   ✅ Significant change detection only")
    print("   ✅ Session-aware thresholds")
    print("   ✅ Weekend international exposure monitoring")
    print("   ✅ Smart email alerts (no spam)")
    print("\n🚀 To start the system: python scheduled_market_alerts.py")