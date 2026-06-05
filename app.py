from datetime import date

import pandas as pd
import streamlit as st

from agents.analyst import analyze
from reporting import format_sources, save_report
from tools.news_tool import get_news
from tools.planning_tool import calculate_age, project_sip, project_swp
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


def format_money(value, symbol="$"):
    if value is None:
        return "Unavailable"
    return f"{symbol}{value:,.0f}"


def render_sip_tab(currency_symbol, region):
    is_india = region == "India"
    title = "SIP Planner" if is_india else "Recurring Investment Planner"
    starter_default = 1000
    advanced_default = 25000 if is_india else 1000
    advanced_step = 500 if is_india else 10

    st.subheader(title)
    if is_india:
        st.caption(
            "SIP stands for Systematic Investment Plan. Projection only; fund selection depends on risk profile, time horizon, costs, and taxes."
        )
    else:
        st.caption(
            "Also called dollar-cost averaging in the US. Projection only; fund selection depends on risk profile, time horizon, costs, and taxes."
        )

    starter_cols = st.columns(3)
    starter_monthly = starter_cols[0].number_input(
        "Starter monthly investment",
        min_value=10,
        value=starter_default,
        step=10,
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
    starter_metric_cols[0].metric("Starter Invested", format_money(starter_invested, currency_symbol))
    starter_metric_cols[1].metric("Starter Value", format_money(starter_value, currency_symbol))
    starter_metric_cols[2].metric("Starter Gains", format_money(starter_value - starter_invested, currency_symbol))

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

    render_retirement_tab(currency_symbol, starter_monthly, starter_return)
    st.divider()

    input_cols = st.columns(4)
    monthly_label = "Monthly SIP" if is_india else "Monthly investment"
    monthly_amount = input_cols[0].number_input(
        monthly_label,
        min_value=10,
        value=advanced_default,
        step=advanced_step,
    )
    years = input_cols[1].number_input("Years", min_value=1, max_value=40, value=15, step=1)
    annual_return = input_cols[2].number_input("Expected return", min_value=1.0, max_value=25.0, value=12.0, step=0.5)
    annual_step_up = input_cols[3].number_input("Annual step-up", min_value=0.0, max_value=25.0, value=5.0, step=0.5)

    projected_value, invested, sip_rows = project_sip(monthly_amount, years, annual_return, annual_step_up)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Invested", format_money(invested, currency_symbol))
    metric_cols[1].metric("Projected Value", format_money(projected_value, currency_symbol))
    metric_cols[2].metric("Estimated Gains", format_money(projected_value - invested, currency_symbol))

    chart_cols = st.columns([3, 2])
    with chart_cols[0]:
        st.line_chart(sip_rows.set_index("Year")[["Invested", "Projected Value"]], width="stretch")
    with chart_cols[1]:
        st.dataframe(sip_rows, width="stretch", hide_index=True)

    st.markdown(
        """
**Useful SIP rules**""" if is_india else """
**Useful recurring investment rules**
"""
    )

    if is_india:
        st.markdown(
            """

- For long-term goals, diversified equity index or flexi-cap style funds are usually more suitable than narrow themes.
- Prefer low expense ratio, consistent rolling returns, clean downside behavior, and an investment horizon of 5+ years.
- Increasing the monthly amount over time often matters more than chasing the highest past return.
"""
        )
    else:
        st.markdown(
            """
- For long-term goals, diversified equity index funds or broad-market ETFs are usually more suitable than narrow themes.
- Prefer low expense ratio, consistent behavior, tax efficiency, and an investment horizon of 5+ years.
- Increasing the monthly amount over time often matters more than chasing the highest past return.
- In the US, this usually means automated recurring buys into ETFs, mutual funds, a 401(k), IRA, or brokerage account.
"""
        )


def render_retirement_tab(currency_symbol, default_monthly=1000, default_return=12.0):
    st.subheader("Retirement Timeline")
    retirement_cols = st.columns(4)
    birthday = retirement_cols[0].date_input(
        "Birthday",
        value=date(1995, 1, 1),
        min_value=date(1940, 1, 1),
        max_value=date.today(),
    )
    retirement_age = retirement_cols[1].number_input(
        "Want to retire at age",
        min_value=30,
        max_value=80,
        value=60,
        step=1,
    )
    retirement_monthly = retirement_cols[2].number_input(
        "Monthly until retirement",
        min_value=10,
        value=int(default_monthly),
        step=10,
    )
    retirement_return = retirement_cols[3].number_input(
        "Retirement expected return",
        min_value=1.0,
        max_value=25.0,
        value=float(default_return),
        step=0.5,
    )

    current_age = calculate_age(birthday, date.today())
    years_to_retire = max(int(retirement_age - current_age), 0)
    retirement_metric_cols = st.columns(4)
    retirement_metric_cols[0].metric("Current Age", current_age)
    retirement_metric_cols[1].metric("Years to Retirement", years_to_retire)

    if years_to_retire > 0:
        retirement_value, retirement_invested, _ = project_sip(
            retirement_monthly,
            years_to_retire,
            retirement_return,
            0,
        )
        retirement_metric_cols[2].metric(
            "Invested by Retirement",
            format_money(retirement_invested, currency_symbol),
        )
        retirement_metric_cols[3].metric(
            "Projected at Retirement",
            format_money(retirement_value, currency_symbol),
        )
    else:
        retirement_metric_cols[2].metric("Invested by Retirement", format_money(0, currency_symbol))
        retirement_metric_cols[3].metric("Projected at Retirement", format_money(0, currency_symbol))
        st.warning("Retirement age is not higher than current age.")


def render_swp_tab(currency_symbol, region):
    is_india = region == "India"
    st.subheader("SWP Planner" if is_india else "Withdrawal Planner")
    if is_india:
        st.caption(
            "SWP stands for Systematic Withdrawal Plan. Projection only; stability depends on sequence risk, taxes, inflation, and withdrawal discipline."
        )
    else:
        st.caption(
            "Systematic withdrawals are common in retirement planning. Projection only; stability depends on sequence risk, taxes, inflation, and withdrawal discipline."
        )

    input_cols = st.columns(5)
    corpus_default = 5000000 if is_india else 100000
    corpus_step = 100000 if is_india else 1000
    withdrawal_default = 40000 if is_india else 1000
    withdrawal_step = 1000 if is_india else 100
    corpus = input_cols[0].number_input(
        "Corpus" if is_india else "Portfolio balance",
        min_value=1000,
        value=corpus_default,
        step=corpus_step,
    )
    monthly_withdrawal = input_cols[1].number_input(
        "Monthly SWP" if is_india else "Monthly withdrawal",
        min_value=100,
        value=withdrawal_default,
        step=withdrawal_step,
    )
    years = input_cols[2].number_input("Projection years", min_value=1, max_value=40, value=20, step=1)
    annual_return = input_cols[3].number_input("Expected return ", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
    inflation = input_cols[4].number_input("Withdrawal inflation", min_value=0.0, max_value=15.0, value=4.0, step=0.5)

    ending_balance, withdrawn, depleted_month, swp_rows = project_swp(
        corpus, monthly_withdrawal, years, annual_return, inflation
    )

    metric_cols = st.columns(3)
    metric_cols[0].metric("Total Withdrawn", format_money(withdrawn, currency_symbol))
    metric_cols[1].metric("Ending Corpus" if is_india else "Ending Portfolio", format_money(ending_balance, currency_symbol))
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
        warning_label = "SWP" if is_india else "withdrawal"
        st.warning(f"The starting withdrawal rate is above 6%. That can be aggressive for long retirement-style {warning_label} plans.")
    elif withdrawal_rate <= 0.04:
        st.success("The starting withdrawal rate is at or below 4%, which is generally more conservative.")
    else:
        st.info("The starting withdrawal rate is between 4% and 6%. Review risk tolerance and market sequence risk.")

    st.markdown(
        """
**Useful SWP rules**""" if is_india else """
**Useful withdrawal rules**
"""
    )

    if is_india:
        st.markdown(
            """
- Keep 1-3 years of withdrawals in liquid or short-duration debt funds to reduce forced selling.
- Avoid withdrawing heavily from equity funds during deep drawdowns.
- For regular income, combine debt allocation, conservative hybrid allocation, and periodic rebalancing.
"""
        )
    else:
        st.markdown(
            """
- Keep 1-3 years of withdrawals in cash, money market, CDs, Treasuries, or short-duration bond funds to reduce forced selling.
- Avoid withdrawing heavily from equity funds during deep drawdowns.
- For regular income, combine a conservative fixed-income allocation, equity exposure for growth, and periodic rebalancing.
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
    region = st.radio("Region", ["United States", "India"], horizontal=True)
    is_india = region == "India"
    tool_options = ["Stock Research", "SIP Planner", "Retirement Plan", "SWP Planner"] if is_india else [
        "Stock Research",
        "Recurring Investment",
        "Retirement Plan",
        "Withdrawal Planner",
    ]
    tool = st.radio("Tool", tool_options)
    currency_options = ["INR", "USD"] if is_india else ["USD", "INR"]
    currency = st.radio("Currency", currency_options, horizontal=True)
    currency_symbol = "₹" if currency == "INR" else "$"

    if tool == "Stock Research":
        st.header("Stock Research")
        symbol = st.text_input("Ticker", value="AAPL", max_chars=12).strip().upper()
        period = st.selectbox("Price history", ["6mo", "1y", "2y", "5y"], index=1)
        run_analysis = st.button("Run analysis", type="primary", width="stretch")

if tool == "Stock Research":
    render_stock_research(symbol, period, run_analysis)
elif tool in ("Recurring Investment", "SIP Planner"):
    render_sip_tab(currency_symbol, region)
elif tool == "Retirement Plan":
    render_retirement_tab(currency_symbol)
else:
    render_swp_tab(currency_symbol, region)
