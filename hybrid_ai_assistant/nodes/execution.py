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
        # Pass run_id if available to ensure isolation
        state["container_id"] = get_or_create_container(run_id=state.get("run_id"))
    
    container_id = state["container_id"]
    
    steps = state.get("execution_steps", [])
    completed = []
    
    for step in steps:
        for attempt in range(config.RETRY_BUDGET):
            # Generate context
            # We would normally generate the file tree dynamically
            # For this 'simulated' file structure, we can skip or pass empty
            # context = generate_repo_map(state.get("file_system_state", {}))
            context = "" # simplified for demo
            
            code_prompt = f"""
            You are a coding assistant. 
            Objective: {state['objective']}
            Current Step: {step}
            Tech Stack: {state['selected_plan'].tech_stack if state.get('selected_plan') else 'Python'}
            
            Return a JSON object with two keys: "filename" and "content".
            Example: {{"filename": "main.py", "content": "print('hello')"}}
            Do not include markdown formatting or backticks.
            """
            
            try:
                # 2. Invoke LLM
                response = llm.invoke(code_prompt).content
                
                # Clean up response if it has backticks
                response = response.replace("```json", "").replace("```", "").strip()

                import json
                data = json.loads(response)
                
                filename = data.get('filename')
                content = data.get('content')
                
                if filename and content:
                    # 3. Write File
                    write_file.invoke({"path": filename, "content": content, "container_id": container_id})
                    
                    # 4. Execute (if python)
                    result = "File written"
                    if filename.endswith(".py"):
                        result = exec_in_container(container_id, f"python {filename}")
                    
                    state["logs"].append(f"Executed {step}: {result}")
                    if "error" not in result.lower():
                        break
            except Exception as e:
                state["logs"].append(f"Error executing step {step}: {e}")
                
        completed.append(step)

    state["completed_steps"] = completed
    return state
