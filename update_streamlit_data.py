#!/usr/bin/env python3
"""
Auto-update Streamlit Data
Runs daily to update data for Streamlit dashboard
"""

import subprocess
import sys
from datetime import datetime
import json
import os

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def run_gemma_analysis():
    """Run Gemma AI analysis"""
    log("🤖 Running Gemma AI analysis...")
    try:
        result = subprocess.run(
            [sys.executable, 'gemma_market_analysis.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        if result.returncode == 0:
            log("✅ Gemma analysis complete")
            return True
        else:
            log(f"❌ Gemma analysis failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log("❌ Gemma analysis timed out")
        return False
    except Exception as e:
        log(f"❌ Error running Gemma: {e}")
        return False

def run_dividend_analysis():
    """Run comprehensive dividend stock analysis (scans 600+ stocks)"""
    log("💰 Running dividend stock analysis (scans 600+ stocks)...")
    try:
        result = subprocess.run(
            [sys.executable, 'dividend_stock_analyzer.py'],
            capture_output=True,
            text=True,
            timeout=900  # 15 minutes for comprehensive scan
        )
        if result.returncode == 0:
            log("✅ Dividend analysis complete")
            return True
        else:
            log(f"❌ Dividend analysis failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log("❌ Dividend analysis timed out (15 min limit)")
        return False
    except Exception as e:
        log(f"❌ Error running dividend analysis: {e}")
        return False

def update_recommendations():
    """Update recommendations from scheduled alerts"""
    log("📊 Checking for new recommendations...")
    if os.path.exists('last_recommendations.json'):
        with open('last_recommendations.json', 'r') as f:
            data = json.load(f)
        log(f"✅ Found {len(data.get('buy_signals', []))} BUY signals")
        return True
    else:
        log("⚠️ No recommendations file found")
        return False

def create_summary():
    """Create daily summary"""
    log("📝 Creating daily summary...")
    
    summary = {
        'date': datetime.now().isoformat(),
        'gemma_available': os.path.exists('gemma_top_10_picks.json'),
        'dividend_available': os.path.exists('top_50_dividend_stocks.json'),
        'recommendations_available': os.path.exists('last_recommendations.json'),
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Add Gemma picks count
    if summary['gemma_available']:
        with open('gemma_top_10_picks.json', 'r') as f:
            gemma_data = json.load(f)
        summary['gemma_picks_count'] = len(gemma_data.get('picks', []))
    
    # Add dividend stocks count
    if summary['dividend_available']:
        with open('top_50_dividend_stocks.json', 'r') as f:
            dividend_data = json.load(f)
        summary['dividend_stocks_count'] = len(dividend_data.get('top_50_dividend_stocks', []))
        summary['total_dividend_stocks'] = dividend_data.get('total_dividend_stocks', 0)
    
    # Add recommendations count
    if summary['recommendations_available']:
        with open('last_recommendations.json', 'r') as f:
            rec_data = json.load(f)
        summary['buy_signals_count'] = len(rec_data.get('buy_signals', []))
        summary['watch_signals_count'] = len(rec_data.get('watch_signals', []))
    
    # Save summary
    with open('streamlit_data_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    log("✅ Summary created")
    return True

def main():
    """Main update function"""
    log("🚀 Starting Streamlit data update")
    log("=" * 60)
    
    # Run Gemma analysis
    gemma_success = run_gemma_analysis()
    
    # Run dividend analysis
    dividend_success = run_dividend_analysis()
    
    # Update recommendations
    rec_success = update_recommendations()
    
    # Create summary
    summary_success = create_summary()
    
    log("=" * 60)
    if gemma_success and dividend_success and rec_success and summary_success:
        log("✅ All updates complete!")
        return 0
    else:
        log("⚠️ Some updates failed, but continuing...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
