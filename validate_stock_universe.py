#!/usr/bin/env python3
"""
Stock Universe Validator and Cleaner
Identifies and removes delisted/invalid tickers, updates changed symbols
"""

import yfinance as yf
import time
from datetime import datetime
import json

# Known ticker changes and issues
TICKER_UPDATES = {
    # Delisted/Merged/Acquired companies
    "ANSS": None,  # Ansys - check if still valid
    "SQ": "BLOCK",  # Square changed to Block
    "ANTM": "ELV",  # Anthem changed to Elevance Health
    "DFS": "DFS",  # Discover Financial - should be valid, check
    "FISV": "FI",  # Fiserv changed ticker
    "CHEWY": "CHWY",  # Chewy correct ticker
    "WBA": "WBA",  # Walgreens - should be valid, check
    "GRUB": None,  # GrubHub acquired by Just Eat Takeaway
    "TWTR": None,  # Twitter acquired by Elon Musk, delisted
    "MRO": "MRO",  # Marathon Oil - should be valid, check
    "PXD": "PXD",  # Pioneer Natural Resources - check if still valid
    "WORK": None,  # Slack acquired by Salesforce
    "XLNX": None,  # Xilinx acquired by AMD
    "C3AI": "AI",  # C3.ai correct ticker is AI
    "NOVA": "NVMI",  # Nova Measuring Instruments
    "BLUE": "BLUE",  # bluebird bio - check if still valid
    "SAGE": "SAGE",  # Sage Therapeutics - check if still valid
    "ATVI": None,  # Activision Blizzard acquired by Microsoft
    "ONDK": "ONDK",  # On Deck Capital - check if still valid
    "ASTR": "ASTR",  # Astra Space - check if still valid
    "MAXR": "MAXR",  # Maxar Technologies - check if still valid
    "VORB": None,  # Virgin Orbit - went bankrupt
    "HEXO": "HEXO",  # Hexo Corp - check if still valid
    "HCP": "PEAK",  # HCP changed to Healthpeak Properties
    "PEAK": "PEAK",  # Healthpeak Properties
    "AIRB": None,  # Invalid ticker
    
    # Additional known changes
    "FB": "META",  # Facebook to Meta
    "GOOG": "GOOGL",  # Use Class A shares
    "BRK-A": "BRK.A",  # Berkshire Hathaway Class A
    "BRK-B": "BRK.B",  # Berkshire Hathaway Class B
}

def validate_ticker(symbol, max_retries=2):
    """Validate if a ticker symbol is still active and tradeable"""
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get recent data
            hist = ticker.history(period="5d")
            info = ticker.info
            
            # Check if we have valid data
            if hist.empty:
                print(f"❌ {symbol}: No price history")
                return False
            
            # Check if it's a valid stock (has market cap or is an ETF)
            market_cap = info.get('marketCap', 0)
            quote_type = info.get('quoteType', '')
            
            if market_cap == 0 and quote_type not in ['ETF', 'MUTUALFUND']:
                # Try to get basic quote data
                try:
                    current_price = hist['Close'].iloc[-1]
                    if current_price > 0:
                        print(f"✅ {symbol}: Valid (Price: ${current_price:.2f})")
                        return True
                    else:
                        print(f"❌ {symbol}: Invalid price data")
                        return False
                except:
                    print(f"❌ {symbol}: No valid price data")
                    return False
            else:
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
                print(f"✅ {symbol}: Valid (Price: ${current_price:.2f}, MCap: ${market_cap/1e9:.1f}B)")
                return True
                
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ {symbol}: Error - {str(e)[:50]}...")
                return False
            time.sleep(1)  # Wait before retry
    
    return False

