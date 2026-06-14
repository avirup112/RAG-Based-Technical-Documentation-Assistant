from tavily import TavilyClient
from app.core.config import settings
from typing import List, Dict, Any
from loguru import logger

def search_web(query: str) -> List[Dict[str, Any]]:
    """
    Performs a web search using the Tavily API and returns documents.
    """
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY is not set. Skipping web search.")
        return []
        
    try:
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(query=query, search_depth="basic", max_results=3)
        
        docs = []
        for result in response.get("results", []):
            docs.append({
                "content": f"{result.get('title', '')}\\n{result.get('content', '')}",
                "metadata": {
                    "source": "web",
                    "url": result.get("url", ""),
                    "title": result.get("title", "")
                }
            })
            
        logger.info(f"Web search found {len(docs)} results for query: {query}")
        return docs
    except Exception as e:
        logger.error(f"Error during web search: {e}")
        return []
