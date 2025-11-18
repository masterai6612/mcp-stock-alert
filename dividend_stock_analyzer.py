#!/usr/bin/env python3
"""
Comprehensive Dividend Stock Analyzer
Scans 600+ stocks from stock universe for best dividend opportunities
Combines growth potential with dividend income
"""

import yfinance as yf
import json
from datetime import datetime
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Import comprehensive stock universe
try:
    from stock_universe_clean import get_comprehensive_stock_list
    USE_COMPREHENSIVE_UNIVERSE = True
except ImportError:
    try:
        from stock_universe import get_comprehensive_stock_list
        USE_COMPREHENSIVE_UNIVERSE = True
    except ImportError:
        USE_COMPREHENSIVE_UNIVERSE = False
        print("⚠️ Could not import stock universe")

def get_stock_dividend_data(symbol):
    """
    Get dividend and technical data for a single stock
    Returns None if stock doesn't meet criteria
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get dividend yield
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield:
            dividend_yield = dividend_yield * 100  # Convert to percentage
        
        # Skip if no dividend or yield too low
        if not dividend_yield or dividend_yield < 2.0:
            return None
        
        # Get price data for technical analysis
        hist = ticker.history(period='3mo')
        if hist.empty or len(hist) < 20:
            return None
        
        current_price = hist['Close'].iloc[-1]
        price_52w_high = info.get('fiftyTwoWeekHigh', current_price)
        price_52w_low = info.get('fiftyTwoWeekLow', current_price)
        
        # Calculate price position
        if price_52w_high > price_52w_low:
            price_position = ((current_price - price_52w_low) / (price_52w_high - price_52w_low)) * 100
        else:
            price_position = 50
        
        # Calculate RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        # Calculate volume trend
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].tail(5).mean()
        volume_trend = ((recent_volume - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
        
        # Calculate price change
        price_1w_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else current_price
        price_1m_ago = hist['Close'].iloc[-20] if len(hist) >= 20 else current_price
        
        change_1w = ((current_price - price_1w_ago) / price_1w_ago * 100) if price_1w_ago > 0 else 0
        change_1m = ((current_price - price_1m_ago) / price_1m_ago * 100) if price_1m_ago > 0 else 0
        
        # Get company info
        company_name = info.get('longName', symbol)
        sector = info.get('sector', 'Unknown')
        market_cap = info.get('marketCap', 0)
        
        # Calculate technical score (0-10)
        technical_score = calculate_technical_score(
            rsi=current_rsi,
            price_position=price_position,
            volume_trend=volume_trend,
            change_1w=change_1w,
            change_1m=change_1m
        )
        
        # Calculate dividend score (0-100)
        dividend_score = calculate_dividend_score(
            technical_score=technical_score,
            dividend_yield=dividend_yield,
            change_1m=change_1m
        )
        
        # Determine category
        category = determine_category(dividend_yield, change_1m, technical_score)
        
        return {
            'symbol': symbol,
            'company_name': company_name,
            'sector': sector,
            'market_cap': market_cap,
            'current_price': round(current_price, 2),
            'dividend_yield': round(dividend_yield, 2),
            'change_1w': round(change_1w, 2),
            'change_1m': round(change_1m, 2),
            'rsi': round(current_rsi, 2),
            'price_position': round(price_position, 2),
            'volume_trend': round(volume_trend, 2),
            'technical_score': round(technical_score, 2),
            'dividend_score': round(dividend_score, 2),
            'category': category,
            'meets_growth_requirement': change_1m >= 7.0,
            'is_dividend_stock': True
        }
        
    except Exception as e:
        return None

def calculate_technical_score(rsi, price_position, volume_trend, change_1w, change_1m):
    """
    Calculate technical score (0-10)
    """
    score = 0
    
    # RSI score (0-3 points) - prefer 40-70 range
    if 40 <= rsi <= 70:
        score += 3
    elif 30 <= rsi < 40 or 70 < rsi <= 80:
        score += 2
    elif rsi < 30 or rsi > 80:
        score += 1
    
    # Price position score (0-2 points) - prefer not at extremes
    if 30 <= price_position <= 70:
        score += 2
    elif 20 <= price_position < 30 or 70 < price_position <= 80:
        score += 1
    
    # Volume trend score (0-2 points)
    if volume_trend > 20:
        score += 2
    elif volume_trend > 0:
        score += 1
    
    # Price momentum score (0-3 points)
    if change_1w > 3 and change_1m > 5:
        score += 3
    elif change_1w > 0 and change_1m > 0:
        score += 2
    elif change_1m > 0:
        score += 1
    
    return score

def calculate_dividend_score(technical_score, dividend_yield, change_1m):
    """
    Calculate combined dividend score (0-100)
    
    Weighting:
    - Technical score: 50 points (technical_score * 5)
    - Dividend yield: 30 points (up to 10% yield)
    - Growth potential: 20 points (1-month change)
    """
    # Technical component (0-50 points)
    technical_points = technical_score * 5
    
    # Dividend component (0-30 points) - cap at 10% yield
    dividend_points = min(dividend_yield * 3, 30)
    
    # Growth component (0-20 points) - cap at 10% growth
    growth_points = min(max(change_1m * 2, 0), 20)
    
    total_score = technical_points + dividend_points + growth_points
    
    return total_score

def determine_category(dividend_yield, change_1m, technical_score):
    """
    Determine stock category based on characteristics
    """
    is_high_yield = dividend_yield >= 4.0
    is_high_growth = change_1m >= 10.0
    is_good_growth = change_1m >= 7.0
    
    if is_high_growth and is_high_yield:
        return "Growth + High Dividend"
    elif is_good_growth and is_high_yield:
        return "Dividend + Growth"
    elif is_high_growth:
        return "Growth"
    elif is_high_yield:
        return "High Dividend"
    elif is_good_growth:
        return "Growth + Dividend"
    else:
        return "Dividend"

def scan_all_stocks_for_dividends(max_workers=10):
    """
    Scan all stocks from universe for dividend opportunities
    Uses parallel processing for speed
    """
    print("💰 COMPREHENSIVE DIVIDEND STOCK SCANNER")
    print("=" * 70)
    
    # Get stock universe
    if USE_COMPREHENSIVE_UNIVERSE:
        all_stocks = get_comprehensive_stock_list()
        print(f"📊 Scanning {len(all_stocks)} stocks from comprehensive universe")
    else:
        print("❌ Stock universe not available")
        return []
    
    print(f"🔍 Looking for stocks with dividend yield ≥ 2.0%")
    print(f"⚡ Using {max_workers} parallel workers for faster analysis")
    print("=" * 70)
    
    dividend_stocks = []
    processed = 0
    start_time = time.time()
    
    # Process stocks in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_symbol = {
            executor.submit(get_stock_dividend_data, symbol): symbol 
            for symbol in all_stocks
        }
        
        # Process completed tasks
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            processed += 1
            
            try:
                result = future.result()
                if result:
                    dividend_stocks.append(result)
                    print(f"✅ {symbol:8s} | Yield: {result['dividend_yield']:5.2f}% | "
                          f"Growth: {result['change_1m']:6.2f}% | Score: {result['dividend_score']:5.1f} | "
                          f"{result['category']}")
                
                # Progress update every 50 stocks
                if processed % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = processed / elapsed
                    remaining = (len(all_stocks) - processed) / rate
                    print(f"\n📊 Progress: {processed}/{len(all_stocks)} stocks "
                          f"({processed/len(all_stocks)*100:.1f}%) | "
                          f"Found: {len(dividend_stocks)} dividend stocks | "
                          f"ETA: {remaining/60:.1f} min\n")
                    
            except Exception as e:
                continue
    
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✅ Scan complete in {elapsed_time/60:.1f} minutes")
    print(f"📊 Processed: {processed} stocks")
    print(f"💰 Found: {len(dividend_stocks)} dividend-paying stocks")
    print(f"⚡ Rate: {processed/elapsed_time:.1f} stocks/second")
    
    # Sort by dividend score
    dividend_stocks.sort(key=lambda x: x['dividend_score'], reverse=True)
    
    return dividend_stocks

def get_top_dividend_stocks(dividend_stocks, top_n=50):
    """
    Get top N dividend stocks with category breakdown
    """
    top_stocks = dividend_stocks[:top_n]
    
    # Category breakdown
    categories = {}
    for stock in top_stocks:
        cat = stock['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n🏆 TOP {top_n} DIVIDEND STOCKS")
    print("=" * 70)
    print(f"\n📊 Category Breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count} stocks")
    
    print(f"\n💎 Top 10 Dividend Stocks:")
    for i, stock in enumerate(top_stocks[:10], 1):
        print(f"{i:2d}. {stock['symbol']:8s} | {stock['company_name'][:30]:30s} | "
              f"Yield: {stock['dividend_yield']:5.2f}% | Score: {stock['dividend_score']:5.1f} | "
              f"{stock['category']}")
    
    return top_stocks

def main():
    """Main function"""
    print("\n🚀 Starting Comprehensive Dividend Stock Analysis")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Scan all stocks
    dividend_stocks = scan_all_stocks_for_dividends(max_workers=15)
    
    if not dividend_stocks:
        print("❌ No dividend stocks found")
        return
    
    # Get top 50
    top_50 = get_top_dividend_stocks(dividend_stocks, top_n=50)
    
    # Save results
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_scanned': 533,  # From stock universe
        'total_dividend_stocks': len(dividend_stocks),
        'top_50_count': len(top_50),
        'criteria': {
            'min_dividend_yield': 2.0,
            'scoring': {
                'technical': '50%',
                'dividend_yield': '30%',
                'growth': '20%'
            }
        },
        'all_dividend_stocks': dividend_stocks,
        'top_50_dividend_stocks': top_50
    }
    
    # Save to JSON
    with open('top_50_dividend_stocks.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: top_50_dividend_stocks.json")
    print(f"📊 Total dividend stocks found: {len(dividend_stocks)}")
    print(f"🏆 Top 50 stocks saved")
    
    # Summary statistics
    if dividend_stocks:
        avg_yield = sum(s['dividend_yield'] for s in dividend_stocks) / len(dividend_stocks)
        max_yield = max(s['dividend_yield'] for s in dividend_stocks)
        avg_growth = sum(s['change_1m'] for s in dividend_stocks) / len(dividend_stocks)
        
        print(f"\n📈 Statistics:")
        print(f"   Average Dividend Yield: {avg_yield:.2f}%")
        print(f"   Maximum Dividend Yield: {max_yield:.2f}%")
        print(f"   Average 1-Month Growth: {avg_growth:.2f}%")
        print(f"   Stocks with 7%+ growth: {sum(1 for s in dividend_stocks if s['meets_growth_requirement'])}")
    
    print("\n✅ Analysis complete!")
    return top_50

if __name__ == "__main__":
    main()
