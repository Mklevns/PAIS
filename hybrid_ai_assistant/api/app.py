from flask import Flask, request, jsonify
from hybrid_ai_assistant.orchestrator.graph import compiled_graph
from hybrid_ai_assistant.state.state import ProjectState

app = Flask(__name__)

# Basic storage for run IDs if needed, but client should track them
# For demo, the client sends run_id

@app.route('/start', methods=['POST'])
def start():
    objective = request.json.get('objective')
    if not objective:
        return jsonify({"error": "Objective required"}), 400
        
    # Start graph
    # config needs a thread_id for persistence
    import uuid
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "objective": objective,
        "logs": [],
        "completed_steps": [],
        "file_system_state": {},
        "run_id": thread_id
    }
    
    # Invoke until interrupt
    # invoke returns the final state of that step
    # We want to run it until it hits interrupt
    # We can use stream or just invoke. 
    # Since it is async/interruptible, invoke might return early if interrupted?
    # LangGraph invoke runs until end or interruption.
    
    result = compiled_graph.invoke(initial_state, config=config)
    
    return jsonify({"run_id": thread_id, "status": "started"})

@app.route('/poll/<run_id>', methods=['GET'])
def poll(run_id):
    config = {"configurable": {"thread_id": run_id}}
    state = compiled_graph.get_state(config)
    
    if not state.values:
        return jsonify({"status": "not_found"})

    current_values = state.values
    if current_values.get("plan_options"):
        # We are at selection phase or past it
        return jsonify({"options": [opt.dict() for opt in current_values["plan_options"]]})
    
    return jsonify({"status": "running", "logs": current_values.get("logs", [])})

@app.route('/select/<run_id>', methods=['POST'])
def select(run_id):
    option_id = request.json.get('option_id')
    config = {"configurable": {"thread_id": run_id}}
    state_snapshot = compiled_graph.get_state(config)
    
    if not state_snapshot.values:
         return jsonify({"error": "Run not found"}), 404
         
    options = state_snapshot.values.get("plan_options")
    if not options or option_id >= len(options):
        return jsonify({"error": "Invalid option"}), 400

    # Update state
    selected = options[option_id]
    compiled_graph.update_state(config, {"selected_plan": selected})
    
    # Resume
    # To resume, we invoke again with None input (or specific input), using same config
    compiled_graph.invoke(None, config=config)
    
    return jsonify({"status": "resumed"})

if __name__ == '__main__':
    app.run(port=5000)
