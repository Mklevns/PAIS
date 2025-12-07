from langchain_openai import ChatOpenAI
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.config.config import config

def clarify_request(state: ProjectState) -> ProjectState:
    llm = ChatOpenAI(model=config.CLOUD_LLM, api_key=config.OPENAI_API_KEY)
    # Analyze ambiguity, generate questions if needed
    response = llm.invoke(f"Assess ambiguity in: {state['objective']}. If high, suggest clarifications.")
    # Logic to set clarification_status and potentially interrupt for user input
    if "ambiguous" in response.content.lower():
        state["clarification_status"] = False
        state["logs"].append("Clarification needed.")
    else:
        state["clarification_status"] = True
    return state
