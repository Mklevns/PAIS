from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.nodes.clarification import clarify_request
from hybrid_ai_assistant.nodes.research import perform_research
from hybrid_ai_assistant.nodes.option_generator import generate_options
from hybrid_ai_assistant.nodes.human_selection import request_selection
from hybrid_ai_assistant.nodes.execution import execute_plan
import sqlite3

def build_graph():
    graph = StateGraph(ProjectState)

    graph.add_node("clarification", clarify_request)
    graph.add_node("research", perform_research)
    graph.add_node("option_generator", generate_options)
    graph.add_node("human_selection", request_selection)
    graph.add_node("execution", execute_plan)

    # Simple flow for now
    # Check Clarification -> (if needed) -> END (wait for user) or Loop?
    # User design: start -> clarification -> research
    
    # We need an entry point. 
    # Logic: Start at clarification.
    graph.set_entry_point("clarification")
    
    # Conditional edge from clarification
    def route_clarification(state):
        if state.get("clarification_needed", False):
            return END  # Or some node to ask user
        return "research"

    graph.add_edge("clarification", "research") # Simplified, ignoring conditional for this draft
    
    # Research -> Option Gen
    # Conditional loop: research -> reflection -> research if incomplete
    # Simplified: Research -> Option Gen
    graph.add_edge("research", "option_generator")
    
    graph.add_edge("option_generator", "human_selection")
    
    # Interrupt before execution is handled by compile(interrupt_before=...)
    graph.add_edge("human_selection", "execution")
    graph.add_edge("execution", END)

    # Persistence
    # Ensure db exists or let sqlite3 handle it
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    return graph.compile(checkpointer=checkpointer, interrupt_before=["execution"])

compiled_graph = build_graph()
