import os
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import holidays
import time
import smtplib
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

# ----------- SETTINGS -----------
symbols = [
    "NVDA", "AMD", "MSFT", "GOOGL", "META", "SNOW", "PLTR",
    "AVGO", "ORCL", "FANG", "AEM", "WPM", "NEM", "RRC", "LRCX",
    "TSLA", "AAPL", "AMZN", "JPM", "BAC", "NFLX", "XOM", "CVX",
    "SPY", "QQQ", "SHOP", "BNS", "TD",
    "PFE", "KO", "MO", "PM", "VZ", "T", "ENB", "SLF",
    "KHC", "PEP", "CMCSA", "CSCO", "QCOM", "ADP", "HON",
    "LYB", "UPS", "CAG", "ARE", "AMCR", "EIX", "DOW", "OKE", "BEN", "VICI", "SBUX", "PAYX",
    # AI stocks additions
    "AI", "BBAI", "SOUN", "TEM", "PATH",
    # Rare mineral additions
    "MP", "UUUU", "TMC", "HBM",
    # Crypto stocks and coins
    "HUT", "RIOT", "MARA", "COIN", "STKE", "BTC", "ETH", "SOL",
    # Controversial/top surge stocks
    "CELH", "CRSP", "UBER", "ANF", "ALM", "GME"
]

# Credentials via environment (safer). Set ALERT_EMAIL_PASS to enable SMTP send.
email_to = os.environ.get("ALERT_EMAIL_TO", "masterai6612@gmail.com")
email_from = os.environ.get("ALERT_EMAIL_FROM", "masterai6612@gmail.com")
email_password = os.environ.get("ALERT_EMAIL_PASS", "")  # Gmail app password recommended
x_bearer_token = os.environ.get("X_BEARER_TOKEN", "")

BULLISH = ["upgrade", "buy", "beats", "growth", "strong", "outperform", "target raised", "record", "top pick"]
BEARISH = ["downgrade", "sell", "misses", "fall", "weak", "underperform", "disappoint", "decline"]

ANTICIPATED_KEYWORDS = [
    "anticipat", "anticipates", "anticipation", "raise", "raised",
    "price target raised", "expects", "forecast", "projects",
    "guidance", "raises guidance", "target raised", "upgraded target"
]

ET_ZONE = ZoneInfo("America/New_York")

def is_market_open():
    today = datetime.date.today()
    us_holidays = holidays.US(years=today.year)
    weekday_open = today.weekday() < 5
    holiday = today in us_holidays
    return weekday_open and not holiday

def is_in_alert_window(start_hour=7, start_min=30, end_hour=10, end_min=0):
    now_et = datetime.datetime.now(ET_ZONE).time()
    start = datetime.time(start_hour, start_min)
    end = datetime.time(end_hour, end_min)
    return start <= now_et <= end

def calc_rsi(prices, period=14):
    prices = prices.dropna()
    if len(prices) < period + 1:
        return float("nan")
    delta = prices.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(window=period).mean().iloc[-1]
    roll_down = down.rolling(window=period).mean().iloc[-1]
    if roll_down == 0:
        return 100.0
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)

def fetch_stocks(symbols):
    stock_data = {}
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="15d")
            if hist.empty:
                continue
            close = float(hist["Close"].iloc[-1])
            open_ = float(hist["Open"].iloc[-1])
            growth = ((close - open_) / open_) * 100 if open_ else 0.0
            volume = int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0
            rsi = calc_rsi(hist["Close"].tail(30))
            stock_data[sym] = {
                "open": open_,
                "close": close,
                "growth": growth,
                "volume": volume,
                "rsi": rsi
            }
        except Exception as e:
            print(f"fetch_stocks error for {sym}: {e}")
            continue
    return stock_data

def fetch_stock_news(symbol):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/news"
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        headlines = []
        for h in soup.find_all("h3"):
            text = h.get_text(strip=True)
            if not text:
                continue
            sentiment = "Neutral"
            low = text.lower()
            if any(w in low for w in BULLISH):
                sentiment = "Bullish"
            if any(w in low for w in BEARISH):
                sentiment = "Bearish"
            headlines.append((text, sentiment))
        return headlines[:6]
    except Exception as e:
        print(f"fetch_stock_news error for {symbol}: {e}")
        return []

def detect_anticipated_raise(headlines):
    for text, _ in headlines:
        if any(kw in text.lower() for kw in ANTICIPATED_KEYWORDS):
            return True
    return False

def fetch_x_feed_sentiment(symbol):
    if not x_bearer_token:
        return "Unknown"
    headers = {"Authorization": f"Bearer {x_bearer_token}"}
    search_url = f"https://api.twitter.com/2/tweets/search/recent?query=%24{symbol}&max_results=10"
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        data = res.json()
        tweets = [t.get("text", "") for t in data.get("data", [])]
        bullish = sum("buy" in t.lower() or "bull" in t.lower() for t in tweets)
        bearish = sum("sell" in t.lower() or "bear" in t.lower() for t in tweets)
        if bullish > bearish:
            return "Bullish"
        if bearish > bullish:
            return "Bearish"
        return "Neutral"
    except Exception as e:
        print(f"X Sentiment fetch error for {symbol}: {e}")
        return "Unknown"

