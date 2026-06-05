import pandas as pd
import streamlit as st

from agents.analyst import analyze
from reporting import format_sources, save_report
from tools.news_tool import get_news
from tools.stock_tool import get_price_history, get_stock_info


st.set_page_config(
    page_title="Financial Research Agent",
    layout="wide",
)


def format_number(value, kind="number"):
    if value is None:
        return "Unavailable"

    if kind == "currency":
        return f"${value:,.2f}"
    if kind == "large":
        if value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        if value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        if value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        return f"${value:,.0f}"
    if kind == "percent":
        return f"{value * 100:.2f}%"

    return f"{value:,.2f}" if isinstance(value, float) else str(value)


def build_news_frame(news):
    rows = []
    for item in news:
        rows.append(
            {
                "Title": item.get("title"),
                "Published": item.get("published_date") or "Unavailable",
                "URL": item.get("url"),
                "Summary": item.get("content"),
            }
        )
    return pd.DataFrame(rows)


def render_price_chart(history):
    chart_data = history[["Date", "Close"]].dropna()
    if chart_data.empty:
        return None

    width = 760
    height = 280
    padding_x = 48
    padding_y = 28
    values = chart_data["Close"].tolist()
    min_price = min(values)
    max_price = max(values)
    price_range = max(max_price - min_price, 1)
    point_count = max(len(values) - 1, 1)

    points = []
    for index, price in enumerate(values):
        x = padding_x + (index / point_count) * (width - padding_x * 2)
        y = height - padding_y - ((price - min_price) / price_range) * (height - padding_y * 2)
        points.append(f"{x:.2f},{y:.2f}")

    first_date = pd.to_datetime(chart_data["Date"].iloc[0]).strftime("%b %d, %Y")
    last_date = pd.to_datetime(chart_data["Date"].iloc[-1]).strftime("%b %d, %Y")

    return f"""
<div style="width:100%; overflow:hidden;">
  <svg viewBox="0 0 {width} {height}" width="100%" height="280" role="img" aria-label="Price history chart">
    <rect x="0" y="0" width="{width}" height="{height}" rx="8" fill="#ffffff" />
    <line x1="{padding_x}" y1="{height - padding_y}" x2="{width - padding_x}" y2="{height - padding_y}" stroke="#d8dee9" />
    <line x1="{padding_x}" y1="{padding_y}" x2="{padding_x}" y2="{height - padding_y}" stroke="#d8dee9" />
    <text x="{padding_x}" y="18" fill="#334155" font-size="13">${max_price:,.2f}</text>
    <text x="{padding_x}" y="{height - 8}" fill="#334155" font-size="13">${min_price:,.2f}</text>
    <text x="{padding_x}" y="{height - 32}" fill="#64748b" font-size="12">{first_date}</text>
    <text x="{width - padding_x - 82}" y="{height - 32}" fill="#64748b" font-size="12">{last_date}</text>
    <polyline points="{" ".join(points)}" fill="none" stroke="#0f766e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</div>
"""


st.title("Financial Research Agent")

with st.sidebar:
    st.header("Research")
    symbol = st.text_input("Ticker", value="AAPL", max_chars=12).strip().upper()
    period = st.selectbox("Price history", ["6mo", "1y", "2y", "5y"], index=1)
    run_analysis = st.button("Run analysis", type="primary", use_container_width=True)

if run_analysis:
    if not symbol:
        st.error("Enter a ticker symbol.")
        st.stop()

    with st.status("Building research report...", expanded=True) as status:
        st.write("Fetching stock data")
        stock_data = get_stock_info(symbol)

        if not stock_data:
            status.update(label="Ticker not found", state="error")
            st.error(f"No company data found for `{symbol}`.")
            st.stop()

        st.write("Fetching price history")
        history = get_price_history(symbol, period=period)

        st.write("Fetching recent news")
        news = get_news(stock_data["company"])

        st.write("Writing analyst report")
        report = analyze(stock_data, news)

        report_path = save_report(symbol, report, stock_data, news)
        status.update(label="Research report ready", state="complete")

    st.subheader(f"{stock_data['company']} ({symbol})")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Price", format_number(stock_data.get("price"), "currency"))
    metric_cols[1].metric("Market Cap", format_number(stock_data.get("market_cap"), "large"))
    metric_cols[2].metric("Trailing P/E", format_number(stock_data.get("pe_ratio")))
    metric_cols[3].metric("Forward P/E", format_number(stock_data.get("forward_pe")))

    detail_cols = st.columns(4)
    detail_cols[0].metric("Sector", stock_data.get("sector") or "Unavailable")
    detail_cols[1].metric("EPS", format_number(stock_data.get("eps"), "currency"))
    detail_cols[2].metric("52W Low", format_number(stock_data.get("fifty_two_week_low"), "currency"))
    detail_cols[3].metric("52W High", format_number(stock_data.get("fifty_two_week_high"), "currency"))

    chart_col, source_col = st.columns([3, 2])

    with chart_col:
        st.subheader("Price")
        if history.empty:
            st.info("Price history is unavailable for this ticker.")
        else:
            chart = render_price_chart(history)
            if chart:
                st.markdown(chart, unsafe_allow_html=True)
            else:
                st.info("Price history is unavailable for this ticker.")

    with source_col:
        st.subheader("Sources")
        if news:
            st.dataframe(
                build_news_frame(news)[["Title", "Published", "URL"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recent news sources returned.")

    st.subheader("Analyst Report")
    st.markdown(report)

    report_markdown = report_path.read_text(encoding="utf-8")
    download_cols = st.columns([1, 1, 4])
    download_cols[0].download_button(
        "Download report",
        data=report_markdown,
        file_name=report_path.name,
        mime="text/markdown",
        use_container_width=True,
    )
    download_cols[1].caption(f"Saved to `{report_path}`")

    with st.expander("Source notes"):
        st.markdown(format_sources(news))
else:
    st.info("Enter a ticker and run analysis.")
