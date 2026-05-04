import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 5) -> str:
    """
    Searches the web and returns clean text results
    ready to be fed into a Claude agent.
    """
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        
        results = []
        for i, result in enumerate(response["results"], 1):
            results.append(
                f"Result {i}:\n"
                f"Title: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['content']}\n"
            )
        
        return "\n---\n".join(results)
    
    except Exception as e:
        return f"Search failed: {str(e)}"
