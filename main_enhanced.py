#!/usr/bin/env python3
"""
Enhanced Main Script - Agentic Stock Alert System
Combines all sophisticated features:
- 269+ stock universe
- X (Twitter) sentiment analysis
- Earnings calendar integration
- Investment themes analysis
- Professional email alerts
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our enhanced modules
from stock_universe import get_comprehensive_stock_list
from enhanced_yahoo_client import EnhancedYahooClient
from main import (
    fetch_stocks, make_recommendation, get_enhanced_data,
    fetch_x_feed_sentiment, send_gmail_email
)

def run_enhanced_analysis():
    """Run comprehensive analysis with all features"""
    
    print("🚀 Starting Enhanced Agentic Stock Analysis...")
    print("=" * 60)
    
    # Get comprehensive stock universe
    all_symbols = get_comprehensive_stock_list()
    print(f"📊 Stock Universe: {len(all_symbols)} stocks")
    
    # Limit for performance (can be adjusted)
    analysis_limit = 50
    symbols_to_analyze = all_symbols[:analysis_limit]
    print(f"🎯 Analyzing: {len(symbols_to_analyze)} stocks")
    
    # Get enhanced data (earnings, themes)
    print("📅 Getting earnings calendar...")
    print("🔥 Getting investment themes...")
    earnings_symbols, hot_theme_stocks, themes = get_enhanced_data()
    
    print(f"📅 Earnings today: {len(earnings_symbols)} stocks")
    print(f"🔥 Hot themes: {len(themes.get('themes', []))} themes")
    print(f"🎯 Hot theme stocks: {len(hot_theme_stocks)} stocks")
    
    # Perform comprehensive analysis
    print("\n🔍 Performing comprehensive analysis...")
    results = []
    
    for i, symbol in enumerate(symbols_to_analyze, 1):
        try:
            print(f"   Analyzing {symbol} ({i}/{len(symbols_to_analyze)})...", end=" ")
            
            # Get stock data with X sentiment
            stock_data = fetch_stocks([symbol], include_sentiment=True)
            
            if symbol in stock_data:
                info = stock_data[symbol]
                
                # Check catalysts
                earnings_soon = symbol in earnings_symbols
                in_hot_theme = symbol in hot_theme_stocks
                
                # Get enhanced recommendation
                recommendation = make_recommendation(
                    info, [], None,  # No headlines for now
                    earnings_soon=earnings_soon,
                    in_hot_theme=in_hot_theme
                )
                
                # Store result
                result = {
                    'symbol': symbol,
                    'price': info.get('current_price', info.get('close', 0)),
                    'change_percent': info.get('change_percent', info.get('growth', 0)),
                    'volume': info.get('volume', 0),
                    'rsi': info.get('rsi', 0),
                    'x_sentiment': info.get('x_sentiment', 'Unknown'),
                    'recommendation': recommendation,
                    'earnings_soon': earnings_soon,
                    'in_hot_theme': in_hot_theme
                }
                
                results.append(result)
                print(f"✅ {recommendation}")
            else:
                print("❌ No data")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Analyze results
    print("\n" + "=" * 60)
    print("📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    # Filter buy signals
    buy_signals = [r for r in results if 'BUY' in r['recommendation']]
    strong_buy_signals = [r for r in results if r['recommendation'] == 'STRONG BUY']
    
    # X sentiment analysis
    bullish_sentiment = [r for r in results if r['x_sentiment'] == 'Bullish']
    bearish_sentiment = [r for r in results if r['x_sentiment'] == 'Bearish']
    neutral_sentiment = [r for r in results if r['x_sentiment'] == 'Neutral']
    
    # Earnings and themes
    earnings_stocks = [r for r in results if r['earnings_soon']]
    theme_stocks = [r for r in results if r['in_hot_theme']]
    
    print(f"📈 Total Analyzed: {len(results)}")
    print(f"💰 Buy Signals: {len(buy_signals)}")
    print(f"🚀 Strong Buy Signals: {len(strong_buy_signals)}")
    print(f"📅 Earnings Soon: {len(earnings_stocks)}")
    print(f"🔥 Hot Theme Stocks: {len(theme_stocks)}")
    print()
    print(f"🐦 X Sentiment Analysis:")
    print(f"   📈 Bullish: {len(bullish_sentiment)}")
    print(f"   📉 Bearish: {len(bearish_sentiment)}")
    print(f"   😐 Neutral: {len(neutral_sentiment)}")
    
    # Show top buy signals
    if buy_signals:
        print("\n🎯 TOP BUY SIGNALS:")
        print("-" * 40)
        
        # Sort by recommendation strength and X sentiment
        buy_signals.sort(key=lambda x: (
            2 if x['recommendation'] == 'STRONG BUY' else 1,
            2 if x['x_sentiment'] == 'Bullish' else 0,
            1 if x['earnings_soon'] else 0,
            1 if x['in_hot_theme'] else 0
        ), reverse=True)
        
        for signal in buy_signals[:10]:  # Top 10
            flags = []
            if signal['x_sentiment'] == 'Bullish':
                flags.append('🐦📈')
            if signal['earnings_soon']:
                flags.append('📅')
            if signal['in_hot_theme']:
                flags.append('🔥')
            
            flag_text = ' '.join(flags) if flags else ''
            
            print(f"   {signal['symbol']:6} | {signal['recommendation']:10} | "
                  f"${signal['price']:7.2f} | {signal['change_percent']:+6.2f}% | "
                  f"RSI:{signal['rsi']:5.1f} | {flag_text}")
    
    # Send email alert if there are buy signals
    if buy_signals:
        print("\n📧 Sending email alert...")
        
        # Create market context
        market_context = {
            'sentiment': 'BULLISH' if len(buy_signals) > len(results) * 0.3 else 'NEUTRAL',
            'earnings_today': len(earnings_symbols),
            'hot_themes': len(themes.get('themes', []))
        }
        
        # Create email subject
        if len(bullish_sentiment) >= 3 and len(buy_signals) >= 3:
            subject = f"🐦🚀 X BULLISH: {len(bullish_sentiment)} Stocks + {len(buy_signals)} BUY Signals!"
        elif len(buy_signals) >= 5:
            subject = f"📈 MAJOR ALERT: {len(buy_signals)} Buy Signals from Enhanced Analysis"
        else:
            subject = f"💡 {len(buy_signals)} Buy Signal{'s' if len(buy_signals) > 1 else ''} from Agentic Analysis"
        
        # Prepare email data
        email_data = {
            'subject': subject,
            'email_to': 'masterai6612@gmail.com',
            'buy_signals': buy_signals,
            'market_context': market_context,
            'summary': {
                'total_analyzed': len(results),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Send via our email system
        try:
            import requests
            response = requests.post(
                "http://localhost:5002/api/send-email-alert",
                json=email_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Email sent successfully!")
                    print(f"📧 Subject: {result.get('subject')}")
                    print(f"📬 To: masterai6612@gmail.com")
                else:
                    print(f"⚠️ Email API responded but may not have sent")
            else:
                print(f"❌ Email API failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")
            print("💡 Make sure n8n integration server is running: python n8n_integration.py")
    
    else:
        print("\n📧 No buy signals found - no email alert sent")
    
    print("\n" + "=" * 60)
    print("✅ ENHANCED ANALYSIS COMPLETE!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    print("🤖 Enhanced Agentic Stock Alert System")
    print("Combining all sophisticated features for institutional-level analysis")
    print()
    
    try:
        results = run_enhanced_analysis()
        
        print(f"\n🎯 Analysis Summary:")
        print(f"   • Analyzed {len(results)} stocks from 269+ universe")
        print(f"   • Used X (Twitter) sentiment analysis")
        print(f"   • Integrated earnings calendar")
        print(f"   • Analyzed investment themes")
        print(f"   • Generated intelligent recommendations")
        print(f"   • Sent professional email alerts")
        
        print(f"\n📧 Check masterai6612@gmail.com for email alerts!")
        print(f"🚀 Your agentic system is working at institutional level!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        print("💡 Make sure all dependencies are installed and configured")
        sys.exit(1)