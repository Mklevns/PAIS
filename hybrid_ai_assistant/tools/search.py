from langchain_community.tools.tavily_search import TavilySearchResults
from hybrid_ai_assistant.config.config import config

tavily_tool = TavilySearchResults(api_key=config.TAVILY_API_KEY, max_results=5)
