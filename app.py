import pandas as pd
import streamlit as st

from agents.analyst import analyze
from reporting import format_sources, save_report
from tools.news_tool import get_news
from tools.planning_tool import project_sip, project_swp
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


def format_inr(value):
    if value is None:
        return "Unavailable"
    return f"₹{value:,.0f}"


def render_sip_tab():
    st.subheader("SIP Planner")
    st.caption("Projection only. Fund selection should be based on risk profile, time horizon, costs, and tax situation.")

    starter_cols = st.columns(3)
    starter_monthly = starter_cols[0].number_input(
        "Starter monthly investment",
        min_value=100,
        value=1000,
        step=100,
    )
    starter_years = starter_cols[1].number_input(
        "Starter years",
        min_value=1,
        max_value=40,
        value=10,
        step=1,
    )
    starter_return = starter_cols[2].number_input(
        "Starter expected return",
        min_value=1.0,
        max_value=25.0,
        value=12.0,
        step=0.5,
    )

    starter_value, starter_invested, _ = project_sip(starter_monthly, starter_years, starter_return, 0)
    starter_metric_cols = st.columns(3)
    starter_metric_cols[0].metric("Starter Invested", format_inr(starter_invested))
    starter_metric_cols[1].metric("Starter Value", format_inr(starter_value))
    starter_metric_cols[2].metric("Starter Gains", format_inr(starter_value - starter_invested))

    comparison_rows = []
    for comparison_years in [5, 10, 15, 20]:
        value, invested, _ = project_sip(starter_monthly, comparison_years, starter_return, 0)
        comparison_rows.append(
            {
                "Years": comparison_years,
                "Monthly Investment": round(starter_monthly),
                "Invested": round(invested),
                "Projected Value": round(value),
                "Estimated Gains": round(value - invested),
            }
        )

    st.caption("Quick comparison for different investment periods")
    st.dataframe(pd.DataFrame(comparison_rows), width="stretch", hide_index=True)
    st.divider()

    input_cols = st.columns(4)
    monthly_amount = input_cols[0].number_input("Monthly SIP", min_value=500, value=25000, step=500)
    years = input_cols[1].number_input("Years", min_value=1, max_value=40, value=15, step=1)
    annual_return = input_cols[2].number_input("Expected return", min_value=1.0, max_value=25.0, value=12.0, step=0.5)
    annual_step_up = input_cols[3].number_input("Annual step-up", min_value=0.0, max_value=25.0, value=5.0, step=0.5)

    projected_value, invested, sip_rows = project_sip(monthly_amount, years, annual_return, annual_step_up)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Invested", format_inr(invested))
    metric_cols[1].metric("Projected Value", format_inr(projected_value))
    metric_cols[2].metric("Estimated Gains", format_inr(projected_value - invested))

    chart_cols = st.columns([3, 2])
    with chart_cols[0]:
        st.line_chart(sip_rows.set_index("Year")[["Invested", "Projected Value"]], width="stretch")
    with chart_cols[1]:
        st.dataframe(sip_rows, width="stretch", hide_index=True)

    st.markdown(
        """
**Useful SIP rules**

- For long-term goals, diversified equity index or flexi-cap style funds are usually more suitable than narrow themes.
- Prefer low expense ratio, consistent rolling returns, clean downside behavior, and an investment horizon of 5+ years.
- Step-up SIPs often matter more than chasing the highest past return.
"""
    )


def render_swp_tab():
    st.subheader("SWP Planner")
    st.caption("Projection only. SWP stability depends on market sequence risk, taxes, inflation, and withdrawal discipline.")

    input_cols = st.columns(5)
    corpus = input_cols[0].number_input("Corpus", min_value=100000, value=5000000, step=100000)
    monthly_withdrawal = input_cols[1].number_input("Monthly SWP", min_value=1000, value=40000, step=1000)
    years = input_cols[2].number_input("Projection years", min_value=1, max_value=40, value=20, step=1)
    annual_return = input_cols[3].number_input("Expected return ", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
    inflation = input_cols[4].number_input("Withdrawal inflation", min_value=0.0, max_value=15.0, value=4.0, step=0.5)

    ending_balance, withdrawn, depleted_month, swp_rows = project_swp(
        corpus, monthly_withdrawal, years, annual_return, inflation
    )

    metric_cols = st.columns(3)
    metric_cols[0].metric("Total Withdrawn", format_inr(withdrawn))
    metric_cols[1].metric("Ending Corpus", format_inr(ending_balance))
    if depleted_month:
        metric_cols[2].metric("Corpus Depleted", f"Month {depleted_month}")
    else:
        metric_cols[2].metric("Corpus Depleted", "No")

    chart_cols = st.columns([3, 2])
    with chart_cols[0]:
        st.line_chart(swp_rows.set_index("Year")[["Remaining Corpus"]], width="stretch")
    with chart_cols[1]:
        st.dataframe(swp_rows, width="stretch", hide_index=True)

    withdrawal_rate = monthly_withdrawal * 12 / corpus
    if withdrawal_rate > 0.06:
        st.warning("The starting withdrawal rate is above 6%. That can be aggressive for long retirement-style SWP plans.")
    elif withdrawal_rate <= 0.04:
        st.success("The starting withdrawal rate is at or below 4%, which is generally more conservative.")
    else:
        st.info("The starting withdrawal rate is between 4% and 6%. Review risk tolerance and market sequence risk.")

    st.markdown(
        """
**Useful SWP rules**

- Keep 1-3 years of withdrawals in liquid or short-duration debt funds to reduce forced selling.
- Avoid withdrawing heavily from equity funds during deep drawdowns.
- For regular income, combine debt allocation, conservative hybrid allocation, and periodic rebalancing.
"""
    )


def render_stock_research(symbol, period, run_analysis):
    if not run_analysis:
        st.info("Enter a ticker and run analysis.")
        return

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
                width="stretch",
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
        width="stretch",
    )
    download_cols[1].caption(f"Saved to `{report_path}`")

    with st.expander("Source notes"):
        st.markdown(format_sources(news))


st.title("Financial Research Agent")

with st.sidebar:
    tool = st.radio("Tool", ["Stock Research", "SIP Planner", "SWP Planner"])

    if tool == "Stock Research":
        st.header("Stock Research")
        symbol = st.text_input("Ticker", value="AAPL", max_chars=12).strip().upper()
        period = st.selectbox("Price history", ["6mo", "1y", "2y", "5y"], index=1)
        run_analysis = st.button("Run analysis", type="primary", width="stretch")

if tool == "Stock Research":
    render_stock_research(symbol, period, run_analysis)
elif tool == "SIP Planner":
    render_sip_tab()
else:
    render_swp_tab()
