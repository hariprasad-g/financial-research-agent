from tools.stock_tool import get_stock_info
from tools.news_tool import get_news
from agents.analyst import analyze
from reporting import save_report

symbol = input("Enter Stock Symbol: ").upper()

print("\nFetching stock data...")
stock_data = get_stock_info(symbol)

if not stock_data:
    print(f"No company data found for {symbol}. Check the ticker symbol and try again.")
    raise SystemExit(1)

print("Fetching latest news...")
news = get_news(stock_data["company"])

print("Analyzing...\n")

report = analyze(stock_data, news)
report_path = save_report(symbol, report, stock_data, news)

print("\n" + "="*80)
print(f"FINANCIAL RESEARCH REPORT - {symbol}")
print("="*80)

print(report)

print(f"\nSaved report: {report_path}")
print("="*80)
