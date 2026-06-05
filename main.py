from tools.stock_tool import get_stock_info
from tools.news_tool import get_news
from agents.analyst import analyze

symbol = input("Enter Stock Symbol: ").upper()

print("\nFetching stock data...")
stock_data = get_stock_info(symbol)

print("Fetching latest news...")
news = get_news(stock_data["company"])

print("Analyzing...\n")

report = analyze(stock_data, news)

print("\n" + "="*80)
print(f"FINANCIAL RESEARCH REPORT - {symbol}")
print("="*80)

print(report)

print("="*80)