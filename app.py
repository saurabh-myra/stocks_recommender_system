import os
from flask import Flask, request, render_template
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# --- API Keys ---
FINNHUB_KEY = "d1a0abhr01qltimud76gd1a0abhr01qltimud770"

# --- Stock List ---


def get_sp500_stocks():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    return df['Symbol'].tolist()


STOCKS = get_sp500_stocks()[:50]  # limit to first 50 for speed & API safety


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


def process_stock(stock, market_cap_threshold, fall_threshold):
    current_price, previous_close, market_cap = get_finnhub_quote_and_profile(stock)

    if current_price == 0 or previous_close == 0 or market_cap < market_cap_threshold:
        return None

    percentage_fall = ((current_price - previous_close) / previous_close) * 100

    if percentage_fall <= -fall_threshold:
        return {
            'stock': stock,
            'current_price': round(current_price, 2),
            'previous_close': round(previous_close, 2),
            'market_cap': round(market_cap),
            'percentage_fall': round(percentage_fall, 2)
        }

    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    market_cap_threshold = 100_000_000
    fall_threshold = 5.0

    if request.method == 'POST':
        try:
            market_cap_threshold = int(request.form.get('market_cap_threshold', 100_000_000))
            fall_threshold = float(request.form.get('fall_threshold', 5.0))
        except ValueError:
            pass

        def worker(symbol):
            try:
                return process_stock(symbol, market_cap_threshold, fall_threshold)
            except Exception as e:
                print(f"[ERROR] {symbol}: {e}")
                return None

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(worker, stock): stock for stock in STOCKS}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

    return render_template('index.html', results=results)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(host='0.0.0.0', port=port)

