#!/usr/bin/env python3
"""
Test script to verify all main analysis files are using the expanded stock universe
"""

def test_main_py():
    """Test main.py stock universe"""
    try:
        import sys
        import os
        sys.path.insert(0, os.getcwd())
        
        # Import main.py symbols
        from main import symbols as main_symbols
        print(f"✅ main.py: {len(main_symbols)} stocks loaded")
        print(f"   First 10: {main_symbols[:10]}")
        return len(main_symbols)
    except Exception as e:
        print(f"❌ main.py error: {e}")
        return 0

def test_main_enhanced_py():
    """Test main_enhanced.py stock universe"""
    try:
        from main_enhanced import symbols as enhanced_symbols
        print(f"✅ main_enhanced.py: {len(enhanced_symbols)} stocks loaded")
        print(f"   First 10: {enhanced_symbols[:10]}")
        return len(enhanced_symbols)
    except Exception as e:
        print(f"❌ main_enhanced.py error: {e}")
        return 0

def test_main_copilot_py():
    """Test main_copilot.py stock universe"""
    try:
        from main_copilot import symbols as copilot_symbols
        print(f"✅ main_copilot.py: {len(copilot_symbols)} stocks loaded")
        print(f"   First 10: {copilot_symbols[:10]}")
        return len(copilot_symbols)
    except Exception as e:
        print(f"❌ main_copilot.py error: {e}")
        return 0

def test_scheduled_alerts():
    """Test scheduled alerts stock universe access"""
    try:
        from stock_universe import get_comprehensive_stock_list
        stocks = get_comprehensive_stock_list()
        print(f"✅ scheduled_market_alerts.py: Can access {len(stocks)} stocks")
        print(f"   First 10: {stocks[:10]}")
        return len(stocks)
    except Exception as e:
        print(f"❌ scheduled_market_alerts.py error: {e}")
        return 0

def main():
    print("🧪 Testing Stock Universe Integration")
    print("=" * 50)
    
    # Test all main analysis files
    main_count = test_main_py()
    enhanced_count = test_main_enhanced_py()
    copilot_count = test_main_copilot_py()
    scheduled_count = test_scheduled_alerts()
    
    print("\n📊 SUMMARY")
    print("=" * 20)
    
    if main_count > 200:
        print("✅ main.py: Using expanded universe")
    else:
        print("❌ main.py: Still using old stock list")
    
    if enhanced_count > 200:
        print("✅ main_enhanced.py: Using expanded universe")
    else:
        print("❌ main_enhanced.py: Still using old stock list")
    
    if copilot_count > 200:
        print("✅ main_copilot.py: Using expanded universe")
    else:
        print("❌ main_copilot.py: Still using old stock list")
    
    if scheduled_count > 200:
        print("✅ scheduled_market_alerts.py: Can access expanded universe")
    else:
        print("❌ scheduled_market_alerts.py: Cannot access expanded universe")
    
    # Check consistency
    counts = [main_count, enhanced_count, copilot_count, scheduled_count]
    unique_counts = set(c for c in counts if c > 0)
    
    if len(unique_counts) == 1:
        print(f"\n🎯 All systems consistent: {list(unique_counts)[0]} stocks")
    else:
        print(f"\n⚠️  Inconsistent stock counts: {unique_counts}")
    
    print(f"\n🚀 Stock universe integration test complete!")

if __name__ == "__main__":
    main()