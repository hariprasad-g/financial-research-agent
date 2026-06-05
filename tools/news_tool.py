from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def _normalize_result(item):
    return {
        "title": item.get("title"),
        "url": item.get("url"),
        "published_date": item.get("published_date"),
        "content": item.get("content"),
        "score": item.get("score"),
    }


def get_news(company):
    if not company:
        return []

    result = client.search(
        query=f"latest financial news about {company}",
        topic="news",
        include_answer=False,
        max_results=5
    )

    return [_normalize_result(item) for item in result.get("results", [])]
