#!/usr/bin/env python3
"""
Additional Dashboard Features
Extended functionality for the web dashboard
"""

import json
import os
from datetime import datetime, timedelta
import yfinance as yf
from enhanced_yahoo_client import EnhancedYahooClient

def get_system_logs():
    """Get recent system logs and alerts"""
    logs = []
    
    # Check sent alerts
    if os.path.exists('sent_alerts.json'):
        try:
            with open('sent_alerts.json', 'r') as f:
                alerts = json.load(f)
            
            for date, symbols in alerts.items():
                for symbol in symbols:
                    logs.append({
                        'timestamp': f"{date} 12:00:00",  # Approximate time
                        'type': 'alert',
                        'message': f"Upward trend alert sent for {symbol}",
                        'level': 'info'
                    })
        except Exception as e:
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'error',
                'message': f"Error reading alerts: {e}",
                'level': 'error'
            })
    
    # Check stock tracking changes
    if os.path.exists('stock_tracking.json'):
        try:
            with open('stock_tracking.json', 'r') as f:
                tracking = json.load(f)
            
            for change in tracking.get('change_history', [])[-10:]:  # Last 10 changes
                if change.get('added'):
                    logs.append({
                        'timestamp': change['timestamp'],
                        'type': 'watchlist',
                        'message': f"Added stocks to {change['watchlist']}: {', '.join(change['added'])}",
                        'level': 'info'
                    })
                if change.get('removed'):
                    logs.append({
                        'timestamp': change['timestamp'],
                        'type': 'watchlist',
                        'message': f"Removed stocks from {change['watchlist']}: {', '.join(change['removed'])}",
                        'level': 'warning'
                    })
        except Exception as e:
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'error',
                'message': f"Error reading tracking: {e}",
                'level': 'error'
            })
    
    # Sort by timestamp (most recent first)
    logs.sort(key=lambda x: x['timestamp'], reverse=True)
    return logs[:20]  # Return last 20 logs

def get_performance_metrics():
    """Get system performance metrics"""
    metrics = {
        'alerts_last_7_days': 0,
        'stocks_added_last_7_days': 0,
        'avg_daily_alerts': 0,
        'most_alerted_stock': None,
        'best_performing_theme': None
    }
    
    try:
        # Calculate alerts in last 7 days
        if os.path.exists('sent_alerts.json'):
            with open('sent_alerts.json', 'r') as f:
                alerts = json.load(f)
            
            last_7_days = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                last_7_days.append(date)
            
            total_alerts = 0
            stock_counts = {}
            
            for date in last_7_days:
                if date in alerts:
                    daily_alerts = len(alerts[date])
                    total_alerts += daily_alerts
                    
                    for stock in alerts[date]:
                        stock_counts[stock] = stock_counts.get(stock, 0) + 1
            
            metrics['alerts_last_7_days'] = total_alerts
            metrics['avg_daily_alerts'] = round(total_alerts / 7, 1)
            
            if stock_counts:
                metrics['most_alerted_stock'] = max(stock_counts, key=stock_counts.get)
        
        # Calculate stocks added in last 7 days
        if os.path.exists('stock_tracking.json'):
            with open('stock_tracking.json', 'r') as f:
                tracking = json.load(f)
            
            cutoff_date = datetime.now() - timedelta(days=7)
            stocks_added = 0
            
            for change in tracking.get('change_history', []):
                change_date = datetime.fromisoformat(change['timestamp'])
                if change_date >= cutoff_date and change.get('added'):
                    stocks_added += len(change['added'])
            
            metrics['stocks_added_last_7_days'] = stocks_added
        
        # Get best performing theme
        try:
            client = EnhancedYahooClient()
            themes = client.get_investment_themes()
            if themes and themes.get('themes'):
                best_theme = max(themes['themes'], key=lambda x: x.get('avg_change_percent', 0))
                metrics['best_performing_theme'] = {
                    'name': best_theme['theme'],
                    'performance': best_theme['avg_change_percent']
                }
        except Exception as e:
            print(f"Error getting themes for metrics: {e}")
    
    except Exception as e:
        print(f"Error calculating performance metrics: {e}")
    
    return metrics

def get_stock_alerts_history():
    """Get detailed history of stock alerts"""
    history = []
    
    if os.path.exists('sent_alerts.json'):
        try:
            with open('sent_alerts.json', 'r') as f:
                alerts = json.load(f)
            
            for date, symbols in alerts.items():
                for symbol in symbols:
                    # Try to get current stock data for context
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        hist_data = ticker.history(period='1d')
                        
                        current_price = hist_data['Close'].iloc[-1] if not hist_data.empty else 0
                        
                        history.append({
                            'date': date,
                            'symbol': symbol,
                            'company': info.get('longName', symbol),
                            'current_price': current_price,
                            'sector': info.get('sector', 'Unknown')
                        })
                    except:
                        history.append({
                            'date': date,
                            'symbol': symbol,
                            'company': symbol,
                            'current_price': 0,
                            'sector': 'Unknown'
                        })
        except Exception as e:
            print(f"Error getting alerts history: {e}")
    
    # Sort by date (most recent first)
    history.sort(key=lambda x: x['date'], reverse=True)
    return history[:50]  # Return last 50 alerts

def export_data_to_json():
    """Export all dashboard data to JSON for backup/analysis"""
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'system_logs': get_system_logs(),
        'performance_metrics': get_performance_metrics(),
        'alerts_history': get_stock_alerts_history()
    }
    
    filename = f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        return filename
    except Exception as e:
        print(f"Error exporting data: {e}")
        return None

if __name__ == "__main__":
    # Test the functions
    print("📊 Testing dashboard features...")
    
    print("\n📋 System Logs:")
    logs = get_system_logs()
    for log in logs[:5]:
        print(f"  {log['timestamp']}: {log['message']}")
    
    print("\n📈 Performance Metrics:")
    metrics = get_performance_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n💾 Exporting data...")
    filename = export_data_to_json()
    if filename:
        print(f"  ✅ Data exported to: {filename}")
    else:
        print("  ❌ Export failed")