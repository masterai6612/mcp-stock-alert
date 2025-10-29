"""
Enhanced Stock Alert System with Yahoo Finance
Includes earnings calendar and investment themes
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import holidays
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from enhanced_yahoo_client import EnhancedYahooClient

# ----------- SETTINGS -----------
symbols = [
    "NVDA", "AMD", "MSFT", "GOOGL", "META", "SNOW", "PLTR",
    "AVGO", "ORCL", "FANG", "AEM", "WPM", "NEM", "RRC", "LRCX",
    "TSLA", "AAPL", "AMZN", "JPM", "BAC", "NFLX", "XOM", "CVX",
    "SPY", "QQQ", "SHOP", "BNS", "TD",
    "PFE", "KO", "MO", "PM", "VZ", "T", "ENB", "SLF",
    "KHC", "PEP", "CMCSA", "CSCO", "QCOM", "ADP", "HON",
    "LYB", "UPS", "CAG", "PEAK", "ARE", "AMCR", "EIX", "DOW", "OKE", "BEN", "VICI", "SBUX", "PAYX",
    # AI stocks additions
    "AI", "BBAI", "SOUN", "TEM", "PATH",
    # Rare mineral additions
    "MP", "UUUU", "UCU", "TMC", "HBM",
    # Crypto stocks and coins
    "HUT", "RIOT", "MARA", "COIN", "STKE", "BTC", "ETH", "SOL", "BNB", "XRP",
    # Controversial/top surge stocks
    "CELH", "CRSP", "UBER", "ANF", "ALM", "GME"
]

email_to = "masterai6612@gmail.com"
email_from = "masterai6612@gmail.com"
email_password = "svpq udbt cnsf awab"  # <--- Replace with your Gmail app password

x_bearer_token = "AAAAAAAAAAAAAAAAAAAAACkK4wEAAAAAKdKADQ5xHT9pZ2UAfrak4x9fhx4%3D3jEBEHsBTX3o3KpxCjIWsq7LCM5AA8nqcj0RjIXdRUrwTO5szv"  # <--- Replace with your real X/Twitter Bearer Token

BULLISH = ["upgrade", "buy", "beats", "growth", "strong", "outperform", "target raised", "record", "top pick"]
BEARISH = ["downgrade", "sell", "misses", "fall", "weak", "underperform", "disappoint", "decline"]

def is_market_open():
    today = datetime.date.today()
    us_holidays = holidays.US(years=today.year)
    ca_holidays = holidays.CA(years=today.year)
    weekday_open = today.weekday() < 5
    holiday = today in us_holidays or today in ca_holidays
    return weekday_open and not holiday

def calc_rsi(prices, period=14):
    delta = prices.diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    roll_up = up.rolling(window=period).mean()
    roll_down = down.rolling(window=period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def fetch_stocks(symbols):
    stock_data = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        hist = ticker.history(period="15d")
        try:
            close = hist["Close"].iloc[-1]
            open_ = hist["Open"].iloc[-1]
            growth = ((close - open_) / open_) * 100
            volume = hist["Volume"].iloc[-1]
            rsi = calc_rsi(hist["Close"].tail(14))
            stock_data[sym] = {
                "open": open_,
                "close": close,
                "growth": growth,
                "volume": volume,
                "rsi": rsi
            }
        except Exception:
            continue
    return stock_data

def fetch_stock_news(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    headlines = []
    for h in soup.find_all("h3"):
        text = h.get_text(strip=True)
        sentiment = "Neutral"
        if any(word in text.lower() for word in BULLISH):
            sentiment = "Bullish"
        if any(word in text.lower() for word in BEARISH):
            sentiment = "Bearish"
        headlines.append((text, sentiment))
    return headlines[:5]

def fetch_x_feed_sentiment(symbol):
    headers = {"Authorization": f"Bearer {x_bearer_token}"}
    search_url = f"https://api.twitter.com/2/tweets/search/recent?query=%24{symbol}&max_results=10"
    try:
        res = requests.get(search_url, headers=headers)
        data = res.json()
        tweets = [t.get("text", "") for t in data.get("data", [])]
        bullish = sum("buy" in tweet.lower() or "bull" in tweet.lower() for tweet in tweets)
        bearish = sum("sell" in tweet.lower() or "bear" in tweet.lower() for tweet in tweets)
        if bullish > bearish:
            return "Bullish"
        elif bearish > bullish:
            return "Bearish"
        else:
            return "Neutral"
    except Exception as e:
        print(f"X Sentiment fetch error for {symbol}:", e)
        return "Unknown"

def make_recommendation(info, headlines, x_sentiment, earnings_soon=False, in_hot_theme=False):
    """Enhanced recommendation with earnings and theme data"""
    bullish_count = sum(1 for _, sentiment in headlines if sentiment == "Bullish")
    bearish_count = sum(1 for _, sentiment in headlines if sentiment == "Bearish")
    
    # Enhanced scoring with new factors
    score = 0
    
    # Original factors
    if info["growth"] >= 7:
        score += 3
    if 55 <= info["rsi"] <= 80:
        score += 2
    if bullish_count >= 2 and bearish_count == 0:
        score += 2
    if x_sentiment == "Bullish":
        score += 1
    
    # New factors
    if earnings_soon:
        score += 2  # Earnings catalyst
    if in_hot_theme:
        score += 1  # Theme momentum
    
    # Recommendation logic
    if score >= 8:
        return "STRONG BUY"
    elif score >= 6:
        return "BUY"
    elif score >= 4:
        return "WATCH"
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
    
    if themes and themes.get('themes'):
        for theme in themes['themes'][:3]:  # Top 3 themes
            if theme.get('representative_stocks'):
                hot_theme_stocks.update(theme['representative_stocks'])
    
    return earnings_symbols, hot_theme_stocks, themes

def send_enhanced_email(alerts, news_dict, recs_dict, x_dict, earnings_symbols, themes):
    """Enhanced email with earnings and theme information"""
    if not alerts:
        return
    
    body = "🚀 ENHANCED STOCK ALERTS & RECOMMENDATIONS\n"
    body += "=" * 50 + "\n\n"
    
    # Add market themes summary
    if themes and themes.get('themes'):
        body += "🎯 TOP MARKET THEMES:\n"
        for i, theme in enumerate(themes['themes'][:3], 1):
            body += f"  {i}. {theme['theme']}: {theme['avg_change_percent']:+.2f}%\n"
        body += "\n"
    
    # Add sector performance
    if themes and themes.get('trending_sectors'):
        body += "📈 TOP PERFORMING SECTORS:\n"
        for i, sector in enumerate(themes['trending_sectors'][:3], 1):
            body += f"  {i}. {sector['sector']}: {sector['change_percent_5d']:+.2f}%\n"
        body += "\n"
    
    body += "📊 STOCK ALERTS (Growth ≥ 7%):\n"
    body += "=" * 30 + "\n"
    
    for sym, info in alerts.items():
        earnings_soon = sym in earnings_symbols
        recommendation = recs_dict[sym]
        
        # Add special indicators
        indicators = []
        if earnings_soon:
            indicators.append("📅 EARNINGS SOON")
        if recommendation in ["BUY", "STRONG BUY"]:
            indicators.append("🔥 HOT PICK")
        
        body += f"\n{sym} - {recommendation}"
        if indicators:
            body += f" ({', '.join(indicators)})"
        body += "\n"
        
        body += f"  💰 Price: ${info['open']:.2f} → ${info['close']:.2f}\n"
        body += f"  📈 Growth: {info['growth']:.2f}%\n"
        body += f"  📊 Volume: {info['volume']:,}\n"
        body += f"  🎯 RSI(14): {info['rsi']:.2f}\n"
        body += f"  🐦 X Sentiment: {x_dict[sym]}\n"
        
        if earnings_soon:
            body += f"  📅 Earnings: Within 7 days\n"
        
        body += "  📰 Recent News:\n"
        for headline, sentiment in news_dict[sym]:
            body += f"    [{sentiment}] {headline}\n"
    
    # Send email
    subject = f"🚀 Enhanced Stock Alerts - {len(alerts)} Signals"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(email_from, email_password)
        s.sendmail(email_from, [email_to], msg.as_string())
    
    print(f"Enhanced email sent to {email_to}")

def buy_signals(stock_data):
    return {sym: info for sym, info in stock_data.items() if info['growth'] >= 7}

def main_enhanced_task():
    """Enhanced main task with earnings and themes"""
    if not is_market_open():
        print("Markets closed today (weekend or holiday). Skipping analysis.")
        return
    
    print("🚀 Starting Enhanced Stock Analysis...")
    
    # Get enhanced data
    earnings_symbols, hot_theme_stocks, themes = get_enhanced_data()
    print(f"📅 Found {len(earnings_symbols)} stocks with upcoming earnings")
    print(f"🎯 Found {len(hot_theme_stocks)} stocks in hot themes")
    
    # Get stock data
    data = fetch_stocks(symbols)
    signals = buy_signals(data)
    
    # Get news and sentiment
    news_dict = {sym: fetch_stock_news(sym) for sym in signals}
    x_dict = {sym: fetch_x_feed_sentiment(sym) for sym in signals}
    
    # Enhanced recommendations
    recs_dict = {}
    for sym in signals:
        earnings_soon = sym in earnings_symbols
        in_hot_theme = sym in hot_theme_stocks
        recs_dict[sym] = make_recommendation(
            signals[sym], news_dict[sym], x_dict[sym], 
            earnings_soon, in_hot_theme
        )
    
    # Display results
    print("\n🎯 ENHANCED STOCK ANALYSIS RESULTS:")
    print("=" * 50)
    
    for sym in signals:
        info = signals[sym]
        recommendation = recs_dict[sym]
        earnings_soon = sym in earnings_symbols
        in_hot_theme = sym in hot_theme_stocks
        
        print(f"\n{sym} - {recommendation}")
        if earnings_soon:
            print("  📅 EARNINGS WITHIN 7 DAYS")
        if in_hot_theme:
            print("  🎯 IN HOT THEME")
        
        print(f"  💰 ${info['open']:.2f} → ${info['close']:.2f} ({info['growth']:+.2f}%)")
        print(f"  📊 Volume: {info['volume']:,} | RSI: {info['rsi']:.2f}")
        print(f"  🐦 X Sentiment: {x_dict[sym]}")
    
    # Send enhanced email
    send_enhanced_email(signals, news_dict, recs_dict, x_dict, earnings_symbols, themes)

if __name__ == "__main__":
    # Run once for testing
    main_enhanced_task()
    
    # Uncomment below for scheduled runs
    # schedule.every().day.at("07:30").do(main_enhanced_task)
    # print("Enhanced scheduler started. Waiting for the next run...")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)