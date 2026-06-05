# Financial Research Agent

An AI-powered financial research assistant built using:

- OpenAI GPT-4o
- Yahoo Finance
- Tavily Search
- Python
- Streamlit

## Features

- Stock analysis
- Recent news with source citations
- Price chart
- Key valuation and balance-sheet metrics
- Risk assessment
- Investment recommendations
- Recurring investment planner, also known as SIP or dollar-cost averaging
- Starter view for small monthly investments such as $1,000
- Retirement Plan tool using birthday and target retirement age
- Goal amount planning with required monthly contribution
- Risk profiles with return assumptions
- Retirement projection handoff into withdrawal planning
- Withdrawal planner, also known as SWP or systematic withdrawals
- Markdown exports for retirement and withdrawal plans
- USD and INR display modes
- Region selector for US-first or India-first planner labels and defaults
- Markdown report export

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with:

```bash
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

## Run Web App

```bash
streamlit run app.py
```

## Run CLI

```bash
python main.py
```

## Example

```bash
Enter Stock Symbol: NVDA
```

Generates:

- Company Overview
- Key Metrics
- Recent News Summary
- Bull Case
- Bear Case
- Risks
- Recommendation
- Confidence Score

Reports are saved to the `reports/` folder.

## Recurring Investment and Withdrawal Planning

The Streamlit app includes calculators for:

- Recurring investment projection with annual step-up
- Starter projection for $1,000/month-style investing
- Top-level retirement-age projection from birthday and desired retirement age
- Goal-based monthly contribution estimate
- Risk profile presets for return assumptions
- Portfolio withdrawal depletion and sustainability
- Retirement projection reuse inside withdrawal/SWP planning
- Year-by-year projection tables
- Markdown downloads for planning outputs
- Conservative guidance for fund-selection and withdrawal-rate decisions

Use the region selector to switch between US labels/defaults and India labels/defaults. SIP and SWP are common Indian terms. In the US, similar workflows are usually described as automated recurring investments, dollar-cost averaging, and systematic withdrawals from brokerage or retirement accounts. These tools are educational projections and do not provide personalized financial advice.
