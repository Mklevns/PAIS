"""
Semantic routing logic for cloud vs local model selection.
Determines which model to use based on task complexity.
"""
from typing import Literal
from hybrid_ai_assistant.config.config import config


TaskType = Literal["research", "planning", "code_generation", "debugging", "simple_query"]


def route_to_model(task_type: TaskType, complexity: str = "medium") -> str:
    """
    Route a task to the appropriate model (cloud or local).
    
    Args:
        task_type: Type of task to perform
        complexity: Estimated complexity (low, medium, high)
        
    Returns:
        Model name to use
    """
    # Decision matrix:
    # - Research and planning: Always cloud (requires better reasoning)
    # - Code generation: Cloud for high complexity, local for low/medium
    # - Debugging: Cloud (requires analysis)
    # - Simple queries: Local (fast responses)
    
    if task_type in ["research", "planning", "debugging"]:
        return config.CLOUD_MODEL
    
    elif task_type == "code_generation":
        if complexity == "high":
            return config.CLOUD_MODEL
        else:
            return config.LOCAL_MODEL
    
    elif task_type == "simple_query":
        return config.LOCAL_MODEL
    
    # Default to cloud for unknown tasks
    return config.CLOUD_MODEL


def calculate_complexity(
    objective: str,
    tech_stack: str = "",
    estimated_steps: int = 5
) -> str:
    """
    Calculate estimated complexity of a task.
    
    Args:
        objective: Task objective description
        tech_stack: Technologies involved
        estimated_steps: Number of implementation steps
        
    Returns:
        Complexity level: low, medium, or high
    """
    # Simple heuristics for complexity estimation
    complexity_score = 0
    
    # Factor 1: Objective length and keywords
    objective_lower = objective.lower()
    if len(objective) > 200:
        complexity_score += 1
    
    complex_keywords = [
        "distributed", "scalable", "enterprise", "microservices",
        "real-time", "production", "deploy", "ci/cd", "kubernetes"
    ]
    complexity_score += sum(1 for kw in complex_keywords if kw in objective_lower)
    
    # Factor 2: Tech stack complexity
    if tech_stack:
        stack_lower = tech_stack.lower()
        complex_tech = [
            "kubernetes", "docker", "grpc", "graphql", "websocket",
            "redis", "postgresql", "mongodb", "elasticsearch"
        ]
        complexity_score += sum(1 for tech in complex_tech if tech in stack_lower)
    
    # Factor 3: Number of steps
    if estimated_steps > 10:
        complexity_score += 2
    elif estimated_steps > 5:
        complexity_score += 1
    
    # Map score to complexity level
    if complexity_score <= 2:
        return "low"
    elif complexity_score <= 5:
        return "medium"
    else:
        return "high"


def should_use_cloud(task_description: str) -> bool:
    """
    Determine if a task should use cloud model.
    Convenience function for quick decisions.
    
    Args:
        task_description: Description of the task
        
    Returns:
        True if cloud model should be used, False for local
    """
    # Check for cloud-requiring keywords
    cloud_keywords = [
        "research", "analyze", "compare", "evaluate", "plan",
        "design", "architecture", "recommend", "decide"
    ]
    
    task_lower = task_description.lower()
    
    return any(keyword in task_lower for keyword in cloud_keywords)


def get_model_for_task(task_description: str, force_cloud: bool = False) -> str:
    """
    Get the appropriate model for a given task.
    
    Args:
        task_description: Description of the task
        force_cloud: Force use of cloud model regardless of heuristics
        
    Returns:
        Model name to use
    """
    if force_cloud:
        return config.CLOUD_MODEL
    
    if should_use_cloud(task_description):
        return config.CLOUD_MODEL
    else:
        return config.LOCAL_MODEL