def clean_stock_universe():
    """Clean and validate the entire stock universe"""
    from stock_universe import get_comprehensive_stock_list
    
    print("🧹 Cleaning Stock Universe")
    print("=" * 50)
    
    # Get current stock list
    all_stocks = get_comprehensive_stock_list()
    print(f"📊 Starting with {len(all_stocks)} stocks")
    
    valid_stocks = []
    invalid_stocks = []
    updated_stocks = []
    
    for i, symbol in enumerate(all_stocks):
        print(f"\n[{i+1}/{len(all_stocks)}] Checking {symbol}...")
        
        # Check if we have a known update for this ticker
        if symbol in TICKER_UPDATES:
            new_symbol = TICKER_UPDATES[symbol]
            if new_symbol is None:
                print(f"🗑️  {symbol}: Known delisted/acquired - removing")
                invalid_stocks.append(symbol)
                continue
            elif new_symbol != symbol:
                print(f"🔄 {symbol} → {new_symbol}: Updating ticker")
                if validate_ticker(new_symbol):
                    valid_stocks.append(new_symbol)
                    updated_stocks.append((symbol, new_symbol))
                else:
                    invalid_stocks.append(symbol)
                continue
        
        # Validate the ticker
        if validate_ticker(symbol):
            valid_stocks.append(symbol)
        else:
            invalid_stocks.append(symbol)
        
        # Rate limiting
        if i % 10 == 0 and i > 0:
            print(f"\n📊 Progress: {i}/{len(all_stocks)} checked")
            print(f"   ✅ Valid: {len(valid_stocks)}")
            print(f"   ❌ Invalid: {len(invalid_stocks)}")
            time.sleep(2)  # Pause to avoid rate limiting
    
    # Summary
    print(f"\n📋 CLEANING SUMMARY")
    print("=" * 30)
    print(f"📊 Original stocks: {len(all_stocks)}")
    print(f"✅ Valid stocks: {len(valid_stocks)}")
    print(f"❌ Invalid stocks: {len(invalid_stocks)}")
    print(f"🔄 Updated tickers: {len(updated_stocks)}")
    print(f"📈 Success rate: {len(valid_stocks)/len(all_stocks)*100:.1f}%")
    
    # Show invalid stocks
    if invalid_stocks:
        print(f"\n❌ INVALID STOCKS TO REMOVE:")
        for stock in invalid_stocks:
            print(f"   {stock}")
    
    # Show updated stocks
    if updated_stocks:
        print(f"\n🔄 TICKER UPDATES:")
        for old, new in updated_stocks:
            print(f"   {old} → {new}")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'original_count': len(all_stocks),
        'valid_stocks': valid_stocks,
        'invalid_stocks': invalid_stocks,
        'updated_stocks': updated_stocks,
        'success_rate': len(valid_stocks)/len(all_stocks)*100
    }
    
    with open('stock_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to stock_validation_results.json")
    
    return results

def quick_fix_known_issues():
    """Quick fix for known problematic tickers"""
    print("🔧 Quick Fix for Known Issues")
    print("=" * 40)
    
    # Read current stock universe file
    with open('stock_universe.py', 'r') as f:
        content = f.read()
    
    # Apply known fixes
    fixes_applied = 0
    
    # Remove known delisted stocks
    delisted = [
        '"ANSS"', '"GRUB"', '"TWTR"', '"WORK"', '"XLNX"', '"ATVI"', 
        '"VORB"', '"AIRB"', '"C3AI"'
    ]
    
    for stock in delisted:
        if stock in content:
            content = content.replace(f'{stock}, ', '')
            content = content.replace(f', {stock}', '')
            content = content.replace(stock, '')
            fixes_applied += 1
            print(f"🗑️  Removed {stock}")
    
    # Update known ticker changes
    ticker_changes = [
        ('"SQ"', '"BLOCK"'),
        ('"ANTM"', '"ELV"'),
        ('"FISV"', '"FI"'),
        ('"CHEWY"', '"CHWY"'),
        ('"C3AI"', '"AI"'),
        ('"HCP"', '"PEAK"'),
        ('"FB"', '"META"')
    ]
    
    for old, new in ticker_changes:
        if old in content:
            content = content.replace(old, new)
            fixes_applied += 1
            print(f"🔄 Updated {old} → {new}")
    
    # Write back the fixed content
    if fixes_applied > 0:
        with open('stock_universe.py', 'w') as f:
            f.write(content)
        print(f"\n✅ Applied {fixes_applied} fixes to stock_universe.py")
    else:
        print("ℹ️  No fixes needed")
    
    return fixes_applied

if __name__ == "__main__":
    print("🚀 Stock Universe Validation Tool")
    print("=" * 50)
    
    # Quick fix first
    quick_fix_known_issues()
    
    # Ask user if they want to run full validation
    print(f"\n🔍 Full validation will check all ~600 stocks")
    print(f"   This may take 10-15 minutes due to API rate limits")
    
    choice = input("\nRun full validation? (y/n): ").lower().strip()
    
    if choice == 'y':
        results = clean_stock_universe()
        print(f"\n🎉 Validation complete!")
    else:
        print(f"ℹ️  Skipping full validation. Quick fixes applied.")