#!/usr/bin/env python3
"""
Stock Alert System Web Dashboard
Real-time monitoring of system health and top stocks
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
import psutil
from datetime import datetime, timedelta
import holidays
from enhanced_yahoo_client import EnhancedYahooClient
import yfinance as yf
import threading
import time
import numpy as np
import pandas as pd

app = Flask(__name__, template_folder='dashboard')

# Global cache for data
cache = {
    'last_update': None,
    'system_status': {},
    'top_stocks': [],
    'market_data': {},
    'earnings': [],
    'themes': {}
}

def convert_to_json_serializable(obj):
    """Convert pandas/numpy types to JSON serializable types"""
    if isinstance(obj, (np.integer, pd.Int64Dtype)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

def is_canadian_stock(symbol):
    """Check if a stock symbol is Canadian"""
    return symbol.endswith('.TO') or symbol.endswith('.V') or symbol.endswith('.CN')

def get_stock_market_info(symbol):
    """Get market information for a stock symbol"""
    if is_canadian_stock(symbol):
        return {
            'market': 'TSX',
            'currency': 'CAD',
            'flag': '🇨🇦',
            'exchange': 'Toronto Stock Exchange'
        }
    else:
        return {
            'market': 'US',
            'currency': 'USD', 
            'flag': '🇺🇸',
            'exchange': 'US Markets'
        }

def get_usd_cad_rate():
    """Get current USD/CAD exchange rate"""
    try:
        ticker = yf.Ticker('USDCAD=X')
        hist = ticker.history(period='1d')
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except:
        pass
    return 1.35  # Fallback rate

def get_system_health():
    """Get comprehensive system health status"""
    health = {
        'timestamp': datetime.now().isoformat(),
        'scheduler_running': False,
        'scheduler_pid': None,
        'scheduler_uptime': None,
        'next_alert': None,
        'market_status': 'closed',
        'alerts_sent_today': 0,
        'watchlists': {},
        'email_config': 'configured',
        'dependencies': 'ok'
    }
    
    # Check if scheduler is running
    try:
        result = subprocess.run(['pgrep', '-f', 'scheduled_market_alerts'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            health['scheduler_running'] = True
            health['scheduler_pid'] = pids[0] if pids else None
            
            # Get process uptime
            if health['scheduler_pid']:
                try:
                    proc = psutil.Process(int(health['scheduler_pid']))
                    create_time = datetime.fromtimestamp(proc.create_time())
                    uptime = datetime.now() - create_time
                    health['scheduler_uptime'] = str(uptime).split('.')[0]  # Remove microseconds
                except:
                    health['scheduler_uptime'] = 'unknown'
    except Exception as e:
        print(f"Error checking scheduler: {e}")
    
    # Check market status
    now = datetime.now()
    us_holidays = holidays.US(years=now.year)
    ca_holidays = holidays.CA(years=now.year)
    
    is_weekday = now.weekday() < 5
    is_holiday = now.date() in us_holidays or now.date() in ca_holidays
    
    # Market hours (9:30 AM - 4:00 PM EDT)
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if is_weekday and not is_holiday:
        if market_open_time <= now <= market_close_time:
            health['market_status'] = 'open'
        elif now < market_open_time:
            health['market_status'] = 'pre_market'
        else:
            health['market_status'] = 'after_hours'
    else:
        health['market_status'] = 'closed'
    
    # Calculate next alert time
    tomorrow = now + timedelta(days=1)
    next_alert_time = tomorrow.replace(hour=7, minute=30, second=0, microsecond=0)
    
    # Find next trading day
    while (next_alert_time.weekday() >= 5 or 
           next_alert_time.date() in us_holidays or 
           next_alert_time.date() in ca_holidays):
        next_alert_time += timedelta(days=1)
    
    health['next_alert'] = next_alert_time.strftime('%A, %B %d at 7:30 AM EDT')
    
    # Check alerts sent today
    if os.path.exists('sent_alerts.json'):
        try:
            with open('sent_alerts.json', 'r') as f:
                alerts = json.load(f)
            today = now.strftime('%Y-%m-%d')
            health['alerts_sent_today'] = len(alerts.get(today, []))
        except:
            health['alerts_sent_today'] = 0
    
    # Check watchlists and comprehensive stock universe
    health['watchlists'] = {}
    
    # Add comprehensive stock universe count
    try:
        from stock_universe import get_comprehensive_stock_list
        comprehensive_stocks = get_comprehensive_stock_list()
        health['watchlists']['Comprehensive Universe'] = len(comprehensive_stocks)
    except:
        pass
    
    # Check traditional watchlists from tracking file
    if os.path.exists('stock_tracking.json'):
        try:
            with open('stock_tracking.json', 'r') as f:
                tracking = json.load(f)
            traditional_watchlists = {
                name: len(stocks) 
                for name, stocks in tracking.get('watchlists', {}).items()
            }
            health['watchlists'].update(traditional_watchlists)
        except:
            pass
    
    return health

def get_top_stocks():
    """Get top performing stocks with technical analysis"""
    try:
        from stock_universe import get_comprehensive_stock_list
        client = EnhancedYahooClient()
        
        # Get comprehensive stock list but limit for dashboard performance
        all_symbols = get_comprehensive_stock_list()
        
        # For dashboard, focus on most liquid/popular stocks for faster loading
        priority_symbols = [
            # US Mega caps (always include)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            # US Large caps
            'AVGO', 'LLY', 'JPM', 'UNH', 'XOM', 'V', 'PG', 'JNJ', 'MA', 'HD',
            'CVX', 'ABBV', 'NFLX', 'BAC', 'CRM', 'KO', 'ASML', 'COST', 'PEP',
            # Recent IPOs & Growth
            'RIVN', 'LCID', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'SNOW', 'AI', 'CRWD',
            # Canadian Major Banks (US-listed)
            'TD', 'RY', 'BNS', 'BMO', 'CM',
            # Canadian Energy & Resources (US-listed)
            'ENB', 'CNQ', 'SU', 'CNR', 'CP',
            # Canadian Tech & Growth (US-listed)
            'SHOP', 'BAM', 'TRI',
            # Canadian TSX-listed (major ones)
            'RY.TO', 'TD.TO', 'SHOP.TO', 'ENB.TO', 'CNR.TO', 'CNQ.TO', 'SU.TO',
            'BNS.TO', 'BMO.TO', 'CM.TO', 'SLF.TO', 'MFC.TO', 'ABX.TO', 'GOLD.TO'
        ]
        
        # Use priority list for dashboard (faster loading)
        symbols = priority_symbols
        
        stocks_data = []
        for symbol in symbols:
            try:
                quote = client.get_stock_quote(symbol)
                if quote:
                    # Get additional technical data
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        # Calculate 5-day change
                        current = hist['Close'].iloc[-1]
                        five_days_ago = hist['Close'].iloc[0]
                        change_5d = ((current - five_days_ago) / five_days_ago) * 100
                        
                        # Get market info
                        market_info = get_stock_market_info(symbol)
                        
                        stocks_data.append({
                            'symbol': symbol,
                            'name': quote.get('company_name', symbol),
                            'price': float(quote.get('current_price', 0)) if quote.get('current_price') else 0,
                            'change_1d': float(quote.get('change_percent', 0)) if quote.get('change_percent') else 0,
                            'change_5d': float(change_5d) if not pd.isna(change_5d) else 0,
                            'volume': int(quote.get('volume', 0)) if quote.get('volume') else 0,
                            'market_cap': int(quote.get('market_cap', 0)) if quote.get('market_cap') else 0,
                            'market': market_info['market'],
                            'currency': market_info['currency'],
                            'flag': market_info['flag'],
                            'exchange': market_info['exchange']
                        })
            except Exception as e:
                print(f"Error getting data for {symbol}: {e}")
                continue
        
        # Sort by 1-day performance
        stocks_data.sort(key=lambda x: x['change_1d'], reverse=True)
        return stocks_data[:15]  # Top 15
        
    except Exception as e:
        print(f"Error getting top stocks: {e}")
        return []

def get_market_overview():
    """Get market indices overview including Canadian markets"""
    indices = {
        'S&P 500': '^GSPC',
        'NASDAQ': '^IXIC',
        'TSX Composite': '^GSPTSE',
        'TSX 60': '^TX60.TO',
        'Dow Jones': '^DJI',
        'Russell 2000': '^RUT',
        'VIX': '^VIX',
        'USD/CAD': 'USDCAD=X'
    }
    
    market_data = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2d')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change_pct = ((current - previous) / previous) * 100
                
                market_data[name] = {
                    'value': float(current) if not pd.isna(current) else 0,
                    'change': float(change_pct) if not pd.isna(change_pct) else 0,
                    'symbol': symbol
                }
        except Exception as e:
            print(f"Error getting {name}: {e}")
    
    return market_data

def update_cache():
    """Update cache with fresh data"""
    global cache
    
    print("🔄 Updating dashboard cache...")
    
    try:
        # Update system status
        cache['system_status'] = get_system_health()
        
        # Update top stocks
        cache['top_stocks'] = get_top_stocks()
        
        # Update market data
        cache['market_data'] = get_market_overview()
        
        # Update earnings and themes
        client = EnhancedYahooClient()
        earnings_raw = client.get_earnings_calendar(days_ahead=3)
        cache['earnings'] = convert_to_json_serializable(earnings_raw[:10] if earnings_raw else [])
        
        themes_raw = client.get_investment_themes()
        cache['themes'] = convert_to_json_serializable(themes_raw) if themes_raw else {}
        
        cache['last_update'] = datetime.now().isoformat()
        print("✅ Cache updated successfully")
        
    except Exception as e:
        print(f"❌ Error updating cache: {e}")

def background_updater():
    """Background thread to update cache every 5 minutes"""
    while True:
        update_cache()
        time.sleep(300)  # 5 minutes

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify(cache['system_status'])

@app.route('/api/stocks')
def api_stocks():
    """API endpoint for top stocks"""
    return jsonify(cache['top_stocks'])

@app.route('/api/market')
def api_market():
    """API endpoint for market data"""
    return jsonify(cache['market_data'])

@app.route('/api/earnings')
def api_earnings():
    """API endpoint for earnings"""
    return jsonify(cache['earnings'])

@app.route('/api/themes')
def api_themes():
    """API endpoint for investment themes"""
    return jsonify(cache['themes'])

@app.route('/api/canadian-stocks')
def api_canadian_stocks():
    """API endpoint for Canadian stocks specifically"""
    canadian_stocks = [stock for stock in cache['top_stocks'] if stock.get('market') == 'TSX']
    
    # If not enough Canadian stocks in cache, get fresh data
    if len(canadian_stocks) < 5:
        try:
            from stock_universe import CANADIAN_LARGE_CAPS
            client = EnhancedYahooClient()
            
            canadian_data = []
            # Get top Canadian stocks
            priority_canadian = ['RY.TO', 'TD.TO', 'SHOP.TO', 'ENB.TO', 'CNR.TO', 
                                'CNQ.TO', 'SU.TO', 'BNS.TO', 'BMO.TO', 'CM.TO']
            
            for symbol in priority_canadian[:10]:
                try:
                    quote = client.get_stock_quote(symbol)
                    if quote:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period='5d')
                        
                        if not hist.empty:
                            current = hist['Close'].iloc[-1]
                            five_days_ago = hist['Close'].iloc[0]
                            change_5d = ((current - five_days_ago) / five_days_ago) * 100
                            
                            market_info = get_stock_market_info(symbol)
                            
                            canadian_data.append({
                                'symbol': symbol,
                                'name': quote.get('company_name', symbol),
                                'price': float(quote.get('current_price', 0)) if quote.get('current_price') else 0,
                                'change_1d': float(quote.get('change_percent', 0)) if quote.get('change_percent') else 0,
                                'change_5d': float(change_5d) if not pd.isna(change_5d) else 0,
                                'volume': int(quote.get('volume', 0)) if quote.get('volume') else 0,
                                'market_cap': int(quote.get('market_cap', 0)) if quote.get('market_cap') else 0,
                                'market': market_info['market'],
                                'currency': market_info['currency'],
                                'flag': market_info['flag'],
                                'exchange': market_info['exchange']
                            })
                except Exception as e:
                    print(f"Error getting Canadian stock {symbol}: {e}")
                    continue
            
            canadian_data.sort(key=lambda x: x['change_1d'], reverse=True)
            return jsonify(canadian_data)
            
        except Exception as e:
            print(f"Error getting Canadian stocks: {e}")
    
    return jsonify(canadian_stocks)

@app.route('/api/market-comparison')
def api_market_comparison():
    """API endpoint for US vs Canadian market comparison"""
    try:
        usd_cad_rate = get_usd_cad_rate()
        
        us_stocks = [stock for stock in cache['top_stocks'] if stock.get('market') == 'US']
        canadian_stocks = [stock for stock in cache['top_stocks'] if stock.get('market') == 'TSX']
        
        comparison = {
            'usd_cad_rate': usd_cad_rate,
            'us_market': {
                'count': len(us_stocks),
                'avg_change': sum(s['change_1d'] for s in us_stocks) / len(us_stocks) if us_stocks else 0,
                'top_performer': max(us_stocks, key=lambda x: x['change_1d']) if us_stocks else None
            },
            'canadian_market': {
                'count': len(canadian_stocks),
                'avg_change': sum(s['change_1d'] for s in canadian_stocks) / len(canadian_stocks) if canadian_stocks else 0,
                'top_performer': max(canadian_stocks, key=lambda x: x['change_1d']) if canadian_stocks else None
            },
            'market_indices': {
                'sp500': cache['market_data'].get('S&P 500', {}),
                'tsx': cache['market_data'].get('TSX Composite', {}),
                'nasdaq': cache['market_data'].get('NASDAQ', {})
            }
        }
        
        return jsonify(comparison)
        
    except Exception as e:
        print(f"Error getting market comparison: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh')
def api_refresh():
    """Force refresh cache"""
    update_cache()
    return jsonify({'status': 'refreshed', 'timestamp': cache['last_update']})

if __name__ == '__main__':
    # Initial cache update
    update_cache()
    
    # Start background updater
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    print("🚀 Starting Stock Alert Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🔄 Data updates every 5 minutes (reduced API traffic)")
    
    app.run(host='0.0.0.0', port=5001, debug=False)