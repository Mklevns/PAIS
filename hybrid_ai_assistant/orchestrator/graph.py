from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.nodes.clarification import clarify_request
from hybrid_ai_assistant.nodes.research import perform_research
from hybrid_ai_assistant.nodes.option_generator import generate_options
from hybrid_ai_assistant.nodes.human_selection import request_selection  # UPDATED: Renamed import
from hybrid_ai_assistant.nodes.execution import execute_plan
import sqlite3

def build_graph():
    graph = StateGraph(ProjectState)

    graph.add_node("clarification", clarify_request)
    graph.add_node("research", perform_research)
    graph.add_node("option_generator", generate_options)
    graph.add_node("human_selection", request_selection)  # UPDATED: Uses new function
    graph.add_node("execution", execute_plan)

    # UPDATED: Conditional edges for clarification
    def route_clarification(state):
        # If clarification is FALSE (meaning we are NOT clear), we might want to stop or ask user.
        # Based on clarification.py logic: 
        # if "ambiguous", state["clarification_status"] = False.
        
        if state.get("clarification_status") is False:
            # In a real app, you might route to a "ask_user" node. 
            # For now, let's say we just log it and proceed, or end.
            return "research" 
        return "research"

    graph.add_conditional_edges(
        "clarification",
        route_clarification,
        {
            "research": "research",
            "end": END  # If you implemented a halt logic
        }
    )
    
    # Needs entry point
    graph.set_entry_point("clarification")

    graph.add_conditional_edges("research", lambda s: "option_generator" if len(s["research_memory"]) > 0 else "research")  # Loop for reflection
    graph.add_edge("option_generator", "human_selection")
    graph.add_edge("human_selection", "execution")
    graph.add_edge("execution", END)

    checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
    # UPDATED: Interrupt before human_selection
    return graph.compile(checkpointer=checkpointer, interrupt_before=["human_selection"])

compiled_graph = build_graph()
