from langchain_community.chat_models import ChatOllama
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.tools.file_ops import write_file, mkdir, set_active_container, list_dir
from hybrid_ai_assistant.utils.docker_utils import get_or_create_container, exec_in_container
from hybrid_ai_assistant.utils.repo_map import generate_repo_map
from hybrid_ai_assistant.config.config import config

def execute_plan(state: ProjectState) -> ProjectState:
    llm = ChatOllama(model=config.LOCAL_CODER_MODEL, base_url=config.OLLAMA_HOST)
    container_id = get_or_create_container()
    set_active_container(container_id) # Set context for tools
    
    steps = state.get("execution_steps", [])
    completed = []
    
    for step in steps:
        # For simplicity, we just try to generate code for the step
        # In reality this is a complex ReAct loop
        
        # 1. Get Context
        # We need to construct a file tree dict for repo map
        # This is expensive to do every time, but for now:
        file_tree = {} 
        # listing = list_dir.invoke(".") # Would return string
        # Parsing listing to build tree is skipped for brevity
        
        context = generate_repo_map(file_tree)
        
        code_prompt = f"Generate code for step: {step}. \nContext:\n{context}\nReturn ONLY the filename and content in a format I can parse, e.g. FILENAME: ... CONTENT: ..."
        
        # 2. Invoke LLM
        # response = llm.invoke(code_prompt).content
        
        # 3. Write File (Simulation)
        # Using tool directly
        write_file.invoke({"path": "output.txt", "content": f"Executed {step}"})
        
        # 4. Verify
        # exec_in_container(container_id, "python output.txt") 
        
        completed.append(step)
        state["logs"].append(f"Executed {step}")

    state["completed_steps"] = completed
    return state
