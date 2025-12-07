import sys
import os
import uuid
import time
from typing import Dict, Any

# Ensure path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from hybrid_ai_assistant.orchestrator.graph import compiled_graph
from hybrid_ai_assistant.config.config import config as app_config

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py 'Your project intent'")
        # Fallback for dev
        objective = "Create a simple calculator in Python"
    else:
        objective = sys.argv[1]

    print(f"Starting Project: {objective}")
    
    thread_id = str(uuid.uuid4())
    run_config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "objective": objective,
        "logs": [],
        "completed_steps": [],
        "file_system_state": {},
        "research_memory": [],
        "plan_options": [],
        "execution_steps": []
    }
    
    # Run graph - will likely pause at human_selection (interrupt before execution)
    print("Running initial research and planning...")
    try:
        # We can stream events to show progress
        # compiled_graph.invoke(initial_state, config=run_config)
        
        # Using stream to show logs
        for event in compiled_graph.stream(initial_state, config=run_config):
             for k, v in event.items():
                 print(f"Finished node: {k}")
                 if "logs" in v and v["logs"]:
                     print(f"Log: {v['logs'][-1]}")
                     
    except Exception as e:
        print(f"Graph execution paused or error: {e}")

    # Check state
    state_snapshot = compiled_graph.get_state(run_config)
    
    # Check if we have options
    if state_snapshot.values and state_snapshot.values.get("plan_options"):
        options = state_snapshot.values["plan_options"]
        print("\nGenerated Options:")
        for i, opt in enumerate(options):
            print(f"[{i}] {opt.tech_stack}")
            print(f"    Why: {opt.why_fits}")
            print(f"    Pros: {', '.join(opt.pros)}")
            print(f"    Cons: {', '.join(opt.cons)}")
            
        # Selection
        if not state_snapshot.values.get("selected_plan"):
            while True:
                try:
                    choice = int(input("\nSelect an option (number): "))
                    if 0 <= choice < len(options):
                        selected = options[choice]
                        print(f"Selected: {selected.tech_stack}")
                        
                        # Update state
                        compiled_graph.update_state(run_config, {"selected_plan": selected})
                        break
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
            
            # Resume
            print("Resuming execution...")
            for event in compiled_graph.stream(None, config=run_config):
                for k, v in event.items():
                    print(f"Finished node: {k}")
                    if "logs" in v and v["logs"]:
                         # We might want to see the new logs
                         # Note: simplistic log print, might print duplicates if not careful
                         # but sufficient for demo
                         pass
                         
    print("Workflow completed.")
    final_state = compiled_graph.get_state(run_config)
    print("Final State Keys:", final_state.values.keys())

if __name__ == "__main__":
    main()
