#!/usr/bin/env python3
"""
Stock Change Tracker
Monitors changes in stock watchlists and highlights newly added stocks
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple

class StockChangeTracker:
    def __init__(self, tracking_file="stock_tracking.json"):
        self.tracking_file = tracking_file
        self.data = self.load_tracking_data()
    
    def load_tracking_data(self) -> Dict:
        """Load tracking data from file"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading tracking data: {e}")
        
        return {
            "watchlists": {},
            "last_updated": None,
            "change_history": []
        }
    
    def save_tracking_data(self):
        """Save tracking data to file"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving tracking data: {e}")
    
    def update_watchlist(self, watchlist_name: str, current_stocks: List[str]) -> Dict:
        """
        Update watchlist and detect changes
        Returns dict with added, removed, and unchanged stocks
        """
        current_set = set(current_stocks)
        previous_set = set(self.data["watchlists"].get(watchlist_name, []))
        
        # Detect changes
        added = current_set - previous_set
        removed = previous_set - current_set
        unchanged = current_set & previous_set
        
        # Update tracking data
        self.data["watchlists"][watchlist_name] = current_stocks
        self.data["last_updated"] = datetime.now().isoformat()
        
        # Record change history
        if added or removed:
            change_record = {
                "timestamp": datetime.now().isoformat(),
                "watchlist": watchlist_name,
                "added": list(added),
                "removed": list(removed)
            }
            self.data["change_history"].append(change_record)
            
            # Keep only last 100 changes
            self.data["change_history"] = self.data["change_history"][-100:]
        
        self.save_tracking_data()
        
        return {
            "added": list(added),
            "removed": list(removed),
            "unchanged": list(unchanged),
            "has_changes": bool(added or removed)
        }
    
    def get_recent_changes(self, hours: int = 24) -> List[Dict]:
        """Get changes within the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_changes = []
        for change in self.data["change_history"]:
            change_time = datetime.fromisoformat(change["timestamp"])
            if change_time >= cutoff_time:
                recent_changes.append(change)
        
        return recent_changes
    
    def get_newly_added_stocks(self, watchlist_name: str, hours: int = 24) -> List[str]:
        """Get stocks added to watchlist in the last N hours"""
        recent_changes = self.get_recent_changes(hours)
        newly_added = []
        
        for change in recent_changes:
            if change["watchlist"] == watchlist_name:
                newly_added.extend(change["added"])
        
        return list(set(newly_added))  # Remove duplicates
    
    def is_stock_new(self, stock: str, watchlist_name: str, hours: int = 24) -> bool:
        """Check if a stock was added recently"""
        newly_added = self.get_newly_added_stocks(watchlist_name, hours)
        return stock in newly_added

# Global tracker instance
tracker = StockChangeTracker()

def track_watchlist_changes(watchlist_name: str, stocks: List[str]) -> Dict:
    """Convenience function to track changes"""
    return tracker.update_watchlist(watchlist_name, stocks)

def get_stock_status(stock: str, watchlist_name: str) -> str:
    """Get status emoji for stock (NEW, REMOVED, or empty)"""
    if tracker.is_stock_new(stock, watchlist_name, hours=24):
        return "🆕 NEW"
    return ""

def format_stock_with_status(stock: str, watchlist_name: str) -> str:
    """Format stock symbol with status indicator"""
    status = get_stock_status(stock, watchlist_name)
    if status:
        return f"{stock} {status}"
    return stock