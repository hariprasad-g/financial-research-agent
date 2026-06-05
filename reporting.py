from datetime import datetime
from pathlib import Path


REPORTS_DIR = Path("reports")


def format_sources(news):
    if not news:
        return "No recent news sources were returned."

    lines = []
    for index, item in enumerate(news, start=1):
        title = item.get("title") or "Untitled source"
        url = item.get("url") or "No URL"
        date = item.get("published_date") or "Date unavailable"
        lines.append(f"{index}. [{title}]({url}) - {date}")

    return "\n".join(lines)


def save_report(symbol, report, stock_data, news):
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = REPORTS_DIR / f"{symbol.upper()}_{timestamp}.md"

    content = f"""# Financial Research Report - {symbol.upper()}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Stock Snapshot

{stock_data}

## Report

{report}

## Sources

{format_sources(news)}
"""

    filename.write_text(content, encoding="utf-8")
    return filename
