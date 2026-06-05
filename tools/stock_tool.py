import yfinance as yf


def _safe_info_value(info, *keys):
    for key in keys:
        value = info.get(key)
        if value not in (None, "", "N/A"):
            return value
    return None


def get_stock_info(symbol):
    ticker = yf.Ticker(symbol)

    try:
        info = ticker.info
    except Exception:
        return None

    company = _safe_info_value(info, "longName", "shortName")

    if not company:
        return None

    return {
        "symbol": symbol.upper(),
        "company": company,
        "price": _safe_info_value(info, "currentPrice", "regularMarketPrice"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "previous_close": info.get("previousClose"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "dividend_yield": info.get("dividendYield"),
        "profit_margins": info.get("profitMargins"),
        "revenue_growth": info.get("revenueGrowth"),
        "gross_margins": info.get("grossMargins"),
        "free_cashflow": info.get("freeCashflow"),
        "total_cash": info.get("totalCash"),
        "total_debt": info.get("totalDebt"),
        "recommendation": info.get("recommendationKey"),
        "analyst_count": info.get("numberOfAnalystOpinions"),
    }


def get_price_history(symbol, period="1y"):
    ticker = yf.Ticker(symbol)
    history = ticker.history(period=period)

    if history.empty:
        return history

    history = history.reset_index()
    return history
