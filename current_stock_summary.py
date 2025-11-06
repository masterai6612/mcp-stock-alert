#!/usr/bin/env python3
"""
Current Stock Summary - US and Canadian Markets
Generate comprehensive BUY/SELL recommendations
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email and Telegram settings
EMAIL_TO = "masterai6612@gmail.com"
EMAIL_FROM = os.getenv('EMAIL_FROM', 'masterai6612@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_technical_analysis(symbol):
    """Get comprehensive technical analysis with BUY/SELL signals"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        info = ticker.info
        
        # Skip if no data (delisted or invalid symbol)
        if hist.empty or len(hist) < 20:
            return None
        
        # Skip if current price is too low (penny stocks or delisted)
        current_price = hist['Close'].iloc[-1]
        if current_price < 1.0:
            return None
        
        close = hist['Close']
        volume = hist['Volume']
        high = hist['High']
        low = hist['Low']
        
        # Enhanced Technical Indicators
        current_price = close.iloc[-1]
        
        # Moving Averages
        ma_5 = close.rolling(window=5).mean().iloc[-1]
        ma_10 = close.rolling(window=10).mean().iloc[-1]
        ma_20 = close.rolling(window=20).mean().iloc[-1]
        ma_50 = close.rolling(window=50).mean().iloc[-1]
        ma_200 = close.rolling(window=min(200, len(close))).mean().iloc[-1]
        
        # RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD (Moving Average Convergence Divergence)
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd_line = exp1 - exp2
        macd = macd_line.iloc[-1]
        signal_line = macd_line.ewm(span=9).mean().iloc[-1]
        macd_histogram = macd - signal_line
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        bb_ma = close.rolling(window=bb_period).mean()
        bb_std_dev = close.rolling(window=bb_period).std()
        bb_upper = (bb_ma + (bb_std_dev * bb_std)).iloc[-1]
        bb_lower = (bb_ma - (bb_std_dev * bb_std)).iloc[-1]
        bb_width = ((bb_upper - bb_lower) / bb_ma.iloc[-1]) * 100
        bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100
        
        # Stochastic Oscillator
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        stoch_k = k_percent.rolling(window=3).mean().iloc[-1]
        stoch_d = k_percent.rolling(window=3).mean().rolling(window=3).mean().iloc[-1]
        
        # Williams %R
        williams_r = -100 * ((highest_high.iloc[-1] - current_price) / (highest_high.iloc[-1] - lowest_low.iloc[-1]))
        
        # Average True Range (ATR) for volatility
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[-1]
        atr_percent = (atr / current_price) * 100
        
        # Volume analysis
        avg_volume = volume.tail(20).mean()
        recent_volume = volume.iloc[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # On-Balance Volume (OBV)
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        obv_trend = obv.iloc[-1] - obv.iloc[-10] if len(obv) > 10 else 0
        
        # Price Performance Analysis
        price_1d = ((current_price - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
        price_3d = ((current_price - close.iloc[-4]) / close.iloc[-4]) * 100 if len(close) > 3 else 0
        price_5d = ((current_price - close.iloc[-6]) / close.iloc[-6]) * 100 if len(close) > 5 else 0
        price_1w = ((current_price - close.iloc[-8]) / close.iloc[-8]) * 100 if len(close) > 7 else 0
        price_2w = ((current_price - close.iloc[-15]) / close.iloc[-15]) * 100 if len(close) > 14 else 0
        price_1m = ((current_price - close.iloc[-21]) / close.iloc[-21]) * 100 if len(close) > 20 else 0
        price_3m = ((current_price - close.iloc[0]) / close.iloc[0]) * 100 if len(close) > 0 else 0
        
        # Support and Resistance levels
        recent_high = high.tail(20).max()
        recent_low = low.tail(20).min()
        resistance_distance = ((recent_high - current_price) / current_price) * 100
        support_distance = ((current_price - recent_low) / current_price) * 100
        
        # Enhanced Scoring System for BUY/SELL signals
        score = 0
        signals = []
        buy_reasons = []
        sell_reasons = []
        
        # 1. MOMENTUM ANALYSIS (5% gain/loss logic)
        if price_1d >= 5.0:
            score += 4
            buy_reasons.append(f"Strong daily momentum +{price_1d:.1f}%")
            signals.append(f"🚀 Daily surge +{price_1d:.1f}%")
        elif price_1d <= -5.0:
            score -= 4
            sell_reasons.append(f"Weak daily momentum {price_1d:.1f}%")
            signals.append(f"📉 Daily drop {price_1d:.1f}%")
        elif price_1d > 2.0:
            score += 2
            signals.append(f"📈 Daily gain +{price_1d:.1f}%")
        elif price_1d < -2.0:
            score -= 2
            signals.append(f"📉 Daily loss {price_1d:.1f}%")
        
        if price_5d >= 10.0:
            score += 3
            buy_reasons.append(f"Strong 5-day trend +{price_5d:.1f}%")
        elif price_5d <= -10.0:
            score -= 3
            sell_reasons.append(f"Weak 5-day trend {price_5d:.1f}%")
        
        if price_1w >= 7.0:
            score += 2
            buy_reasons.append(f"Weekly momentum +{price_1w:.1f}%")
        elif price_1w <= -7.0:
            score -= 2
            sell_reasons.append(f"Weekly decline {price_1w:.1f}%")
        
        # 2. MOVING AVERAGE ANALYSIS
        ma_score = 0
        if current_price > ma_5 > ma_10 > ma_20 > ma_50:
            ma_score += 5
            buy_reasons.append("Perfect MA alignment (bullish)")
            signals.append("🎯 Perfect MA stack")
        elif current_price > ma_20 > ma_50:
            ma_score += 3
            signals.append("📈 Above key MAs")
        elif current_price > ma_20:
            ma_score += 2
            signals.append("Above 20-day MA")
        elif current_price < ma_20:
            ma_score -= 2
            signals.append("Below 20-day MA")
        
        if current_price > ma_200:
            ma_score += 1
            signals.append("Above 200-day MA")
        else:
            ma_score -= 1
            sell_reasons.append("Below 200-day MA (bearish)")
        
        score += ma_score
        
        # 3. RSI ANALYSIS (Enhanced)
        if rsi < 20:
            score += 5
            buy_reasons.append(f"Extremely oversold RSI {rsi:.1f}")
            signals.append(f"🔥 RSI oversold {rsi:.1f}")
        elif rsi < 30:
            score += 3
            buy_reasons.append(f"Oversold RSI {rsi:.1f}")
            signals.append(f"📈 RSI oversold {rsi:.1f}")
        elif 30 <= rsi <= 45:
            score += 2
            signals.append(f"RSI healthy {rsi:.1f}")
        elif 45 < rsi <= 55:
            score += 1
            signals.append(f"RSI neutral {rsi:.1f}")
        elif 55 < rsi <= 70:
            score += 0
            signals.append(f"RSI moderate {rsi:.1f}")
        elif 70 < rsi <= 80:
            score -= 2
            sell_reasons.append(f"Overbought RSI {rsi:.1f}")
            signals.append(f"⚠️ RSI overbought {rsi:.1f}")
        elif rsi > 80:
            score -= 4
            sell_reasons.append(f"Extremely overbought RSI {rsi:.1f}")
            signals.append(f"🔴 RSI extreme {rsi:.1f}")
        
        # 4. MACD ANALYSIS
        if macd > signal_line and macd_histogram > 0:
            score += 3
            buy_reasons.append("MACD bullish crossover")
            signals.append("🚀 MACD bullish")
        elif macd > signal_line:
            score += 2
            signals.append("MACD above signal")
        elif macd < signal_line and macd_histogram < 0:
            score -= 2
            sell_reasons.append("MACD bearish crossover")
            signals.append("📉 MACD bearish")
        
        # 5. BOLLINGER BANDS ANALYSIS
        if bb_position < 10:  # Near lower band
            score += 3
            buy_reasons.append("Near Bollinger lower band")
            signals.append("🎯 BB oversold")
        elif bb_position > 90:  # Near upper band
            score -= 3
            sell_reasons.append("Near Bollinger upper band")
            signals.append("⚠️ BB overbought")
        elif bb_width < 10:  # Squeeze
            score += 1
            signals.append("BB squeeze (breakout pending)")
        
        # 6. STOCHASTIC OSCILLATOR
        if stoch_k < 20 and stoch_d < 20:
            score += 2
            buy_reasons.append("Stochastic oversold")
            signals.append("📈 Stoch oversold")
        elif stoch_k > 80 and stoch_d > 80:
            score -= 2
            sell_reasons.append("Stochastic overbought")
            signals.append("📉 Stoch overbought")
        
        # 7. WILLIAMS %R
        if williams_r < -80:
            score += 2
            buy_reasons.append("Williams %R oversold")
        elif williams_r > -20:
            score -= 2
            sell_reasons.append("Williams %R overbought")
        
        # 8. VOLUME ANALYSIS
        if volume_ratio > 2.0:
            score += 2
            signals.append(f"🔊 High volume {volume_ratio:.1f}x")
        elif volume_ratio > 1.5:
            score += 1
            signals.append(f"Volume above avg {volume_ratio:.1f}x")
        elif volume_ratio < 0.5:
            score -= 1
            signals.append(f"Low volume {volume_ratio:.1f}x")
        
        # 9. VOLATILITY ANALYSIS (ATR)
        if atr_percent > 5.0:
            score -= 1
            signals.append(f"High volatility {atr_percent:.1f}%")
        elif atr_percent < 1.0:
            score += 1
            signals.append(f"Low volatility {atr_percent:.1f}%")
        
        # 10. SUPPORT/RESISTANCE ANALYSIS
        if support_distance > 10:
            score += 1
            signals.append("Strong support level")
        elif resistance_distance < 5:
            score -= 1
            signals.append("Near resistance")
        
        # 11. TREND STRENGTH
        if price_1m > 20:
            score += 2
            buy_reasons.append(f"Strong monthly trend +{price_1m:.1f}%")
        elif price_1m < -20:
            score -= 2
            sell_reasons.append(f"Weak monthly trend {price_1m:.1f}%")
        
        # 12. GOLDEN/DEATH CROSS
        if ma_50 > ma_200 and (ma_50 - ma_200) / ma_200 > 0.02:  # Golden cross
            score += 2
            buy_reasons.append("Golden cross formation")
            signals.append("✨ Golden cross")
        elif ma_50 < ma_200 and (ma_200 - ma_50) / ma_200 > 0.02:  # Death cross
            score -= 2
            sell_reasons.append("Death cross formation")
            signals.append("💀 Death cross")
        
        # Determine recommendation
        if score >= 8:
            recommendation = "STRONG BUY"
        elif score >= 5:
            recommendation = "BUY"
        elif score >= 2:
            recommendation = "WEAK BUY"
        elif score >= -2:
            recommendation = "HOLD"
        elif score >= -5:
            recommendation = "WEAK SELL"
        elif score >= -8:
            recommendation = "SELL"
        else:
            recommendation = "STRONG SELL"
        
        return {
            'symbol': symbol,
            'company_name': info.get('longName', symbol),
            'current_price': current_price,
            'change_1d': price_1d,
            'change_3d': price_3d,
            'change_5d': price_5d,
            'change_1w': price_1w,
            'change_2w': price_2w,
            'change_1m': price_1m,
            'change_3m': price_3m,
            'volume': recent_volume,
            'volume_ratio': volume_ratio,
            'avg_volume': avg_volume,
            'rsi': rsi,
            'ma_5': ma_5,
            'ma_10': ma_10,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'macd': macd,
            'macd_signal': signal_line,
            'macd_histogram': macd_histogram,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_position': bb_position,
            'bb_width': bb_width,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'williams_r': williams_r,
            'atr': atr,
            'atr_percent': atr_percent,
            'obv_trend': obv_trend,
            'support_distance': support_distance,
            'resistance_distance': resistance_distance,
            'recent_high': recent_high,
            'recent_low': recent_low,
            'score': score,
            'recommendation': recommendation,
            'signals': signals,
            'buy_reasons': buy_reasons,
            'sell_reasons': sell_reasons,
            'market_cap': info.get('marketCap', 0),
            'sector': info.get('sector', 'Unknown'),
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'price_to_book': info.get('priceToBook', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def filter_active_stocks(stock_list):
    """Filter out delisted or inactive stocks"""
    active_stocks = []
    delisted_keywords = ['delisted', 'not found', 'invalid', 'suspended']
    
    for symbol in stock_list:
        # Skip known problematic symbols
        skip_symbols = [
            'DFS', 'ANSS', 'WISH', 'C3AI', 'TWTR', 'SQ', 'ATLASSIAN', 'ATVI',
            'EXPR', 'NAKD', 'ASTR', 'MAXR', 'HEXO', 'PARA', 'ABX', 'GOLD',
            'ERF.TO', 'KL.TO', 'FCU.TO', 'TFI.TO', 'PWF.TO', 'NVEI.TO', 
            'NUVEI.TO', 'CRH.TO', 'PHM.TO', 'BBBY'
        ]
        
        if symbol not in skip_symbols:
            active_stocks.append(symbol)
    
    return active_stocks

def analyze_stock_universe():
    """Analyze comprehensive stock universe - ALL active stocks"""
    print("🔍 Analyzing FULL comprehensive stock universe...")
    
    # Import the complete stock universe
    try:
        from stock_universe import get_comprehensive_stock_list, SP500_LARGE_CAPS, RECENT_IPOS_AND_GROWTH, TRENDING_STOCKS, CANADIAN_LARGE_CAPS
        
        # Get all stocks from our comprehensive universe
        all_stocks = get_comprehensive_stock_list()
        
        # Filter out delisted stocks
        all_stocks = filter_active_stocks(all_stocks)
        
        # Separate US and Canadian stocks
        us_stocks = []
        canadian_stocks = []
        
        for symbol in all_stocks:
            if symbol.endswith('.TO') or symbol.endswith('.V') or symbol.endswith('.CN'):
                canadian_stocks.append(symbol)
            else:
                us_stocks.append(symbol)
        
        print(f"📊 Active universe loaded: {len(all_stocks)} total stocks")
        print(f"   🇺🇸 US stocks: {len(us_stocks)}")
        print(f"   🇨🇦 Canadian stocks: {len(canadian_stocks)}")
        
    except ImportError:
        print("⚠️ Could not import stock_universe, using curated lists...")
        
        # Comprehensive US stocks - cleaned and updated
        us_stocks = [
            # NASDAQ Mega Caps
            "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
            "AVGO", "COST", "NFLX", "ADBE", "PEP", "CSCO", "CMCSA", "INTC",
            "AMD", "QCOM", "TXN", "INTU", "ISRG", "BKNG", "AMGN", "HON",
            "VRTX", "ADI", "GILD", "LRCX", "REGN", "MRVL", "KLAC", "AMAT",
            "MDLZ", "SBUX", "ADP", "PYPL", "ABNB", "PCAR", "ORLY", "DXCM",
            "CTAS", "FAST", "PAYX", "ROST", "ODFL", "VRSK", "KMB", "CTSH",
            "LULU", "CHTR", "MCHP", "NXPI", "CPRT", "WDAY", "TEAM", "ADSK",
            "GRMN", "CRWD", "FTNT", "PANW", "SNOW", "ZS", "DDOG", "NET",
            "OKTA", "SPLK", "MDB", "DOCU", "ZM", "ROKU", "PINS", "SNAP",
            
            # S&P 500 Large Caps (NYSE)
            "BRK-B", "LLY", "JPM", "UNH", "XOM", "V", "PG", "JNJ", "MA", "HD",
            "CVX", "ABBV", "BAC", "CRM", "KO", "ASML", "TMO", "MRK", "WMT",
            "ACN", "LIN", "ABT", "DHR", "VZ", "SPGI", "CAT", "NOW", "PFE",
            "GE", "AXP", "T", "NEE", "IBM", "LOW", "SYK", "UBER", "PGR",
            "RTX", "ELV", "BSX", "MDT", "C", "SCHW", "AMT", "DE", "BLK",
            "TMUS", "CVS", "FI", "CB", "SO", "WM", "EQIX", "DUK", "ZTS",
            "ITW", "AON", "CL", "APD", "CMG", "MMC", "ICE", "PLD", "FCX",
            "USB", "PNC", "SHW", "EMR", "GD", "TJX", "MCO", "NSC", "BDX",
            "ECL", "MSI", "TGT", "COF", "ROP", "CARR", "NUE", "AJG", "CME",
            "TRV", "EA", "F", "GM", "LMT", "BA", "UPS", "FDX", "MMM", "GS",
            "MS", "WFC", "SPY", "QQQ", "IWM", "DIA",
            
            # Recent IPOs and Growth (Active)
            "RIVN", "LCID", "RBLX", "COIN", "HOOD", "SOFI", "AFRM", "UPST",
            "OPEN", "SPCE", "PLTR", "AI", "DDOG", "ZM", "PTON", "LYFT", "DASH",
            
            # High-growth Tech (NASDAQ)
            "TSM", "SWKS", "FSLY", "S", "CYBR", "OKTA", "MDB", "DOCU",
            "TWLO", "SHOP", "SPOT", "SQ", "UBER", "LYFT", "DASH", "ABNB",
            
            # EV & Clean Energy
            "NIO", "XPEV", "LI", "ENPH", "SEDG", "FSLR", "RUN", "PLUG",
            
            # Biotech & Healthcare Innovation
            "MRNA", "BNTX", "NVAX", "BIIB", "ILMN", "BMRN", "SGEN", "ALNY",
            
            # Gaming & Entertainment (Active)
            "TTWO", "EA", "RBLX", "U", "NFLX", "DIS", "WBD",
            
            # Trending/Meme stocks (Active)
            "GME", "AMC", "KOSS", "SNDL", "TLRY", "CGC", "ACB", "CRON",
            
            # Social Media & Communication (Active)
            "META", "SNAP", "PINS", "MTCH", "BMBL", "TWTR",
            
            # Space & Innovation (Active)
            "RKLB", "PL", "IRDM", "MAXR",
            
            # Additional NASDAQ Growth
            "ORCL", "MU", "SNPS", "CDNS", "BMY", "ALGN", "IDXX", "ISRG",
            "MNST", "WBA", "MRNA", "BNTX", "ZM", "DOCU", "CRWD", "ZS"
        ]
        
        # Filter out delisted stocks from US list
        us_stocks = filter_active_stocks(us_stocks)
        
        # Canadian stocks - cleaned and active only
        canadian_stocks = [
            # Big 6 Banks (TSX)
            "RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO", "NA.TO",
            
            # Energy & Resources (Active TSX)
            "ENB.TO", "TRP.TO", "CNQ.TO", "SU.TO", "IMO.TO", "CVE.TO", "ARX.TO",
            "WCP.TO", "BTE.TO", "MEG.TO", "POU.TO", "VET.TO", "TVE.TO",
            
            # Mining & Materials (Active TSX)
            "ABX.TO", "GOLD.TO", "K.TO", "FM.TO", "WPM.TO", "AEM.TO",
            "NGT.TO", "CCO.TO", "NXE.TO", "DML.TO", "PAAS.TO", "EQX.TO",
            
            # Technology & Growth (TSX)
            "SHOP.TO", "CSU.TO", "ATD.TO", "L.TO", "DOL.TO", "OTEX.TO", "LSPD.TO",
            
            # Railroads & Transportation (TSX)
            "CNR.TO", "CP.TO", "TFII.TO", "GFL.TO",
            
            # Telecommunications (TSX)
            "T.TO", "BCE.TO", "RCI-B.TO", "QBR-B.TO",
            
            # Utilities (TSX)
            "FTS.TO", "EMA.TO", "CU.TO", "H.TO", "AQN.TO", "BEP-UN.TO",
            
            # Insurance & Financial Services (TSX)
            "SLF.TO", "MFC.TO", "IFC.TO", "GWO.TO", "FFH.TO", "POW.TO",
            
            # Real Estate & Infrastructure (TSX)
            "BAM.TO", "BIP-UN.TO", "CCL-B.TO", "WCN.TO", "WSP.TO", "BN.TO",
            
            # Consumer & Retail (TSX)
            "MG.TO", "EMP-A.TO", "GIL.TO", "CTC-A.TO", "QSR.TO",
            
            # Healthcare & Pharma (TSX)
            "TRI.TO", "WELL.TO", "VHI.TO", "CRH.TO", "DOC.TO",
            
            # Cannabis (Active Players)
            "WEED.TO", "ACB.TO", "TLRY.TO", "CRON.TO", "OGI.TO", "HEXO.TO",
            
            # REITs (Active)
            "REI-UN.TO", "CRT-UN.TO", "HR-UN.TO", "CAR-UN.TO", "SRU-UN.TO",
            "RioCan.TO", "CT-UN.TO", "DIR-UN.TO",
            
            # US-listed Canadian companies (Active dual listings)
            "SHOP", "TD", "RY", "BNS", "BMO", "CM", "ENB", "CNR", "CP", "SLF",
            "MFC", "BAM", "TRI", "CNQ", "SU", "IMO", "CVE", "ABX", "GOLD", "K",
            "WPM", "AEM", "CCO", "NXE"
        ]
        
        # Filter out delisted stocks from Canadian list
        canadian_stocks = filter_active_stocks(canadian_stocks)
    
    us_results = []
    canadian_results = []
    
    print(f"📊 Analyzing {len(us_stocks)} US stocks...")
    for i, symbol in enumerate(us_stocks):
        result = get_technical_analysis(symbol)
        if result:
            us_results.append(result)
        if (i + 1) % 10 == 0:
            print(f"   Processed {i + 1}/{len(us_stocks)} US stocks...")
    
    print(f"🇨🇦 Analyzing {len(canadian_stocks)} Canadian stocks...")
    for i, symbol in enumerate(canadian_stocks):
        result = get_technical_analysis(symbol)
        if result:
            canadian_results.append(result)
        if (i + 1) % 10 == 0:
            print(f"   Processed {i + 1}/{len(canadian_stocks)} Canadian stocks...")
    
    return us_results, canadian_results

def send_telegram_message(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Split long messages
        max_length = 4000
        if len(message) <= max_length:
            messages = [message]
        else:
            messages = []
            lines = message.split('\n')
            current_msg = ""
            
            for line in lines:
                if len(current_msg + line + '\n') <= max_length:
                    current_msg += line + '\n'
                else:
                    if current_msg:
                        messages.append(current_msg.strip())
                    current_msg = line + '\n'
            
            if current_msg:
                messages.append(current_msg.strip())
        
        for i, msg_part in enumerate(messages):
            if i > 0:
                msg_part = f"📄 *Part {i+1}/{len(messages)}*\n\n{msg_part}"
            
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': msg_part,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                return False
        
        return True
    except:
        return False

def create_summary_report(us_results, canadian_results):
    """Create comprehensive summary report"""
    now = datetime.now()
    
    # Sort results by recommendation strength
    def sort_key(stock):
        order = {
            'STRONG BUY': 6, 'BUY': 5, 'WEAK BUY': 4,
            'HOLD': 3, 'WEAK SELL': 2, 'SELL': 1, 'STRONG SELL': 0
        }
        return order.get(stock['recommendation'], 3)
    
    us_results.sort(key=sort_key, reverse=True)
    canadian_results.sort(key=sort_key, reverse=True)
    
    # Create email report
    subject = f"📊 Stock Market Summary - {now.strftime('%Y-%m-%d %H:%M')} EST"
    
    email_body = f"""
📊 COMPREHENSIVE STOCK MARKET ANALYSIS
=====================================
{now.strftime('%Y-%m-%d %H:%M:%S')} EST

🇺🇸 US MARKET ANALYSIS ({len(us_results)} stocks)
===============================================
"""
    
    # US Market summary
    us_buy_signals = [s for s in us_results if 'BUY' in s['recommendation']]
    us_sell_signals = [s for s in us_results if 'SELL' in s['recommendation']]
    us_hold_signals = [s for s in us_results if s['recommendation'] == 'HOLD']
    
    email_body += f"""
📈 BUY Signals: {len(us_buy_signals)} stocks
📉 SELL Signals: {len(us_sell_signals)} stocks  
📊 HOLD Signals: {len(us_hold_signals)} stocks

🚀 TOP US BUY RECOMMENDATIONS:
"""
    
    for stock in us_buy_signals[:10]:
        email_body += f"""
📈 {stock['symbol']} - {stock['recommendation']} (Score: {stock['score']})
   💰 ${stock['current_price']:.2f} | 1D: {stock['change_1d']:+.2f}% | 5D: {stock['change_5d']:+.2f}% | 1M: {stock['change_1m']:+.2f}%
   🎯 RSI: {stock['rsi']:.1f} | MACD: {stock['macd']:.3f} | Stoch: {stock['stoch_k']:.1f}
   📊 BB Position: {stock['bb_position']:.1f}% | Volume: {stock['volume_ratio']:.1f}x avg
   🏢 {stock['sector']} | P/E: {stock['pe_ratio']:.1f} | Div: {stock['dividend_yield']:.1f}%
   🔍 Key Signals: {', '.join(stock['signals'][:4])}
   🚀 Buy Reasons: {', '.join(stock['buy_reasons'][:2]) if stock['buy_reasons'] else 'Technical alignment'}
"""
    
    if us_sell_signals:
        email_body += f"""

📉 TOP US SELL RECOMMENDATIONS:
"""
        for stock in us_sell_signals[:5]:
            email_body += f"""
📉 {stock['symbol']} - {stock['recommendation']} (Score: {stock['score']})
   💰 ${stock['current_price']:.2f} | 1D: {stock['change_1d']:+.2f}% | 5D: {stock['change_5d']:+.2f}% | 1M: {stock['change_1m']:+.2f}%
   🎯 RSI: {stock['rsi']:.1f} | MACD: {stock['macd']:.3f} | Stoch: {stock['stoch_k']:.1f}
   📊 BB Position: {stock['bb_position']:.1f}% | Volume: {stock['volume_ratio']:.1f}x avg
   🏢 {stock['sector']} | P/E: {stock['pe_ratio']:.1f}
   ⚠️ Sell Reasons: {', '.join(stock['sell_reasons'][:2]) if stock['sell_reasons'] else 'Technical weakness'}
"""
    
    # Canadian Market
    email_body += f"""

🇨🇦 CANADIAN MARKET ANALYSIS ({len(canadian_results)} stocks)
====================================================
"""
    
    ca_buy_signals = [s for s in canadian_results if 'BUY' in s['recommendation']]
    ca_sell_signals = [s for s in canadian_results if 'SELL' in s['recommendation']]
    ca_hold_signals = [s for s in canadian_results if s['recommendation'] == 'HOLD']
    
    email_body += f"""
📈 BUY Signals: {len(ca_buy_signals)} stocks
📉 SELL Signals: {len(ca_sell_signals)} stocks
📊 HOLD Signals: {len(ca_hold_signals)} stocks

🚀 TOP CANADIAN BUY RECOMMENDATIONS:
"""
    
    for stock in ca_buy_signals[:10]:
        email_body += f"""
📈 {stock['symbol']} - {stock['recommendation']} (Score: {stock['score']})
   💰 ${stock['current_price']:.2f} CAD | 1D: {stock['change_1d']:+.2f}% | 5D: {stock['change_5d']:+.2f}% | 1M: {stock['change_1m']:+.2f}%
   🎯 RSI: {stock['rsi']:.1f} | MACD: {stock['macd']:.3f} | Stoch: {stock['stoch_k']:.1f}
   📊 BB Position: {stock['bb_position']:.1f}% | Volume: {stock['volume_ratio']:.1f}x avg
   🏢 {stock['sector']} | P/E: {stock['pe_ratio']:.1f} | Div: {stock['dividend_yield']:.1f}%
   🔍 Key Signals: {', '.join(stock['signals'][:4])}
   🚀 Buy Reasons: {', '.join(stock['buy_reasons'][:2]) if stock['buy_reasons'] else 'Technical alignment'}
"""
    
    if ca_sell_signals:
        email_body += f"""

📉 TOP CANADIAN SELL RECOMMENDATIONS:
"""
        for stock in ca_sell_signals[:5]:
            email_body += f"""
📉 {stock['symbol']} - {stock['recommendation']} (Score: {stock['score']})
   💰 ${stock['current_price']:.2f} CAD | 1D: {stock['change_1d']:+.2f}% | 5D: {stock['change_5d']:+.2f}% | 1M: {stock['change_1m']:+.2f}%
   🎯 RSI: {stock['rsi']:.1f} | MACD: {stock['macd']:.3f} | Stoch: {stock['stoch_k']:.1f}
   📊 BB Position: {stock['bb_position']:.1f}% | Volume: {stock['volume_ratio']:.1f}x avg
   🏢 {stock['sector']} | P/E: {stock['pe_ratio']:.1f}
   ⚠️ Sell Reasons: {', '.join(stock['sell_reasons'][:2]) if stock['sell_reasons'] else 'Technical weakness'}
"""
    
    # Market summary
    email_body += f"""

📊 MARKET SUMMARY
================
🇺🇸 US Market Sentiment: {'BULLISH' if len(us_buy_signals) > len(us_sell_signals) else 'BEARISH' if len(us_sell_signals) > len(us_buy_signals) else 'NEUTRAL'}
🇨🇦 Canadian Market Sentiment: {'BULLISH' if len(ca_buy_signals) > len(ca_sell_signals) else 'BEARISH' if len(ca_sell_signals) > len(ca_buy_signals) else 'NEUTRAL'}

🎯 TRADING RECOMMENDATIONS:
• Focus on STRONG BUY signals for new positions
• Consider taking profits on SELL signals
• Monitor HOLD positions for breakouts
• Always use proper risk management

⚠️ DISCLAIMER: This analysis is for informational purposes only. 
Always do your own research before making investment decisions.

🤖 Generated by Enhanced Stock Alert System
"""
    
    return subject, email_body

def send_email(subject, body):
    """Send email report"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def main():
    """Main analysis function"""
    print("🚀 COMPREHENSIVE STOCK MARKET ANALYSIS")
    print("=" * 60)
    print(f"🕒 Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Analyze markets
    us_results, canadian_results = analyze_stock_universe()
    
    print(f"\n📊 Analysis Results:")
    print(f"   🇺🇸 US stocks analyzed: {len(us_results)}")
    print(f"   🇨🇦 Canadian stocks analyzed: {len(canadian_results)}")
    
    # Create report
    subject, email_body = create_summary_report(us_results, canadian_results)
    
    # Send email
    email_sent = send_email(subject, email_body)
    
    # Send Telegram
    telegram_msg = f"*{subject}*\n\n" + email_body.replace('=', '-')
    telegram_sent = send_telegram_message(telegram_msg)
    
    print(f"\n📧 Email sent: {'✅' if email_sent else '❌'}")
    print(f"📱 Telegram sent: {'✅' if telegram_sent else '❌'}")
    
    # Print summary to console
    print(f"\n🎯 QUICK SUMMARY:")
    us_buys = len([s for s in us_results if 'BUY' in s['recommendation']])
    us_sells = len([s for s in us_results if 'SELL' in s['recommendation']])
    ca_buys = len([s for s in canadian_results if 'BUY' in s['recommendation']])
    ca_sells = len([s for s in canadian_results if 'SELL' in s['recommendation']])
    
    print(f"   🇺🇸 US: {us_buys} BUY, {us_sells} SELL")
    print(f"   🇨🇦 CA: {ca_buys} BUY, {ca_sells} SELL")
    
    print(f"\n✅ Analysis complete! Check your email and Telegram for full report.")

if __name__ == "__main__":
    main()