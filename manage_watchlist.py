#!/usr/bin/env python3
"""
Watchlist Management Tool
Add or remove stocks from watchlists to test change detection
"""

import sys
from stock_change_tracker import track_watchlist_changes, tracker

def show_current_watchlists():
    """Display current watchlists"""
    print("📊 CURRENT WATCHLISTS")
    print("=" * 50)
    
    if not tracker.data["watchlists"]:
        print("No watchlists found.")
        return
    
    for name, stocks in tracker.data["watchlists"].items():
        print(f"\n📋 {name.upper()}:")
        print(f"   Stocks: {', '.join(stocks)}")
        print(f"   Count: {len(stocks)}")

def show_recent_changes():
    """Display recent changes"""
    print("\n🔄 RECENT CHANGES (Last 24 Hours)")
    print("=" * 50)
    
    recent_changes = tracker.get_recent_changes(24)
    
    if not recent_changes:
        print("No recent changes.")
        return
    
    for change in recent_changes:
        print(f"\n⏰ {change['timestamp']}")
        print(f"📋 Watchlist: {change['watchlist']}")
        if change['added']:
            print(f"🆕 Added: {', '.join(change['added'])}")
        if change['removed']:
            print(f"❌ Removed: {', '.join(change['removed'])}")

def add_stocks_to_watchlist(watchlist_name: str, stocks_to_add: list):
    """Add stocks to a watchlist"""
    current_stocks = tracker.data["watchlists"].get(watchlist_name, [])
    updated_stocks = list(set(current_stocks + stocks_to_add))  # Remove duplicates
    
    changes = track_watchlist_changes(watchlist_name, updated_stocks)
    
    print(f"\n✅ Updated watchlist '{watchlist_name}'")
    if changes['added']:
        print(f"🆕 Added: {', '.join(changes['added'])}")
    if changes['removed']:
        print(f"❌ Removed: {', '.join(changes['removed'])}")
    print(f"📊 Total stocks: {len(updated_stocks)}")

def remove_stocks_from_watchlist(watchlist_name: str, stocks_to_remove: list):
    """Remove stocks from a watchlist"""
    current_stocks = tracker.data["watchlists"].get(watchlist_name, [])
    updated_stocks = [stock for stock in current_stocks if stock not in stocks_to_remove]
    
    changes = track_watchlist_changes(watchlist_name, updated_stocks)
    
    print(f"\n✅ Updated watchlist '{watchlist_name}'")
    if changes['added']:
        print(f"🆕 Added: {', '.join(changes['added'])}")
    if changes['removed']:
        print(f"❌ Removed: {', '.join(changes['removed'])}")
    print(f"📊 Total stocks: {len(updated_stocks)}")

def create_test_scenario():
    """Create a test scenario with stock changes"""
    print("🧪 CREATING TEST SCENARIO")
    print("=" * 50)
    
    # Add some new hot stocks to test
    new_hot_stocks = ["PLTR", "SNOW", "CRWD", "ZS", "OKTA"]
    add_stocks_to_watchlist("test_watchlist", new_hot_stocks)
    
    # Add some to morning watchlist
    morning_additions = ["CRSP", "UBER", "ANF"]
    add_stocks_to_watchlist("morning_watchlist", morning_additions)
    
    print("\n🎯 Test scenario created! Run the email test to see highlighted changes.")

def main():
    if len(sys.argv) < 2:
        print("📊 WATCHLIST MANAGEMENT TOOL")
        print("=" * 50)
        print("Usage:")
        print("  python manage_watchlist.py show              - Show current watchlists")
        print("  python manage_watchlist.py changes           - Show recent changes")
        print("  python manage_watchlist.py add <watchlist> <stocks>    - Add stocks")
        print("  python manage_watchlist.py remove <watchlist> <stocks> - Remove stocks")
        print("  python manage_watchlist.py test              - Create test scenario")
        print()
        print("Examples:")
        print("  python manage_watchlist.py add morning_watchlist PLTR,SNOW,CRWD")
        print("  python manage_watchlist.py remove test_watchlist AAPL,MSFT")
        return
    
    command = sys.argv[1].lower()
    
    if command == "show":
        show_current_watchlists()
        show_recent_changes()
    
    elif command == "changes":
        show_recent_changes()
    
    elif command == "add":
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_watchlist.py add <watchlist> <stocks>")
            print("   Example: python manage_watchlist.py add morning_watchlist PLTR,SNOW")
            return
        
        watchlist_name = sys.argv[2]
        stocks = [stock.strip().upper() for stock in sys.argv[3].split(',')]
        add_stocks_to_watchlist(watchlist_name, stocks)
    
    elif command == "remove":
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_watchlist.py remove <watchlist> <stocks>")
            print("   Example: python manage_watchlist.py remove morning_watchlist AAPL,MSFT")
            return
        
        watchlist_name = sys.argv[2]
        stocks = [stock.strip().upper() for stock in sys.argv[3].split(',')]
        remove_stocks_from_watchlist(watchlist_name, stocks)
    
    elif command == "test":
        create_test_scenario()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()