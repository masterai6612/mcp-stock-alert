#!/usr/bin/env python3
"""
Comprehensive Stock Universe
Top S&P 500 stocks, IPOs, and trending stocks with $10B+ market cap
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import json

# Top S&P 500 stocks with $10B+ market cap (sorted by market cap)
SP500_LARGE_CAPS = [
    # Mega caps ($1T+)
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    
    # Large caps ($100B - $1T)
    "AVGO", "LLY", "JPM", "UNH", "XOM", "V", "PG", "JNJ", "MA", "HD",
    "CVX", "ABBV", "NFLX", "BAC", "CRM", "KO", "ASML", "AZN", "COST",
    "PEP", "TMO", "MRK", "ADBE", "WMT", "CSCO", "ACN", "LIN", "AMD",
    "QCOM", "ABT", "TXN", "DHR", "INTU", "VZ", "AMGN", "SPGI", "CAT",
    "NOW", "ISRG", "PFE", "BKNG", "GE", "HON", "AXP", "T", "NEE",
    "IBM", "LOW", "SYK", "UBER", "PGR", "RTX", "ELV", "BSX", "VRTX",
    "MDT", "GILD", "ADI", "C", "LRCX", "SCHW", "AMT", "AMAT", "DE",
    "BLK", "TMUS", "MDLZ", "CVS", "FI", "REGN", "CB", "SO", "WM",
    "EQIX", "DUK", "ZTS", "ITW", "AON", "CL", "APD", "CMG", "MMC",
    "ICE", "PLD", "FCX", "USB", "PNC", "KLAC", "SHW", "EMR", "GD",
    "PYPL", "TJX", "MCO", "NSC", "BDX", "ECL", "WELL", "MSI", "TGT",
    "COF", "DFS", "ROP", "CARR", "PCAR", "NUE", "CTAS", "ORLY", "AJG",
    "CME", "TRV", "FAST", "PAYX", "ROST", "ODFL", "EA", "VRSK", "KMB",
    "CTSH", "DXCM", "LULU", "CHTR", "MCHP", "NXPI", "CPRT", "WDAY",
    "TEAM", "ADSK", "GRMN", "CRWD", "FTNT", "PANW", "SNOW", "ZS",
    
    # AI & Technology leaders
    "CRM", "ORCL", "INTC", "MU", "MRVL", "SNPS", "CDNS", "ANSS",
    
    # Healthcare & Biotech
    "UNH", "JNJ", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "VRTX", "REGN", "BIIB", "ILMN", "MRNA", "BNTX",
    
    # Financial services
    "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "SCHW", "BLK", "SPGI",
    
    # Energy & Materials
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "KMI", "OKE",
    
    # Consumer & Retail
    "AMZN", "TSLA", "HD", "WMT", "COST", "TGT", "LOW", "SBUX", "MCD", "NKE",
    
    # Industrial & Defense
    "CAT", "HON", "GE", "RTX", "LMT", "BA", "UPS", "FDX", "DE", "MMM"
]

# Recent IPOs and high-growth stocks (2020-2024)
RECENT_IPOS_AND_GROWTH = [
    # Recent IPOs with $10B+ potential
    "RIVN", "LCID", "RBLX", "COIN", "HOOD", "SOFI", "AFRM", "UPST",
    "OPEN", "WISH", "CLOV", "SPCE", "PLTR", "SNOW", "AI", "C3AI",
    "DDOG", "CRWD", "ZM", "PTON", "NFLX", "ROKU", "PINS", "SNAP",
    "TWTR", "SQ", "SHOP", "SPOT", "UBER", "LYFT", "DASH", "ABNB",
    
    # High-growth tech
    "NVDA", "AMD", "TSM", "ASML", "LRCX", "KLAC", "AMAT", "MU",
    "MRVL", "QCOM", "AVGO", "TXN", "ADI", "MCHP", "NXPI", "SWKS",
    
    # Cloud & SaaS
    "CRM", "NOW", "WDAY", "ADBE", "INTU", "ORCL", "MSFT", "GOOGL",
    "AMZN", "TEAM", "ATLASSIAN", "ZM", "OKTA", "DDOG", "NET", "FSLY",
    
    # Fintech & Payments
    "V", "MA", "PYPL", "SQ", "COIN", "HOOD", "SOFI", "AFRM", "UPST",
    
    # EV & Clean Energy
    "TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "ENPH", "SEDG", "NEE",
    
    # Biotech & Healthcare Innovation
    "MRNA", "BNTX", "NVAX", "REGN", "GILD", "VRTX", "BIIB", "ILMN",
    
    # Gaming & Entertainment
    "RBLX", "EA", "ATVI", "TTWO", "NFLX", "DIS", "ROKU", "PINS",
    
    # Cybersecurity
    "CRWD", "ZS", "OKTA", "PANW", "FTNT", "NET", "S", "CYBR"
]

# Trending/Meme stocks and recent market darlings
TRENDING_STOCKS = [
    # Meme stocks
    "GME", "AMC", "BBBY", "KOSS", "EXPR", "NAKD", "SNDL", "CLOV",
    
    # Recent market favorites
    "AAPL", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "MSFT", "NFLX",
    
    # AI & Machine Learning
    "NVDA", "AMD", "GOOGL", "MSFT", "META", "ORCL", "CRM", "NOW",
    "AI", "C3AI", "PLTR", "SNOW", "DDOG", "NET", "CRWD", "ZS",
    
    # Electric Vehicles
    "TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "F", "GM",
    
    # Space & Innovation
    "SPCE", "RKLB", "ASTR", "PL", "MAXR", "IRDM",
    
    # Cannabis & Alternative investments
    "TLRY", "CGC", "ACB", "CRON", "SNDL", "HEXO",
    
    # Social Media & Communication
    "META", "SNAP", "PINS", "TWTR", "RBLX", "MTCH", "BMBL",
    
    # Streaming & Content
    "NFLX", "DIS", "ROKU", "FUBO", "PARA", "WBD", "SPOT"
]

# Canadian stocks (TSX)
CANADIAN_LARGE_CAPS = [
    "SHOP", "TD", "RY", "BNS", "BMO", "CM", "ENB", "CNR", "CP", "SLF",
    "MFC", "BAM", "CCL-B", "WCN", "TRI", "CNQ", "SU", "IMO", "CVE",
    "ABX", "GOLD", "K", "FM", "TKO", "WPM", "AEM", "KL", "NGT"
]

def get_comprehensive_stock_list():
    """Get comprehensive list of stocks to monitor"""
    all_stocks = []
    
    # Add all categories
    all_stocks.extend(SP500_LARGE_CAPS)
    all_stocks.extend(RECENT_IPOS_AND_GROWTH)
    all_stocks.extend(TRENDING_STOCKS)
    all_stocks.extend(CANADIAN_LARGE_CAPS)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_stocks = []
    for stock in all_stocks:
        if stock not in seen:
            seen.add(stock)
            unique_stocks.append(stock)
    
    return unique_stocks

def filter_by_market_cap(symbols, min_market_cap=10_000_000_000):
    """Filter stocks by minimum market cap ($10B default)"""
    filtered_stocks = []
    
    print(f"🔍 Filtering {len(symbols)} stocks by market cap (${min_market_cap/1_000_000_000:.0f}B+)...")
    
    for i, symbol in enumerate(symbols):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            market_cap = info.get('marketCap', 0)
            
            if market_cap >= min_market_cap:
                filtered_stocks.append({
                    'symbol': symbol,
                    'market_cap': market_cap,
                    'company_name': info.get('longName', symbol),
                    'sector': info.get('sector', 'Unknown')
                })
                print(f"✅ {symbol}: ${market_cap/1_000_000_000:.1f}B")
            else:
                print(f"❌ {symbol}: ${market_cap/1_000_000_000:.1f}B (below threshold)")
                
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"📊 Processed {i + 1}/{len(symbols)} stocks...")
                
        except Exception as e:
            print(f"⚠️  Error checking {symbol}: {e}")
            continue
    
    return filtered_stocks

def get_recent_ipos(days_back=365):
    """Get recent IPOs from the last N days"""
    # This would typically require a specialized API
    # For now, return our curated list of recent IPOs
    return [
        "RIVN", "LCID", "RBLX", "COIN", "HOOD", "SOFI", "AFRM", "UPST",
        "AI", "SNOW", "DDOG", "CRWD", "NET", "FSLY", "ABNB", "DASH"
    ]

def save_stock_universe(filename="stock_universe.json"):
    """Save the comprehensive stock universe to file"""
    universe = {
        'timestamp': datetime.now().isoformat(),
        'categories': {
            'sp500_large_caps': SP500_LARGE_CAPS,
            'recent_ipos_growth': RECENT_IPOS_AND_GROWTH,
            'trending_stocks': TRENDING_STOCKS,
            'canadian_large_caps': CANADIAN_LARGE_CAPS
        },
        'all_unique_stocks': get_comprehensive_stock_list(),
        'total_count': len(get_comprehensive_stock_list())
    }
    
    with open(filename, 'w') as f:
        json.dump(universe, f, indent=2)
    
    print(f"💾 Stock universe saved to {filename}")
    print(f"📊 Total unique stocks: {universe['total_count']}")
    
    return universe

if __name__ == "__main__":
    print("🚀 Building Comprehensive Stock Universe")
    print("=" * 50)
    
    # Get all stocks
    all_stocks = get_comprehensive_stock_list()
    print(f"📊 Total unique stocks: {len(all_stocks)}")
    
    # Save to file
    universe = save_stock_universe()
    
    # Show breakdown by category
    print(f"\n📋 Stock Categories:")
    print(f"   S&P 500 Large Caps: {len(SP500_LARGE_CAPS)}")
    print(f"   Recent IPOs & Growth: {len(RECENT_IPOS_AND_GROWTH)}")
    print(f"   Trending Stocks: {len(TRENDING_STOCKS)}")
    print(f"   Canadian Large Caps: {len(CANADIAN_LARGE_CAPS)}")
    
    # Optional: Filter by market cap (uncomment to run)
    # print(f"\n🔍 Filtering by $10B+ market cap...")
    # filtered = filter_by_market_cap(all_stocks[:50])  # Test with first 50
    # print(f"✅ {len(filtered)} stocks meet the criteria")