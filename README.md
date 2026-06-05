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
- Withdrawal planner, also known as SWP or systematic withdrawals
- USD and INR display modes
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
- Portfolio withdrawal depletion and sustainability
- Year-by-year projection tables
- Conservative guidance for fund-selection and withdrawal-rate decisions

SIP and SWP are common Indian terms. In the US, similar workflows are usually described as automated recurring investments, dollar-cost averaging, and systematic withdrawals from brokerage or retirement accounts. These tools are educational projections and do not provide personalized financial advice.
