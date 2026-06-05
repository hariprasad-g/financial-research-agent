from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("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")
)

def get_news(company):

    result = client.search(
        query=f"latest financial news about {company}",
        max_results=5
    )

    return result["results"]