from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o"
)

def analyze(stock_data, news):

    prompt = f"""
You are a senior Wall Street analyst.

Use only the stock data and news supplied below. Do not invent facts.
If a metric is missing, say it is unavailable instead of guessing.
Separate factual evidence from opinion. This is research assistance, not
personalized financial advice.

Stock Data:
{stock_data}

Recent News Sources:
{news}

Generate a concise Markdown report with these sections:

1. Company Overview

2. Key Metrics

3. Recent News Summary

4. Bull Case

5. Bear Case

6. Risks

7. Investor Fit

8. Recommendation

9. Confidence Score

10. Source Notes

For Recommendation, use Buy, Hold, Watchlist, or Avoid and explain what
would change the view. Include a one-line disclaimer.
"""

    response = llm.invoke(prompt)

    return response.content
