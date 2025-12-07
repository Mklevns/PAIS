"""
Tavily web search integration.
Provides web search capabilities for research phase.
"""
from typing import List, Dict, Any
from hybrid_ai_assistant.config.config import config


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, content, and URL
    """
    results = []
    
    try:
        # Import Tavily client
        from tavily import TavilyClient
        
        # Initialize client
        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        
        # Perform search
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"  # Use advanced search for better results
        )
        
        # Extract results
        if response and "results" in response:
            for item in response["results"]:
                results.append({
                    "query": query,
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", ""),
                    "score": item.get("score", 0.0)
                })
                
    except ImportError:
        # Tavily not installed, return mock results
        results = [
            {
                "query": query,
                "title": f"Mock result for: {query}",
                "content": f"This is a mock search result for the query: {query}. In production, this would contain real search results from Tavily.",
                "url": "https://example.com",
                "score": 0.9
            }
        ]
    except Exception as e:
        # Return error as a result
        results = [
            {
                "query": query,
                "title": "Search Error",
                "content": f"Error performing search: {str(e)}",
                "url": "",
                "score": 0.0
            }
        ]
    
    return results[:max_results]


def search_tool():
    """
    Create a LangChain tool for web search.
    Can be used with LangChain agents.
    
    Returns:
        LangChain tool instance
    """
    from langchain.tools import Tool
    
    return Tool(
        name="web_search",
        description="Search the web for information. Useful for finding current information, best practices, and technical documentation.",
        func=lambda query: search_web(query, max_results=5)
    )
