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

def make_recommendation(info, headlines, x_sentiment):
    bullish_count = sum(1 for _, sentiment in headlines if sentiment == "Bullish")
    bearish_count = sum(1 for _, sentiment in headlines if sentiment == "Bearish")
    if info["growth"] >= 7 and 55 <= info["rsi"] <= 80 and bullish_count >= 2 and bearish_count == 0 and x_sentiment == "Bullish":
        return "BUY"
    elif info["growth"] >= 7 and bullish_count >= 2 and x_sentiment == "Bullish":
        return "WATCH"
    else:
        return "NO SIGNAL"

def send_email(alerts, news_dict, recs_dict, x_dict):
    if not alerts:
        return
    body = "Buy signals & recommendations (growth ≥ 7%):\n"
    for sym, info in alerts.items():
        body += (
            f"\n{sym} - Recommendation: {recs_dict[sym] or 'NO SIGNAL'}\n"
            f"  Growth: {info['growth']:.2f}%\n"
            f"  Open: {info['open']:.2f}\n"
            f"  Close: {info['close']:.2f}\n"
            f"  Volume: {info['volume']:,}\n"
            f"  RSI(14): {info['rsi']:.2f}\n"
            f"  X Feed Sentiment: {x_dict[sym]}\n"
            "  Recent News Headlines & Sentiment:\n"
        )
        for headline, sentiment in news_dict[sym]:
            body += f"    - [{sentiment}] {headline}\n"
    subject = "Stock Buy Signals, News & Recommendation"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(email_from, email_password)
        s.sendmail(email_from, [email_to], msg.as_string())
    print("Email sent to", email_to)

def buy_signals(stock_data):
    return {sym: info for sym, info in stock_data.items() if info['growth'] >= 7}

def main_task():
    if not is_market_open():
        print("Markets closed today (weekend or holiday). Skipping analysis.")
        return
    data = fetch_stocks(symbols)
    signals = buy_signals(data)
    news_dict = {sym: fetch_stock_news(sym) for sym in signals}
    x_dict = {sym: fetch_x_feed_sentiment(sym) for sym in signals}
    recs_dict = {sym: make_recommendation(signals[sym], news_dict[sym], x_dict[sym]) for sym in signals}
    print("Buy Signals (Growth ≥ 7%) & Recommendations:")
    for sym in signals:
        info = signals[sym]
        print(
            f"{sym} - Recommendation: {recs_dict[sym]}\n"
            f"  Open: {info['open']:.2f}\n"
            f"  Close: {info['close']:.2f}\n"
            f"  Growth: {info['growth']:.2f}%\n"
            f"  Volume: {info['volume']:,}\n"
            f"  RSI(14): {info['rsi']:.2f}\n"
            f"  X Feed Sentiment: {x_dict[sym]}\n"
            "  Recent News Headlines and Sentiment:"
        )
        for headline, sentiment in news_dict[sym]:
            print(f"    [{sentiment}] {headline}")
    send_email(signals, news_dict, recs_dict, x_dict)

if __name__ == "__main__":
    schedule.every().day.at("07:30").do(main_task)
    print("Scheduler started. Waiting for the next run...")
    while True:
        schedule.run_pending()
        time.sleep(60)

