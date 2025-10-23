#!/usr/bin/env python3
"""
Utility script to clear alert history.
Run this if you want to reset the duplicate alert prevention system.
"""

import os
import json
from main_copilot import ALERT_HISTORY_FILE

def clear_alert_history():
    """Clear the alert history file"""
    if os.path.exists(ALERT_HISTORY_FILE):
        os.remove(ALERT_HISTORY_FILE)
        print(f"Alert history cleared: {ALERT_HISTORY_FILE}")
    else:
        print("No alert history file found")

def show_alert_history():
    """Show current alert history"""
    if os.path.exists(ALERT_HISTORY_FILE):
        try:
            with open(ALERT_HISTORY_FILE, 'r') as f:
                history = json.load(f)
            print("Current alert history:")
            for date, alerts in history.items():
                print(f"  {date}: {len(alerts)} alerts")
                for alert in alerts:
                    print(f"    - {alert}")
        except Exception as e:
            print(f"Error reading alert history: {e}")
    else:
        print("No alert history file found")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_alert_history()
    elif len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_alert_history()
    else:
        print("Usage:")
        print("  python clear_alert_history.py show   - Show current alert history")
        print("  python clear_alert_history.py clear  - Clear alert history")