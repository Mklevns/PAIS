"""
Clarification node - Cloud-based ambiguity resolution.
Analyzes user objectives and asks for clarification if needed.
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from hybrid_ai_assistant.config.config import config
from hybrid_ai_assistant.state.state import ProjectState


def clarification_node(state: ProjectState) -> Dict[str, Any]:
    """
    Analyze objective for ambiguities and request clarification.
    Runs on cloud model for better understanding.
    
    Args:
        state: Current project state
        
    Returns:
        Updated state with clarification status
    """
    objective = state.get("objective", "")
    logs = state.get("logs", [])
    
    # Initialize cloud model
    llm = ChatOpenAI(
        model=config.CLOUD_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.3
    )
    
    # Prompt to identify ambiguities
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert project analyst. Analyze the user's objective 
        and determine if there are any critical ambiguities that need clarification.
        
        Consider:
        - Missing technical requirements
        - Unclear scope or features
        - Ambiguous technology choices
        - Unspecified constraints or preferences
        
        If clarification is needed, list specific questions.
        If the objective is clear enough, respond with 'NO_CLARIFICATION_NEEDED'."""),
        ("user", "Objective: {objective}")
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({"objective": objective})
        content = response.content.strip()
        
        logs.append(f"Clarification analysis: {content[:200]}...")
        
        if "NO_CLARIFICATION_NEEDED" in content:
            return {
                "clarification_needed": False,
                "clarifications": [],
                "logs": logs,
                "completed_steps": state.get("completed_steps", []) + ["clarification"]
            }
        else:
            # Parse questions (simple split for now)
            questions = [q.strip() for q in content.split("\n") if q.strip() and "?" in q]
            return {
                "clarification_needed": True,
                "clarifications": questions,
                "logs": logs,
                "completed_steps": state.get("completed_steps", []) + ["clarification_requested"]
            }
            
    except Exception as e:
        logs.append(f"Clarification error: {str(e)}")
        # On error, proceed without clarification
        return {
            "clarification_needed": False,
            "clarifications": [],
            "logs": logs,
            "errors": state.get("errors", []) + [f"Clarification error: {str(e)}"]
        }
