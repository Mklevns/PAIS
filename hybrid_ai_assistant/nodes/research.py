from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.tools.search import tavily_tool
from hybrid_ai_assistant.config.config import config

def perform_research(state: ProjectState) -> ProjectState:
    llm = ChatOpenAI(model=config.CLOUD_LLM, api_key=config.OPENAI_API_KEY)
    # Fan-out: Generate queries
    queries = llm.invoke(f"Generate 3-5 research queries for: {state['objective']}. Return just the queries, one per line.").content.split("\n")
    # Parallel search
    results = []
    # Clean up empty lines
    queries = [q for q in queries if q.strip()]
    
    for q in queries:
        try:
            res = tavily_tool.invoke({"query": q})
            results.append({"query": q, "results": res})
        except Exception as e:
             results.append({"query": q, "error": str(e)})

    state["research_memory"] = results
    # Reflection
    reflection = llm.invoke(f"Reflect on results for {state['objective']}: {results}")
    state["logs"].append(reflection.content)
    return state
