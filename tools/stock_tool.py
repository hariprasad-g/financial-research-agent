import yfinance as yf

def get_stock_info(symbol):
    ticker = yf.Ticker(symbol)

    info = ticker.info

    return {
        "company": info.get("longName"),
        "price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "sector": info.get("sector")
    }