def make_recommendation(info, headlines, x_sentiment):
    bullish_count = sum(1 for _, s in headlines if s == "Bullish")
    bearish_count = sum(1 for _, s in headlines if s == "Bearish")
    news_raise = detect_anticipated_raise(headlines)
    if info.get("growth", 0) >= 7 and 55 <= (info.get("rsi") or 0) <= 80 and bullish_count >= 2 and bearish_count == 0 and x_sentiment == "Bullish":
        return "BUY"
    if news_raise:
        if info.get("growth", 0) >= 5 and x_sentiment == "Bullish":
            return "BUY (News Anticipated Raise)"
        return "WATCH (News Anticipated Raise)"
    if info.get("growth", 0) >= 7 and bullish_count >= 2 and x_sentiment == "Bullish":
        return "WATCH"
    return "NO SIGNAL"

def alert_candidates(stock_data, news_all):
    alerts = {}
    for sym, info in stock_data.items():
        if info.get("growth", 0) >= 7:
            alerts[sym] = info.copy()
    for sym, headlines in news_all.items():
        if sym in alerts:
            continue
        if detect_anticipated_raise(headlines):
            info = stock_data.get(sym, {"open": 0.0, "close": 0.0, "growth": 0.0, "volume": 0, "rsi": float("nan")})
            info = info.copy()
            info["news_alert"] = True
            alerts[sym] = info
    return alerts

def send_email(alerts, news_dict, recs_dict, x_dict):
    if not alerts:
        return
    body = "Buy signals & recommendations:\n"
    for sym, info in alerts.items():
        reason = "News: Anticipated Raise" if info.get("news_alert") else "Growth ≥ 7%"
        body += (
            f"\n{sym} - Recommendation: {recs_dict.get(sym,'NO SIGNAL')}\n"
            f"  Alert Reason: {reason}\n"
            f"  Growth: {info.get('growth',0):.2f}%\n"
            f"  Open: {info.get('open',0):.2f}\n"
            f"  Close: {info.get('close',0):.2f}\n"
            f"  Volume: {info.get('volume',0):,}\n"
            f"  RSI(14): {info.get('rsi','nan')}\n"
            f"  X Feed Sentiment: {x_dict.get(sym,'Unknown')}\n"
            "  Recent News Headlines & Sentiment:\n"
        )
        for headline, sentiment in news_dict.get(sym, []):
            body += f"    - [{sentiment}] {headline}\n"
    subject = "Stock Buy Signals, News & Recommendation"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    if not email_password:
        print("ALERT_EMAIL_PASS not set — skipping SMTP send. Summary:\n")
        print(body)
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
            s.starttls()
            s.login(email_from, email_password)
            s.sendmail(email_from, [email_to], msg.as_string())
        print("Email sent to", email_to)
    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed. Use a Gmail App Password and set ALERT_EMAIL_PASS env var.")
    except Exception as e:
        print("Failed to send email:", e)

def main_task():
    if not is_market_open():
        print("Markets closed today (weekend or holiday). Skipping analysis.")
        return
    data = fetch_stocks(symbols)
    if not data:
        print("No stock data retrieved this run.")
        return
    news_all = {sym: fetch_stock_news(sym) for sym in symbols}
    alerts = alert_candidates(data, news_all)
    if not alerts:
        print("No alerts found this run.")
        return
    news_dict = {sym: news_all.get(sym, []) for sym in alerts}
    x_dict = {sym: fetch_x_feed_sentiment(sym) for sym in alerts}
    recs_dict = {sym: make_recommendation(alerts[sym], news_dict[sym], x_dict[sym]) for sym in alerts}
    print(f"Alerts & Recommendations ({datetime.datetime.now(ET_ZONE).isoformat()} ET):")
    for sym in alerts:
        info = alerts[sym]
        reason = "News: Anticipated Raise" if info.get("news_alert") else "Growth ≥ 7%"
        print(
            f"{sym} - Recommendation: {recs_dict.get(sym,'NO SIGNAL')} (Reason: {reason})\n"
            f"  Open: {info.get('open',0):.2f}\n"
            f"  Close: {info.get('close',0):.2f}\n"
            f"  Growth: {info.get('growth',0):.2f}%\n"
            f"  Volume: {info.get('volume',0):,}\n"
            f"  RSI(14): {info.get('rsi','nan')}\n"
            f"  X Feed Sentiment: {x_dict.get(sym,'Unknown')}\n"
            "  Recent News Headlines and Sentiment:"
        )
        for headline, sentiment in news_dict[sym]:
            print(f"    [{sentiment}] {headline}")
    send_email(alerts, news_dict, recs_dict, x_dict)

if __name__ == "__main__":
    print("Agent started. Will run alerts between 07:30 and 10:00 ET on US market days.")
    poll_interval = 300  # seconds between checks while window is open
    while True:
        try:
            if is_market_open() and is_in_alert_window():
                main_task()
            else:
                now_et = datetime.datetime.now(ET_ZONE)
                if not is_market_open():
                    print(f"{now_et.isoformat()} ET - Market closed or holiday. Sleeping...")
                elif not is_in_alert_window():
                    print(f"{now_et.isoformat()} ET - Outside alert window (07:30-10:00 ET). Sleeping...")
        except Exception as e:
            print("Unhandled error in loop:", e)
        time.sleep(poll_interval)