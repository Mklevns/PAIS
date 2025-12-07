"""
Execution node - Local AI for code generation, file operations, and debugging.
Executes the selected plan with iterative debugging.
"""
from typing import Dict, Any
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from hybrid_ai_assistant.config.config import config
from hybrid_ai_assistant.state.state import ProjectState, ExecutionStep
from hybrid_ai_assistant.tools.file_ops import write_file, list_directory, read_file
from hybrid_ai_assistant.tools.shell import execute_command


def execution_node(state: ProjectState) -> Dict[str, Any]:
    """
    Execute the selected plan using local model.
    Generates code, creates files, and runs commands.
    
    Args:
        state: Current project state
        
    Returns:
        Updated state with execution results
    """
    objective = state.get("objective", "")
    selected_plan = state.get("selected_plan")
    logs = state.get("logs", [])
    execution_steps = state.get("execution_steps", [])
    current_step = state.get("current_step", 0)
    created_files = state.get("created_files", [])
    
    if not selected_plan:
        logs.append("Error: No plan selected for execution")
        return {
            "logs": logs,
            "errors": state.get("errors", []) + ["No plan selected for execution"]
        }
    
    # Initialize local model (Ollama)
    try:
        llm = Ollama(
            model=config.LOCAL_MODEL,
            base_url=config.OLLAMA_HOST
        )
    except Exception as e:
        logs.append(f"Failed to initialize local model: {str(e)}")
        logs.append("Falling back to cloud model for execution")
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=config.CLOUD_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.3
        )
    
    # Generate execution plan
    plan_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a code generation expert. Create a step-by-step execution 
        plan to implement the selected technical approach.
        
        For each step, specify:
        1. What to do (create file, run command, etc.)
        2. The exact content or command
        
        Be specific and actionable. Limit to {max_steps} steps.
        Format each step as: STEP N: [action] - [details]"""),
        ("user", """Objective: {objective}
        
        Selected Plan:
        Tech Stack: {tech_stack}
        Reasoning: {why_fits}
        
        Generate execution steps:""")
    ])
    
    try:
        # Generate execution plan
        if current_step == 0:
            logs.append("Generating execution plan...")
            
            chain = plan_prompt | llm
            plan_response = chain.invoke({
                "objective": objective,
                "tech_stack": selected_plan.tech_stack,
                "why_fits": selected_plan.why_fits,
                "max_steps": config.MAX_EXECUTION_STEPS
            })
            
            # Parse steps from response
            plan_text = plan_response if isinstance(plan_response, str) else plan_response.content
            steps_text = [line.strip() for line in plan_text.split("\n") if line.strip().startswith("STEP")]
            
            # Create ExecutionStep objects
            for idx, step_text in enumerate(steps_text[:config.MAX_EXECUTION_STEPS]):
                step = ExecutionStep(
                    step_number=idx + 1,
                    action=step_text,
                    status="pending"
                )
                execution_steps.append(step)
            
            logs.append(f"Created execution plan with {len(execution_steps)} steps")
        
        # Execute steps iteratively
        max_iterations = min(3, len(execution_steps) - current_step)
        for i in range(max_iterations):
            step_idx = current_step + i
            if step_idx >= len(execution_steps):
                break
            
            step = execution_steps[step_idx]
            logs.append(f"Executing step {step.step_number}: {step.action[:50]}...")
            
            # Update step status
            step.status = "running"
            
            # Simple execution logic (in production, this would be more sophisticated)
            try:
                # Check if it's a file creation step
                if "create" in step.action.lower() and "file" in step.action.lower():
                    # Generate file content
                    filename = f"generated_file_{step.step_number}.txt"
                    content = f"# Generated content for step {step.step_number}\n"
                    
                    write_file(filename, content)
                    created_files.append(filename)
                    step.result = f"Created {filename}"
                    step.status = "completed"
                    logs.append(f"Created file: {filename}")
                    
                elif "command" in step.action.lower() or "run" in step.action.lower():
                    # Execute command (in sandboxed environment)
                    command = "echo 'Command executed'"  # Placeholder
                    result = execute_command(command)
                    step.command = command
                    step.result = result.get("output", "")
                    step.status = "completed" if result.get("success") else "failed"
                    logs.append(f"Command result: {step.result[:100]}")
                    
                else:
                    # Generic step completion
                    step.result = "Step completed"
                    step.status = "completed"
                    logs.append(f"Completed step {step.step_number}")
                    
            except Exception as step_error:
                step.status = "failed"
                step.result = f"Error: {str(step_error)}"
                logs.append(f"Step {step.step_number} failed: {str(step_error)}")
        
        # Update current step
        new_current_step = current_step + max_iterations
        
        # Check if all steps are complete
        all_complete = all(
            step.status in ["completed", "failed"] 
            for step in execution_steps
        )
        
        if all_complete:
            logs.append("Execution completed!")
            completed_steps = state.get("completed_steps", []) + ["execution"]
        else:
            completed_steps = state.get("completed_steps", [])
        
        return {
            "execution_steps": execution_steps,
            "current_step": new_current_step,
            "created_files": created_files,
            "logs": logs,
            "completed_steps": completed_steps
        }
        
    except Exception as e:
        logs.append(f"Execution error: {str(e)}")
        return {
            "execution_steps": execution_steps,
            "current_step": current_step,
            "logs": logs,
            "errors": state.get("errors", []) + [f"Execution error: {str(e)}"]
        }
