"""
LangGraph workflow definition.
Builds and compiles the main graph with nodes, edges, and checkpoints.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path

from hybrid_ai_assistant.state.state import ProjectState
from hybrid_ai_assistant.nodes.clarification import clarification_node
from hybrid_ai_assistant.nodes.research import research_node
from hybrid_ai_assistant.nodes.option_generator import option_generator_node
from hybrid_ai_assistant.nodes.human_selection import human_selection_node, should_wait_for_selection
from hybrid_ai_assistant.nodes.execution import execution_node
from hybrid_ai_assistant.config.config import config


def build_graph():
    """
    Build the LangGraph workflow.
    
    Returns:
        Compiled LangGraph instance
    """
    # Create graph with ProjectState schema
    workflow = StateGraph(ProjectState)
    
    # Add nodes
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("research", research_node)
    workflow.add_node("option_generator", option_generator_node)
    workflow.add_node("human_selection", human_selection_node)
    workflow.add_node("execution", execution_node)
    
    # Set entry point
    workflow.set_entry_point("clarification")
    
    # Add edges
    # clarification -> research (always)
    workflow.add_edge("clarification", "research")
    
    # research -> option_generator (always)
    workflow.add_edge("research", "option_generator")
    
    # option_generator -> conditional routing
    # If we need to wait for selection, pause (interrupt)
    # Otherwise, go straight to execution (shouldn't happen normally)
    workflow.add_conditional_edges(
        "option_generator",
        should_wait_for_selection,
        {
            True: "human_selection",  # Wait for human input
            False: "execution"  # Skip if already selected (edge case)
        }
    )
    
    # human_selection -> execution (after user selects)
    workflow.add_edge("human_selection", "execution")
    
    # execution -> END
    workflow.add_edge("execution", END)
    
    # Set up checkpointing for persistence and HITL
    checkpoint_dir = Path(config.CHECKPOINT_DIR)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    checkpointer = SqliteSaver.from_conn_string(
        str(checkpoint_dir / "checkpoints.db")
    )
    
    # Compile graph with interrupt before human_selection
    # This allows the graph to pause and wait for user input
    compiled = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_selection"]
    )
    
    return compiled


# Create the compiled graph instance
compiled_graph = build_graph()


def visualize_graph(output_path: str = "graph.png"):
    """
    Generate a visualization of the graph.
    Requires pygraphviz or other graphviz tools.
    
    Args:
        output_path: Path to save the visualization
    """
    try:
        from IPython.display import Image
        img = Image(compiled_graph.get_graph().draw_png())
        with open(output_path, "wb") as f:
            f.write(img.data)
        print(f"Graph visualization saved to {output_path}")
    except Exception as e:
        print(f"Could not generate graph visualization: {e}")
        print("Install pygraphviz or graphviz for visualization support")
