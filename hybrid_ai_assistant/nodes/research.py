"""
Research node - Cloud-based deep research with web search.
Performs fan-out queries and synthesizes findings.
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from hybrid_ai_assistant.config.config import config
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.tools.search import search_web


def research_node(state: ProjectState) -> Dict[str, Any]:
    """
    Perform deep research on the objective using web search.
    Synthesizes findings into actionable insights.
    
    Args:
        state: Current project state
        
    Returns:
        Updated state with research findings
    """
    objective = state.get("objective", "")
    logs = state.get("logs", [])
    research_memory = state.get("research_memory", [])
    
    # Initialize cloud model
    llm = ChatOpenAI(
        model=config.CLOUD_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.5
    )
    
    # Generate research queries
    query_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a research assistant. Generate {num_queries} specific 
        search queries to research this project objective. Focus on:
        - Best practices and patterns
        - Technology choices and comparisons
        - Common pitfalls and solutions
        - Recent developments and trends
        
        Return only the queries, one per line."""),
        ("user", "Objective: {objective}")
    ])
    
    chain = query_prompt | llm
    
    try:
        # Generate queries
        query_response = chain.invoke({
            "objective": objective,
            "num_queries": config.RESEARCH_DEPTH
        })
        queries = [q.strip() for q in query_response.content.split("\n") if q.strip()]
        logs.append(f"Generated {len(queries)} research queries")
        
        # Execute searches
        search_results = []
        for query in queries[:config.RESEARCH_DEPTH]:
            try:
                results = search_web(query, max_results=config.MAX_SEARCH_RESULTS)
                search_results.extend(results)
                logs.append(f"Searched: {query}")
            except Exception as e:
                logs.append(f"Search error for '{query}': {str(e)}")
        
        # Store in research memory
        for result in search_results:
            research_memory.append({
                "query": result.get("query", ""),
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", "")
            })
        
        # Synthesize findings
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a technical expert. Synthesize the research findings 
            into a clear summary of best practices, technology recommendations, and 
            key considerations for this project.
            
            Focus on:
            - Recommended technologies and why
            - Architecture patterns to consider
            - Common challenges and how to avoid them
            - Key design decisions to make"""),
            ("user", """Objective: {objective}
            
            Research findings:
            {findings}
            
            Provide a concise synthesis:""")
        ])
        
        # Prepare findings text
        findings_text = "\n\n".join([
            f"- {r['title']}: {r['content'][:200]}..."
            for r in search_results[:10]
        ])
        
        synthesis_chain = synthesis_prompt | llm
        synthesis_response = synthesis_chain.invoke({
            "objective": objective,
            "findings": findings_text
        })
        
        synthesis = synthesis_response.content.strip()
        logs.append(f"Research synthesis completed ({len(synthesis)} chars)")
        
        return {
            "research_queries": queries,
            "research_memory": research_memory,
            "research_synthesis": synthesis,
            "logs": logs,
            "completed_steps": state.get("completed_steps", []) + ["research"]
        }
        
    except Exception as e:
        logs.append(f"Research error: {str(e)}")
        return {
            "research_queries": [],
            "research_memory": research_memory,
            "research_synthesis": "Research unavailable due to error.",
            "logs": logs,
            "errors": state.get("errors", []) + [f"Research error: {str(e)}"]
        }
