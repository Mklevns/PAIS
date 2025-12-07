"""
Human Selection node - Placeholder for HITL interrupt.
Waits for human to select an option, then updates state on resume.
"""
from typing import Dict, Any
from hybrid_ai_assistant.state.state import ProjectState


def human_selection_node(state: ProjectState) -> Dict[str, Any]:
    """
    Placeholder node for human-in-the-loop selection.
    In LangGraph, this is typically handled by an interrupt.
    
    This node is called when resuming after selection is made.
    It validates the selection and prepares for execution.
    
    Args:
        state: Current project state
        
    Returns:
        Updated state confirming selection
    """
    logs = state.get("logs", [])
    selected_plan = state.get("selected_plan")
    
    if not selected_plan:
        # This shouldn't happen if graph is configured correctly
        logs.append("Warning: human_selection_node called without selection")
        return {
            "logs": logs,
            "errors": state.get("errors", []) + ["No plan selected"]
        }
    
    # Validate selection
    logs.append(f"Selected plan validated: {selected_plan.tech_stack}")
    
    return {
        "logs": logs,
        "completed_steps": state.get("completed_steps", []) + ["human_selection"]
    }


def should_wait_for_selection(state: ProjectState) -> bool:
    """
    Routing function to determine if we need to wait for selection.
    
    Args:
        state: Current project state
        
    Returns:
        True if we should interrupt for selection, False otherwise
    """
    has_options = bool(state.get("plan_options"))
    has_selection = state.get("selected_plan") is not None
    
    # We should wait if we have options but no selection yet
    return has_options and not has_selection
