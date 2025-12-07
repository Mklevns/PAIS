from langchain_community.chat_models import ChatOllama
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.config.config import config

def route_task(state: ProjectState) -> str:
    llm = ChatOllama(model=config.LOCAL_ROUTER_MODEL, base_url=config.OLLAMA_HOST)
    response = llm.invoke(f"Classify task: {state['objective']}. Research/Plan or Execute?")
    if "research" in response.content.lower():
        return "cloud"
    return "local"
