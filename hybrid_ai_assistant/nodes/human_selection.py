from hybrid_ai_assistant.state.state import ProjectState

def request_selection(state: ProjectState) -> ProjectState:
    # UPDATED: Now processes after user has set selected_plan via update_state
    selected_plan = state.get("selected_plan")
    
    if selected_plan:
        state["logs"].append(f"Selected: {selected_plan.tech_stack}")
        # Logic to generate execution steps
        # UPDATED: You might use an LLM here to break the plan down into granular steps
        state["execution_steps"] = [
            "Initialize project structure",
            f"Create main file for {selected_plan.tech_stack}",
            "Create requirements.txt"
        ] 
    else:
        state["logs"].append("No plan selected; skipping step generation.")

    return state
