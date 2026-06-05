from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o"
)

def analyze(stock_data, news):

    prompt = f"""
You are a senior Wall Street analyst.

Stock Data:
{stock_data}

News:
{news}

Generate:

1. Company Overview

2. Bull Case

3. Bear Case

4. Risks

5. Recommendation

6. Confidence Score
"""

    response = llm.invoke(prompt)

    return response.content