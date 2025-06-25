import requests
import time
import random
import datetime
import csv
from io import StringIO

# --- API Keys ---
FINNHUB_KEY = "d1a0abhr01qltimud76gd1a0abhr01qltimud770"

# --- Filters ---
MARKET_CAP_THRESHOLD = 100_000_000         # USD
PERCENTAGE_FALL_THRESHOLD = 1.0            # % drop in last 1 day

# --- Stock List ---
STOCKS = ['AAPL', 'SRPT', 'DYN', 'NFLX', 'TSLA', 'NVDA', 'META', 'BA', 'INTC', 'ZM']

def get_finnhub_quote_and_profile(stock):
    try:
        quote = requests.get("https://finnhub.io/api/v1/quote", params={
            "symbol": stock,
            "token": FINNHUB_KEY
        }).json()
        current_price = quote.get("c", 0)
        previous_close = quote.get("pc", 0)

        profile = requests.get("https://finnhub.io/api/v1/stock/profile2", params={
            "symbol": stock,
            "token": FINNHUB_KEY
        }).json()
        market_cap = profile.get("marketCapitalization", 0) * 1_000_000

        return current_price, previous_close, market_cap
    except Exception as e:
        print(f"[ERROR] Finnhub API for {stock}: {e}")
        return 0, 0, 0

def process_stock(stock):
    print(f"\n--- Processing {stock} ---")
    current_price, previous_close, market_cap = get_finnhub_quote_and_profile(stock)
    print(f"{stock} | Current: {current_price} | Previous Close: {previous_close} | Market Cap: {market_cap}")

    if current_price == 0 or previous_close == 0 or market_cap < MARKET_CAP_THRESHOLD:
        print(f"❌ {stock} failed market cap or price check.")
        return None

    percentage_fall = ((current_price - previous_close) / previous_close) * 100
    print(f"{stock} | 1-Day Fall: {round(percentage_fall, 2)}%")

    if percentage_fall <= -PERCENTAGE_FALL_THRESHOLD:
        print(f"✅ {stock} passed all checks.")
        return {
            'stock': stock,
            'current_price': round(current_price, 2),
            'previous_close': round(previous_close, 2),
            'market_cap': round(market_cap),
            'percentage_fall': round(percentage_fall, 2)
        }

    print(f"❌ {stock} failed fall threshold.")
    return None

if __name__ == "__main__":
    print("🔍 Evaluating stocks...\n")
    results = []

    for stock in STOCKS:
        result = process_stock(stock)
        if result:
            results.append(result)
        time.sleep(random.uniform(1.5, 2.5))

    print("\n📊 Final Filtered Results (Cap ≥ $100M & 1-Day Drop ≥ 5%):\n")
    if results:
        for r in results:
            print(f"{r['stock']} | Price: {r['current_price']} | Cap: {r['market_cap']} | Fall: {r['percentage_fall']}%")
    else:
        print("⚠️ No stocks matched the criteria.")
