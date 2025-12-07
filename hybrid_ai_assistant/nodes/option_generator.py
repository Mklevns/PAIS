from langchain_openai import ChatOpenAI
from hybrid_ai_assistant.state.state import ProjectState, ProjectOption
from hybrid_ai_assistant.config.config import config
import json

def generate_options(state: ProjectState) -> ProjectState:
    llm = ChatOpenAI(model=config.CLOUD_LLM, api_key=config.OPENAI_API_KEY)
    # Synthesize options
    prompt = f"From research {state['research_memory']}, generate 3 implementation options for {state['objective']}. Return JSON format list of options that matches ProjectOption schema (tech_stack, pros, cons, why_fits, complexity)."
    response = llm.invoke(prompt).content
    
    # Simple parsing logic (in prod use structured output parser)
    # Assuming the LLM is nice and returns JSON or we might need to exact it
    try:
        # Try to find JSON array in response
        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            options = [ProjectOption(**opt) for opt in data]
            state["plan_options"] = options
        else:
             state["logs"].append("Failed to parse options JSON")
    except Exception as e:
        state["logs"].append(f"Error parsing options: {e}")
        
    return state
