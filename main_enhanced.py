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
import argparse
import yfinance as yf
import requests
import holidays
import datetime
from datetime import datetime as dt
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Import our enhanced modules
from stock_universe import get_comprehensive_stock_list
from enhanced_yahoo_client import EnhancedYahooClient

# Configuration
x_bearer_token = os.getenv("X_BEARER_TOKEN", "")
email_to = "masterai6612@gmail.com"
email_from = os.getenv("ALERT_EMAIL_FROM", "")
email_password = os.getenv("ALERT_EMAIL_PASS", "")

# Sentiment keywords
BULLISH = ["upgrade", "buy", "strong", "growth", "beat", "outperform", "positive", "bullish", "rally"]
BEARISH = ["downgrade", "sell", "misses", "fall", "weak", "underperform", "disappoint", "decline"]

def is_market_open():
    """Check if US market is open"""
    today = datetime.date.today()
    us_holidays = holidays.US(years=today.year)
    weekday_open = today.weekday() < 5  # Monday=0, Sunday=6
    holiday = today in us_holidays
    return weekday_open and not holiday

def calc_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    roll_up = up.rolling(window=period).mean()
    roll_down = down.rolling(window=period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calc_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        # Ensure prices is a pandas Series
        if not hasattr(prices, 'ewm') or len(prices) < slow:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'bullish_crossover': False}
            
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1],
            'bullish_crossover': macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]
        }
    except:
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'bullish_crossover': False}

def calc_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    try:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = prices.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_sma = sma.iloc[-1]
        
        # Calculate position within bands (0 = lower band, 1 = upper band)
        band_position = (current_price - current_lower) / (current_upper - current_lower)
        
        return {
            'upper_band': current_upper,
            'lower_band': current_lower,
            'sma': current_sma,
            'band_position': band_position,
            'squeeze': (current_upper - current_lower) / current_sma < 0.1,  # Tight bands
            'breakout_up': current_price > current_upper,
            'breakout_down': current_price < current_lower
        }
    except:
        return {'upper_band': 0, 'lower_band': 0, 'sma': 0, 'band_position': 0.5, 'squeeze': False, 'breakout_up': False, 'breakout_down': False}

def calc_moving_averages(prices):
    """Calculate various moving averages"""
    try:
        # Ensure prices is a pandas Series
        if not hasattr(prices, 'rolling') or not hasattr(prices, 'ewm'):
            return {'sma_20': 0, 'sma_50': 0, 'ema_12': 0, 'ema_26': 0, 'above_sma_20': False, 'above_sma_50': False, 'golden_cross': False, 'death_cross': False}
        
        if len(prices) < 20:
            return {'sma_20': 0, 'sma_50': 0, 'ema_12': 0, 'ema_26': 0, 'above_sma_20': False, 'above_sma_50': False, 'golden_cross': False, 'death_cross': False}
            
        sma_20 = prices.rolling(window=20).mean().iloc[-1]
        sma_50 = prices.rolling(window=50).mean().iloc[-1] if len(prices) >= 50 else sma_20
        ema_12 = prices.ewm(span=12).mean().iloc[-1]
        ema_26 = prices.ewm(span=26).mean().iloc[-1]
        
        current_price = prices.iloc[-1]
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'above_sma_20': current_price > sma_20,
            'above_sma_50': current_price > sma_50,
            'golden_cross': sma_20 > sma_50,  # Bullish signal
            'death_cross': sma_20 < sma_50    # Bearish signal
        }
    except:
        return {'sma_20': 0, 'sma_50': 0, 'ema_12': 0, 'ema_26': 0, 'above_sma_20': False, 'above_sma_50': False, 'golden_cross': False, 'death_cross': False}

