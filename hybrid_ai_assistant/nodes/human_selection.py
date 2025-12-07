from langchain_openai import ChatOpenAI
from hybrid_ai_assistant.config.config import config

def request_selection(state: ProjectState) -> ProjectState:
    # UPDATED: Now processes after user has set selected_plan via update_state
    selected_plan = state.get("selected_plan")
    
    if selected_plan:
        state["logs"].append(f"Selected: {selected_plan.tech_stack}")
        
        # USE LLM TO GENERATE STEPS
        try:
            llm = ChatOpenAI(model=config.CLOUD_LLM, api_key=config.OPENAI_API_KEY)
            step_prompt = f"""
            Break down the implementation of '{state['objective']}' using {selected_plan.tech_stack} 
            into a list of 3-5 sequential coding tasks. 
            Return ONLY the list of tasks, separated by newlines.
            Do not number them.
            """
            response = llm.invoke(step_prompt)
            steps = [s.strip() for s in response.content.split('\n') if s.strip()]
            state["execution_steps"] = steps
        except Exception as e:
            state["logs"].append(f"Error generating steps: {e}")
            # Fallback
            state["execution_steps"] = ["Create main file", "Create requirements.txt"]
    else:
        state["logs"].append("No plan selected; skipping step generation.")

    return state
