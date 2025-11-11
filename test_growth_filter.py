#!/usr/bin/env python3
"""Test the 7% growth filter"""

import sys
sys.path.append('.')

from current_stock_summary import get_technical_analysis

# Test with a few stocks
test_symbols = ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOGL']

print("🧪 Testing 7% Growth Filter")
print("=" * 60)

for symbol in test_symbols:
    print(f"\n📊 Analyzing {symbol}...")
    result = get_technical_analysis(symbol)
    
    if result:
        print(f"   Score: {result['score']}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Recent Growth: 1W={result['change_1w']:.1f}%, 2W={result['change_2w']:.1f}%, 1M={result['change_1m']:.1f}%")
        print(f"   Growth Potential: {result['growth_potential']:.1f}% (confidence: {result['growth_confidence']*100:.0f}%)")
        print(f"   Has Recent Growth (≥7%): {result['has_recent_growth']}")
        print(f"   Meets Growth Requirement: {result['meets_growth_requirement']}")
        
        if result['growth_factors']:
            print(f"   Growth Factors:")
            for factor in result['growth_factors'][:3]:
                print(f"      • {factor}")
    else:
        print(f"   ❌ Could not analyze")

print("\n" + "=" * 60)
print("✅ Test complete!")
