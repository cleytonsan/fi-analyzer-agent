"""
Fetch price and fundamentals. Strategy:
- Try yfinance for quick price + dividends.
- If ALPHAVANTAGE_KEY set, call Alpha Vantage for company overview and ratios.
- For FIIs, fetch via yfinance and infer patrimonial value from info when possible.

This module returns a unified dict with keys used by analyzer.py
"""
import os
import time
import requests
import yfinance as yf

ALPHA_KEY = os.getenv('ALPHAVANTAGE_KEY')


def fetch_stock(ticker: str) -> dict:
    ticker = ticker.upper()
    data = {'ticker': ticker}
    try:
        y = yf.Ticker(ticker + '.SA' if not ticker.endswith('.SA') and len(ticker) <= 5 else ticker)
        info = y.info
        data['price'] = info.get('currentPrice') or info.get('regularMarketPrice')
        data['marketCap'] = info.get('marketCap')
        data['dividendPerShare'] = info.get('dividendRate')
        data['sharesOutstanding'] = info.get('sharesOutstanding')
        # fallback values
        data['raw_info'] = info
    except Exception:
        pass

    # Alpha Vantage fallback for fundamentals
    if ALPHA_KEY:
        try:
            base = 'https://www.alphavantage.co/query'
            params = {'function': 'OVERVIEW', 'symbol': ticker, 'apikey': ALPHA_KEY}
            r = requests.get(base, params=params, timeout=10)
            if r.status_code == 200 and r.text:
                json = r.json()
                # copy relevant fields if present
                for k in ['PERatio','PriceToBookRatio','DividendYield','ReturnOnEquityTTM','DebtToEquity','MarketCapitalization','EBITDA']:
                    if k in json:
                        data[k] = json[k]
                time.sleep(1)
        except Exception:
            pass
    return data


def fetch_fii(ticker: str) -> dict:
    # similar approach, but data keys adjusted: patrimony, dividend history, number of properties unknown
    ticker = ticker.upper()
    data = {'ticker': ticker}
    try:
        y = yf.Ticker(ticker if ticker.endswith('.SA') else ticker + '.SA')
        info = y.info
        data['price'] = info.get('currentPrice')
        data['patrimonio_liquido'] = info.get('totalAssets') or info.get('fundNetAssetValue')
        data['dividendPerShare'] = info.get('dividendRate') or info.get('trailingAnnualDividendRate')
        data['yield'] = info.get('yield') or info.get('dividendYield')
        data['raw_info'] = info
    except Exception:
        pass
    return data