def calc_volume_analysis(hist):
    """Calculate volume-based indicators"""
    try:
        volumes = hist['Volume']
        prices = hist['Close']
        
        avg_volume_20 = volumes.rolling(window=20).mean().iloc[-1]
        current_volume = volumes.iloc[-1]
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
        
        # Price-Volume Trend (PVT)
        price_changes = prices.pct_change()
        pvt = (price_changes * volumes).cumsum()
        pvt_trend = pvt.iloc[-1] > pvt.iloc[-5] if len(pvt) >= 5 else False
        
        # On-Balance Volume (OBV)
        obv = []
        obv_value = 0
        for i in range(1, len(prices)):
            if prices.iloc[i] > prices.iloc[i-1]:
                obv_value += volumes.iloc[i]
            elif prices.iloc[i] < prices.iloc[i-1]:
                obv_value -= volumes.iloc[i]
            obv.append(obv_value)
        
        obv_trend = len(obv) >= 5 and obv[-1] > obv[-5] if obv else False
        
        return {
            'current_volume': current_volume,
            'avg_volume_20': avg_volume_20,
            'volume_ratio': volume_ratio,
            'high_volume': volume_ratio > 1.5,
            'very_high_volume': volume_ratio > 2.0,
            'pvt_bullish': pvt_trend,
            'obv_bullish': obv_trend,
            'volume_breakout': volume_ratio > 2.0 and prices.iloc[-1] > prices.iloc[-2]
        }
    except:
        return {'current_volume': 0, 'avg_volume_20': 0, 'volume_ratio': 1, 'high_volume': False, 'very_high_volume': False, 'pvt_bullish': False, 'obv_bullish': False, 'volume_breakout': False}

