from langchain_openai import ChatOpenAI
from hybrid_ai_assistant.state.state import ProjectState, ProjectOption
from hybrid_ai_assistant.config.config import config
from pydantic import BaseModel, Field
from typing import List

# Define a wrapper model for the list
class OptionList(BaseModel):
    options: List[ProjectOption]

def generate_options(state: ProjectState) -> ProjectState:
    # UPDATED: Use with_structured_output for robust parsing
    llm = ChatOpenAI(model=config.CLOUD_LLM, api_key=config.OPENAI_API_KEY)
    structured_llm = llm.with_structured_output(OptionList)
    
    prompt = f"""
    Based on the following research results: {state['research_memory']}
    
    Generate 3 distinct implementation options for the objective: "{state['objective']}".
    """
    
    try:
        result = structured_llm.invoke(prompt)
        state["plan_options"] = result.options
    except Exception as e:
        state["logs"].append(f"Error parsing options: {e}")
        # Fallback logic or retry could go here
        
    return state
