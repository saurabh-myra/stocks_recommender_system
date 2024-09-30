import yfinance as yf
import datetime
import numpy as np
from yahoo_fin import stock_info as si
from requests.exceptions import ChunkedEncodingError
from flask import Flask, request, render_template
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

app = Flask(__name__)

# Parameters
MARKET_CAP_THRESHOLD = 100000000  # Minimum market cap to consider
TARGET_TO_CURRENT_RATIO_THRESHOLD = 1.5  # Minimum ratio of target to current price
PERCENTAGE_FALL_THRESHOLD = 5  # Minimum percentage fall to consider
DAYS_AGO = 5  # Lookback period in days


def get_stock_list():
    # Fetch lists directly as sets
    #symbols = set(si.tickers_sp500() + si.tickers_nasdaq() + si.tickers_dow())
    #symbols = set(si.tickers_dow())
    symbols = {'AAPL', 'ACHC', 'IRWD', 'RCKT'}
    symbols.discard("")  # Remove any empty strings
    return list(symbols)


def get_percentage_fall(stock_symbol, days_ago):
    today = datetime.date.today()
    start_day = today - datetime.timedelta(days=days_ago)

    # Fetch historical data for the stock
    stock_data = yf.download(stock_symbol, start=start_day, end=today)

    if len(stock_data) < 2:
        return None  # Not enough data

    # Calculate the percentage fall
    closing_prices = stock_data['Close']
    percentage_fall = ((closing_prices.iloc[-1] - closing_prices.iloc[0]) / closing_prices.iloc[0]) * 100

    return percentage_fall


def get_quote_table(stock):
    ticker = yf.Ticker(stock)
    target_est = ticker.info.get('targetMeanPrice', 0)

    # Fetch the current market price from the historical data
    try:
        stock_data = ticker.history(period='1d')
        if not stock_data.empty:
            quote_price = stock_data['Close'].iloc[-1]
        else:
            quote_price = 1  # Fallback value in case data is not available
    except ChunkedEncodingError as e:
        print(f"Error fetching market price for {stock}: {e}")
        quote_price = 1  # Fallback value

    quote_table = {
        '1y Target Est': target_est,
        'Quote Price': quote_price
    }
    return quote_table


def process_stock(stock, market_cap_threshold, target_to_current_ratio_threshold, percentage_fall_threshold, days_ago):
    try:
        stock_info = yf.Ticker(stock).info
        market_cap = stock_info.get('marketCap', 0)
        quote_table = get_quote_table(stock)

        target_est = quote_table.get('1y Target Est', 0)
        quote_price = quote_table.get('Quote Price', 1)

        if market_cap > market_cap_threshold and target_est / quote_price >= target_to_current_ratio_threshold:
            percentage_fall = get_percentage_fall(stock, days_ago)
            if percentage_fall and np.abs(percentage_fall) > percentage_fall_threshold:
                return stock
    except Exception as e:
        print(f'Error processing {stock}: {e}')
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        market_cap_threshold = int(request.form['market_cap_threshold'])
        target_to_current_ratio_threshold = float(request.form['target_to_current_ratio_threshold'])
        percentage_fall_threshold = float(request.form['percentage_fall_threshold'])
        days_ago = int(request.form['days_ago'])

        stocks_fallen = []
        stock_list = get_stock_list()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_stock, stock, market_cap_threshold, target_to_current_ratio_threshold,
                                       percentage_fall_threshold, days_ago): stock for stock in stock_list}
            for future in futures:
                try:
                    result = future.result(timeout=20)
                    if result:
                        stocks_fallen.append(result)
                except FuturesTimeoutError:
                    print(f'Timeout occurred for {futures[future]}')
                except Exception as e:
                    print(f'Error processing {futures[future]}: {e}')

        return render_template('index.html', stocks=stocks_fallen)

    return render_template('index.html', stocks=[])


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)