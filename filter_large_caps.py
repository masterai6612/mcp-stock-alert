#!/usr/bin/env python3
"""
Filter stocks by market cap and create optimized watchlists
Focus on $10B+ market cap stocks for better liquidity and stability
"""

import yfinance as yf
import json
from datetime import datetime
from stock_universe import get_comprehensive_stock_list
import time

def get_stock_info_batch(symbols, batch_size=20):
    """Get stock info in batches to avoid rate limiting"""
    all_stock_info = []
    
    print(f"📊 Processing {len(symbols)} stocks in batches of {batch_size}...")
    
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        print(f"🔄 Processing batch {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}: {batch[0]} to {batch[-1]}")
        
        for symbol in batch:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                market_cap = info.get('marketCap', 0)
                if market_cap and market_cap > 0:
                    all_stock_info.append({
                        'symbol': symbol,
                        'company_name': info.get('longName', symbol),
                        'market_cap': market_cap,
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'country': info.get('country', 'Unknown'),
                        'exchange': info.get('exchange', 'Unknown'),
                        'currency': info.get('currency', 'USD')
                    })
                    
                    # Show progress for large caps
                    if market_cap >= 10_000_000_000:
                        print(f"  ✅ {symbol}: ${market_cap/1_000_000_000:.1f}B - {info.get('longName', symbol)[:40]}")
                
            except Exception as e:
                print(f"  ⚠️  {symbol}: Error - {e}")
                continue
        
        # Small delay between batches to be respectful to Yahoo Finance
        time.sleep(2)
    
    return all_stock_info

def create_filtered_watchlists(stock_info):
    """Create optimized watchlists based on market cap and categories"""
    
    # Filter by market cap
    large_caps = [s for s in stock_info if s['market_cap'] >= 10_000_000_000]  # $10B+
    mega_caps = [s for s in stock_info if s['market_cap'] >= 100_000_000_000]  # $100B+
    
    # Sort by market cap
    large_caps.sort(key=lambda x: x['market_cap'], reverse=True)
    mega_caps.sort(key=lambda x: x['market_cap'], reverse=True)
    
    # Create sector-based lists
    sectors = {}
    for stock in large_caps:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    # Create optimized watchlists
    watchlists = {
        'mega_caps_100b_plus': [s['symbol'] for s in mega_caps],
        'large_caps_10b_plus': [s['symbol'] for s in large_caps],
        'top_50_by_market_cap': [s['symbol'] for s in large_caps[:50]],
        'top_100_by_market_cap': [s['symbol'] for s in large_caps[:100]],
        'morning_focus': [s['symbol'] for s in large_caps[:30]],  # Top 30 for morning alerts
        'intraday_monitor': [s['symbol'] for s in large_caps[:75]]  # Top 75 for intraday
    }
    
    # Add sector-specific lists
    for sector, stocks in sectors.items():
        if len(stocks) >= 5:  # Only sectors with 5+ stocks
            sector_key = f"sector_{sector.lower().replace(' ', '_').replace('&', 'and')}"
            watchlists[sector_key] = [s['symbol'] for s in stocks[:20]]  # Top 20 per sector
    
    return watchlists, large_caps, sectors

def main():
    """Main function to filter and create optimized stock lists"""
    print("🔍 FILTERING STOCKS BY MARKET CAP ($10B+)")
    print("=" * 60)
    
    # Get all stocks
    all_symbols = get_comprehensive_stock_list()
    print(f"📊 Starting with {len(all_symbols)} total stocks")
    
    # Get stock information (this will take a few minutes)
    print(f"\n⏳ This will take 3-5 minutes to avoid rate limiting...")
    stock_info = get_stock_info_batch(all_symbols, batch_size=15)
    
    # Create filtered watchlists
    watchlists, large_caps, sectors = create_filtered_watchlists(stock_info)
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_stocks_analyzed': len(all_symbols),
        'large_caps_10b_plus': len(large_caps),
        'mega_caps_100b_plus': len([s for s in large_caps if s['market_cap'] >= 100_000_000_000]),
        'watchlists': watchlists,
        'stock_details': large_caps,
        'sectors': {sector: len(stocks) for sector, stocks in sectors.items()}
    }
    
    # Save to file
    with open('filtered_stock_universe.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Display summary
    print(f"\n📊 FILTERING RESULTS:")
    print(f"=" * 40)
    print(f"✅ Total stocks analyzed: {len(all_symbols)}")
    print(f"✅ Large caps ($10B+): {len(large_caps)}")
    print(f"✅ Mega caps ($100B+): {results['mega_caps_100b_plus']}")
    
    print(f"\n📋 OPTIMIZED WATCHLISTS CREATED:")
    for name, symbols in watchlists.items():
        if not name.startswith('sector_'):
            print(f"   📈 {name}: {len(symbols)} stocks")
    
    print(f"\n🏭 SECTOR BREAKDOWN:")
    for sector, count in sorted(sectors.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"   🏢 {sector}: {len(count)} stocks")
    
    print(f"\n💾 Results saved to: filtered_stock_universe.json")
    print(f"🎯 Ready to use optimized stock lists!")

if __name__ == "__main__":
    main()