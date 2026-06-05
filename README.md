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