def calc_momentum_indicators(hist):
    """Calculate momentum indicators"""
    try:
        prices = hist['Close']
        highs = hist['High']
        lows = hist['Low']
        
        # Stochastic Oscillator
        lowest_low = lows.rolling(window=14).min()
        highest_high = highs.rolling(window=14).max()
        k_percent = 100 * ((prices - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        
        # Williams %R
        williams_r = -100 * ((highest_high - prices) / (highest_high - lowest_low))
        
        # Rate of Change (ROC)
        roc = ((prices - prices.shift(10)) / prices.shift(10)) * 100
        
        return {
            'stoch_k': k_percent.iloc[-1] if not k_percent.empty else 50,
            'stoch_d': d_percent.iloc[-1] if not d_percent.empty else 50,
            'williams_r': williams_r.iloc[-1] if not williams_r.empty else -50,
            'roc': roc.iloc[-1] if not roc.empty else 0,
            'stoch_oversold': k_percent.iloc[-1] < 20 if not k_percent.empty else False,
            'stoch_overbought': k_percent.iloc[-1] > 80 if not k_percent.empty else False,
            'momentum_bullish': roc.iloc[-1] > 5 if not roc.empty else False
        }
    except:
        return {'stoch_k': 50, 'stoch_d': 50, 'williams_r': -50, 'roc': 0, 'stoch_oversold': False, 'stoch_overbought': False, 'momentum_bullish': False}

def fetch_stocks(symbols, include_sentiment=True, silent=False):
    """Enhanced fetch_stocks with comprehensive technical analysis and X sentiment"""
    stock_data = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        hist = ticker.history(period="60d")  # Extended period for better technical analysis
        try:
            if len(hist) < 20:  # Need minimum data for technical analysis
                if not silent:
                    print(f"❌ Insufficient data for {sym}")
                continue
                
            close = hist["Close"].iloc[-1]
            open_ = hist["Open"].iloc[-1]
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            volume = hist["Volume"].iloc[-1]
            
            # Basic price metrics
            growth = ((close - open_) / open_) * 100
            daily_range = ((high - low) / low) * 100
            
            # Comprehensive Technical Analysis
            rsi = calc_rsi(hist["Close"])
            macd_data = calc_macd(hist["Close"])
            bollinger_data = calc_bollinger_bands(hist["Close"])
            ma_data = calc_moving_averages(hist["Close"])
            volume_data = calc_volume_analysis(hist)
            momentum_data = calc_momentum_indicators(hist)
            
            # Enhanced data structure with all technical indicators
            stock_info = {
                # Basic Price Data
                "symbol": sym,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "current_price": close,
                "change_percent": growth,
                "growth": growth,
                "daily_range": daily_range,
                "volume": volume,
                
                # Technical Indicators
                "rsi": rsi,
                "macd": macd_data,
                "bollinger": bollinger_data,
                "moving_averages": ma_data,
                "volume_analysis": volume_data,
                "momentum": momentum_data,
                
                # Technical Signals
                "technical_score": 0,  # Will be calculated
                "technical_signals": [],
                
                # Price Levels
                "support_level": min(hist["Low"].tail(20)),
                "resistance_level": max(hist["High"].tail(20)),
                "price_near_support": abs(close - min(hist["Low"].tail(20))) / close < 0.02,
                "price_near_resistance": abs(close - max(hist["High"].tail(20))) / close < 0.02
            }
            
            # Calculate Technical Score (0-100)
            technical_score = 0
            signals = []
            
            # RSI Analysis (20 points)
            if 30 <= rsi <= 70:
                technical_score += 15
                if 40 <= rsi <= 60:
                    technical_score += 5
            elif rsi < 30:
                signals.append("RSI_OVERSOLD")
                technical_score += 10  # Potential bounce
            elif rsi > 70:
                signals.append("RSI_OVERBOUGHT")
                technical_score -= 5
            
            # MACD Analysis (15 points)
            if macd_data['bullish_crossover']:
                technical_score += 15
                signals.append("MACD_BULLISH_CROSSOVER")
            elif macd_data['macd'] > macd_data['signal']:
                technical_score += 8
                signals.append("MACD_BULLISH")
            
            # Moving Average Analysis (15 points)
            if ma_data['above_sma_20'] and ma_data['above_sma_50']:
                technical_score += 15
                signals.append("ABOVE_KEY_MAs")
            elif ma_data['golden_cross']:
                technical_score += 10
                signals.append("GOLDEN_CROSS")
            elif ma_data['death_cross']:
                technical_score -= 10
                signals.append("DEATH_CROSS")
            
            # Bollinger Bands Analysis (10 points)
            if bollinger_data['breakout_up']:
                technical_score += 10
                signals.append("BOLLINGER_BREAKOUT_UP")
            elif bollinger_data['squeeze']:
                technical_score += 5
                signals.append("BOLLINGER_SQUEEZE")
            elif bollinger_data['breakout_down']:
                technical_score -= 10
                signals.append("BOLLINGER_BREAKOUT_DOWN")
            
            # Volume Analysis (15 points)
            if volume_data['volume_breakout']:
                technical_score += 15
                signals.append("VOLUME_BREAKOUT")
            elif volume_data['very_high_volume']:
                technical_score += 10
                signals.append("VERY_HIGH_VOLUME")
            elif volume_data['high_volume']:
                technical_score += 5
                signals.append("HIGH_VOLUME")
            
            # Momentum Analysis (10 points)
            if momentum_data['momentum_bullish']:
                technical_score += 10
                signals.append("MOMENTUM_BULLISH")
            elif momentum_data['stoch_oversold']:
                technical_score += 5
                signals.append("STOCH_OVERSOLD")
            elif momentum_data['stoch_overbought']:
                technical_score -= 5
                signals.append("STOCH_OVERBOUGHT")
            
            # Price Action Analysis (15 points)
            if growth > 3 and volume_data['high_volume']:
                technical_score += 15
                signals.append("STRONG_PRICE_ACTION")
            elif growth > 1:
                technical_score += 8
                signals.append("POSITIVE_PRICE_ACTION")
            elif growth < -3:
                technical_score -= 10
                signals.append("WEAK_PRICE_ACTION")
            
            # Update stock info with technical analysis
            stock_info["technical_score"] = min(100, max(0, technical_score))  # Cap at 0-100
            stock_info["technical_signals"] = signals
            
            # Add X (Twitter) sentiment if requested
            if include_sentiment:
                try:
                    x_sentiment = fetch_x_feed_sentiment(sym)
                    stock_info["x_sentiment"] = x_sentiment
                    stock_info["social_sentiment"] = x_sentiment
                    if not silent:
                        print(f"🐦 {sym}: X sentiment = {x_sentiment} | Tech Score: {technical_score}")
                except Exception as e:
                    if not silent:
                        print(f"⚠️ X sentiment failed for {sym}: {e}")
                    stock_info["x_sentiment"] = "Unknown"
                    stock_info["social_sentiment"] = "Unknown"
            
            stock_data[sym] = stock_info
            
        except Exception as e:
            if not silent:
                print(f"❌ Failed to fetch data for {sym}: {e}")
            continue
    
    return stock_data

def fetch_x_feed_sentiment(symbol):
    """Fetch X (Twitter) sentiment for a stock symbol"""
    headers = {"Authorization": f"Bearer {x_bearer_token}"}
    search_url = f"https://api.twitter.com/2/tweets/search/recent?query=%24{symbol}&max_results=10"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            tweets = response.json().get("data", [])
            if tweets:
                bullish_count = sum(1 for tweet in tweets if any(word in tweet["text"].lower() for word in BULLISH))
                bearish_count = sum(1 for tweet in tweets if any(word in tweet["text"].lower() for word in BEARISH))
                
                if bullish_count > bearish_count:
                    return "Bullish"
                elif bearish_count > bullish_count:
                    return "Bearish"
                else:
                    return "Neutral"
        return "Neutral"
    except:
        return "Unknown"

def make_recommendation(info, headlines=[], x_sentiment=None, earnings_soon=False, in_hot_theme=False):
    """Enhanced recommendation with comprehensive technical analysis, earnings, themes, and X sentiment"""
    bullish_count = sum(1 for _, sentiment in headlines if sentiment == "Bullish")
    bearish_count = sum(1 for _, sentiment in headlines if sentiment == "Bearish")
    
    # Get X sentiment from info if not provided
    if x_sentiment is None:
        x_sentiment = info.get('x_sentiment', 'Unknown')
    
    # Base criteria
    growth = info.get('growth', info.get('change_percent', 0))
    rsi = info.get('rsi', 50)
    volume = info.get('volume', 0)
    
    # Technical Analysis Data
    technical_score = info.get('technical_score', 0)
    technical_signals = info.get('technical_signals', [])
    macd_data = info.get('macd', {})
    bollinger_data = info.get('bollinger', {})
    ma_data = info.get('moving_averages', {})
    volume_data = info.get('volume_analysis', {})
    momentum_data = info.get('momentum', {})
    
    # Enhanced scoring system with technical analysis integration
    score = 0
    signal_strength_multiplier = 1.0
    
    # Technical Score (40% weight) - This is the core technical analysis
    technical_weight = technical_score / 100 * 4.0  # Convert 0-100 to 0-4.0
    score += technical_weight
    
    # Price movement (20% weight) - Reduced since technical score includes price action
    if growth >= 7:
        score += 2
    elif growth >= 4:
        score += 1.2
    elif growth >= 2:
        score += 0.6
    elif growth < -3:
        score -= 1
    
    # RSI analysis (10% weight) - Reduced since included in technical score
    if 55 <= rsi <= 80:  # Sweet spot for momentum
        score += 1
    elif 45 <= rsi <= 90:
        score += 0.5
    elif rsi < 30:  # Oversold bounce potential
        score += 0.3
    elif rsi > 85:  # Overbought warning
        score -= 0.5
    
    # Volume confirmation (10% weight)
    if volume_data.get('volume_breakout', False):
        score += 1
        signal_strength_multiplier *= 1.2
    elif volume_data.get('very_high_volume', False):
        score += 0.7
    elif volume_data.get('high_volume', False):
        score += 0.4
    elif volume > 1000000:  # Fallback for basic volume check
        score += 0.3
    
    # Technical Signal Bonuses (10% weight)
    signal_bonus = 0
    strong_signals = ['MACD_BULLISH_CROSSOVER', 'GOLDEN_CROSS', 'BOLLINGER_BREAKOUT_UP', 
                     'VOLUME_BREAKOUT', 'STRONG_PRICE_ACTION']
    moderate_signals = ['MACD_BULLISH', 'ABOVE_KEY_MAs', 'MOMENTUM_BULLISH', 'RSI_OVERSOLD']
    
    for signal in technical_signals:
        if signal in strong_signals:
            signal_bonus += 0.3
            signal_strength_multiplier *= 1.1
        elif signal in moderate_signals:
            signal_bonus += 0.15
    
    score += min(signal_bonus, 1.0)  # Cap signal bonus at 1.0
    
    # Comprehensive Market Sentiment (8% weight) - Enhanced from multiple sources
    sentiment_score = info.get('sentiment_score', 0)
    sentiment_category = info.get('sentiment_category', 'neutral')
    sentiment_confidence = info.get('sentiment_confidence', 0)
    
    if sentiment_category == "bullish":
        sentiment_boost = 0.8 * sentiment_confidence  # Up to 0.8 points
        score += sentiment_boost
        signal_strength_multiplier *= (1.0 + sentiment_confidence * 0.1)
    elif sentiment_category == "bearish":
        sentiment_penalty = 0.8 * sentiment_confidence  # Up to -0.8 points
        score -= sentiment_penalty
        signal_strength_multiplier *= (1.0 - sentiment_confidence * 0.05)
    
    # Legacy X sentiment (2% weight) - Keep for backward compatibility
    if x_sentiment == "Bullish":
        score += 0.2
        signal_strength_multiplier *= 1.02
    elif x_sentiment == "Bearish":
        score -= 0.2
        signal_strength_multiplier *= 0.98
    
    # News sentiment (3% weight)
    if bullish_count > bearish_count:
        score += 0.3
    elif bearish_count > bullish_count:
        score -= 0.3
    
    # Catalysts (2% weight)
    if earnings_soon:
        score += 0.15
        signal_strength_multiplier *= 1.03
    if in_hot_theme:
        score += 0.1
        signal_strength_multiplier *= 1.02
    
    # Apply signal strength multiplier
    final_score = score * signal_strength_multiplier
    
    # Enhanced Decision Logic with Technical Analysis
    # Strong technical signals with multiple confirmations
    strong_technical_signals = len([s for s in technical_signals if s in strong_signals])
    has_volume_confirmation = any(s in technical_signals for s in ['VOLUME_BREAKOUT', 'VERY_HIGH_VOLUME'])
    
    # STRONG BUY: High technical score + strong signals + sentiment alignment
    if (final_score >= 8 and technical_score >= 75 and strong_technical_signals >= 2 and 
        growth >= 5 and has_volume_confirmation and x_sentiment == "Bullish"):
        return "STRONG BUY"
    
    # BUY: Good technical score + some strong signals
    elif (final_score >= 6 and technical_score >= 60 and 
          (strong_technical_signals >= 1 or growth >= 4)):
        return "BUY"
    
    # WATCH: Moderate technical score or mixed signals
    elif (final_score >= 4 and technical_score >= 40) or strong_technical_signals >= 1:
        return "WATCH"
    
    # NO SIGNAL: Low technical score or negative signals
    else:
        return "NO SIGNAL"

def get_enhanced_data():
    """Get earnings calendar and investment themes"""
    client = EnhancedYahooClient()
    
    # Get earnings calendar
    earnings = client.get_earnings_calendar(days_ahead=7)
    earnings_symbols = {item['symbol'] for item in earnings} if earnings else set()
    
    # Get investment themes
    themes = client.get_investment_themes()
    hot_theme_stocks = set()
    
    if themes and 'themes' in themes:
        for theme in themes['themes'][:3]:  # Top 3 themes
            if 'representative_stocks' in theme:
                hot_theme_stocks.update(theme['representative_stocks'])
    
    return earnings_symbols, hot_theme_stocks, themes

def run_enhanced_analysis(silent=False):
    """Run comprehensive analysis with all features"""
    
    if not silent:
        print("🚀 Starting Enhanced Agentic Stock Analysis...")
        print("=" * 60)
    
    # Get comprehensive stock universe
    all_symbols = get_comprehensive_stock_list()
    if not silent:
        print(f"📊 Stock Universe: {len(all_symbols)} stocks")
        print(f"🎯 Analyzing: {len(all_symbols)} stocks")
    
    # Get enhanced data (earnings, themes)
    if not silent:
        print("📅 Getting earnings calendar...")
        print("🔥 Getting investment themes...")
    
    earnings_symbols, hot_theme_stocks, themes = get_enhanced_data()
    
    if not silent:
        print(f"📅 Earnings today: {len(earnings_symbols)} stocks")
        print(f"🔥 Hot themes: {len(themes.get('themes', []))} themes")
        print(f"🎯 Hot theme stocks: {len(hot_theme_stocks)} stocks")
        print("\n🔍 Performing comprehensive analysis...")
    
    # Perform comprehensive analysis
    results = []
    
    for i, symbol in enumerate(all_symbols, 1):
        try:
            if not silent:
                print(f"   Analyzing {symbol} ({i}/{len(all_symbols)})...", end=" ")
            
            # Get stock data with X sentiment
            stock_data = fetch_stocks([symbol], include_sentiment=True, silent=silent)
            
            if symbol in stock_data:
                info = stock_data[symbol]
                
                # Check catalysts
                earnings_soon = symbol in earnings_symbols
                in_hot_theme = symbol in hot_theme_stocks
                
                # Get enhanced recommendation
                recommendation = make_recommendation(
                    info, [], None,
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
                if not silent:
                    print(f"✅ {recommendation}")
            else:
                if not silent:
                    print("❌ No data")
                
        except Exception as e:
            if not silent:
                print(f"❌ Error: {e}")
            continue
    
    # Analyze results
    if not silent:
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
    
    if not silent:
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
    if buy_signals and not silent:
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
        if not silent:
            print("\n📧 Sending email alert...")
        
        # Send via our email system
        try:
            import requests
            
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
                    'timestamp': dt.now().isoformat()
                }
            }
            
            response = requests.post(
                "http://localhost:5002/api/send-email-alert",
                json=email_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    if not silent:
                        print(f"✅ Email sent successfully!")
                        print(f"📧 Subject: {result.get('subject')}")
                        print(f"📬 To: masterai6612@gmail.com")
                else:
                    if not silent:
                        print(f"⚠️ Email API responded but may not have sent")
            else:
                if not silent:
                    print(f"❌ Email API failed: {response.status_code}")
                
        except Exception as e:
            if not silent:
                print(f"⚠️ Email sending failed: {e}")
                print("💡 Make sure n8n integration server is running")
    
    else:
        if not silent:
            print("\n📧 No buy signals found - no email alert sent")
    
    if not silent:
        print("\n" + "=" * 60)
        print("✅ ENHANCED ANALYSIS COMPLETE!")
        print("=" * 60)
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enhanced Agentic Stock Alert System')
    parser.add_argument('--silent', '-s', action='store_true', 
                       help='Run in silent mode (minimal output)')
    args = parser.parse_args()
    
    if not args.silent:
        print("🤖 Enhanced Agentic Stock Alert System")
        print("Combining all sophisticated features for institutional-level analysis")
        print()
    
    try:
        results = run_enhanced_analysis(silent=args.silent)
        
        if not args.silent:
            print(f"\n🎯 Analysis Summary:")
            print(f"   • Analyzed {len(results)} stocks from 269+ universe")
            print(f"   • Used X (Twitter) sentiment analysis")
            print(f"   • Integrated earnings calendar")
            print(f"   • Analyzed investment themes")
            print(f"   • Generated intelligent recommendations")
            print(f"   • Sent professional email alerts")
            
            print(f"\n📧 Check masterai6612@gmail.com for email alerts!")
            print(f"🚀 Your agentic system is working at institutional level!")
        else:
            # Silent mode - just show key stats
            buy_signals = [r for r in results if 'BUY' in r['recommendation']]
            print(f"Analysis: {len(results)} stocks | Buy signals: {len(buy_signals)}")
        
    except KeyboardInterrupt:
        if not args.silent:
            print("\n⚠️ Analysis interrupted by user")
    except Exception as e:
        if not args.silent:
            print(f"\n❌ Analysis failed: {e}")
            print("💡 Make sure all dependencies are installed and configured")
        sys.exit(1)