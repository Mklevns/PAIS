from langchain_community.chat_models import ChatOllama
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.tools.file_ops import write_file, mkdir, list_dir
from hybrid_ai_assistant.utils.docker_utils import get_or_create_container, exec_in_container
from hybrid_ai_assistant.utils.repo_map import generate_repo_map
from hybrid_ai_assistant.config.config import config

def execute_plan(state: ProjectState) -> ProjectState:
    llm = ChatOllama(model=config.LOCAL_CODER_MODEL, base_url=config.OLLAMA_HOST)
    
    # UPDATED: Get or create container and store ID in state
    if not state.get("container_id"):
        state["container_id"] = get_or_create_container()
    
    container_id = state["container_id"]
    
    steps = state.get("execution_steps", [])
    completed = []
    
    for step in steps:
        for attempt in range(config.RETRY_BUDGET):
            # Generate context
            # We would normally generate the file tree dynamically
            # For this 'simulated' file structure, we can skip or pass empty
            context = ""
            
            code_prompt = f"Generate code for step: {step}. \nContext:\n{context}\nReturn ONLY the filename and content in a format I can parse, e.g. FILENAME: ... CONTENT: ..."
            
            # response = llm.invoke(code_prompt).content
            
            # Using tool directly for demo
            # UPDATED: Pass container_id to tools
            write_file.invoke({"path": "output.txt", "content": f"Executed {step}", "container_id": container_id})
            
            result = exec_in_container(container_id, "python output.txt")
            if "error" not in result:
                break
                
        completed.append(step)
        state["logs"].append(f"Executed: {step}")

    state["completed_steps"] = completed
    return state
