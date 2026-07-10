from langchain_core.tools import tool
from duckduckgo_search import DDGS

@tool
def search_web(query: str, max_results: int = 3) -> str:
    """Searches the web using DuckDuckGo. Use this to find company backgrounds, news, or general information."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}")
                
        if not results:
            return "No results found."
            
        return "\n\n".join(results)
    except Exception as e:
        return f"Error searching the web: {str(e)}"
