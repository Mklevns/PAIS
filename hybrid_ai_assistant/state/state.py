"""
State schema and validators for the Hybrid AI Assistant.
Defines ProjectState TypedDict and Pydantic models for structured data.
"""
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class PlanOption(BaseModel):
    """Structured plan option with tech stack and reasoning"""
    tech_stack: str = Field(..., description="Technology stack description")
    why_fits: str = Field(..., description="Why this option fits the requirements")
    pros: List[str] = Field(default_factory=list, description="Advantages of this option")
    cons: List[str] = Field(default_factory=list, description="Disadvantages of this option")
    estimated_complexity: str = Field(default="medium", description="Estimated complexity: low, medium, high")
    
    @validator("estimated_complexity")
    def validate_complexity(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError("Complexity must be low, medium, or high")
        return v


class ExecutionStep(BaseModel):
    """A single execution step with action and result"""
    step_number: int
    action: str
    command: Optional[str] = None
    result: Optional[str] = None
    status: str = Field(default="pending", description="pending, running, completed, failed")


class ProjectState(TypedDict, total=False):
    """
    Main state schema for the LangGraph workflow.
    Uses TypedDict for LangGraph compatibility.
    """
    # Core objective
    objective: str
    
    # Clarification phase
    clarification_needed: bool
    clarifications: List[str]
    
    # Research phase
    research_queries: List[str]
    research_memory: List[Dict[str, Any]]
    research_synthesis: str
    
    # Planning phase
    plan_options: List[PlanOption]
    selected_plan: Optional[PlanOption]
    
    # Execution phase
    execution_steps: List[ExecutionStep]
    current_step: int
    
    # File system state
    file_system_state: Dict[str, Any]
    created_files: List[str]
    
    # Logging and tracking
    logs: List[str]
    completed_steps: List[str]
    errors: List[str]
    
    # Metadata
    start_time: Optional[float]
    end_time: Optional[float]
    total_tokens_used: int


def create_initial_state(objective: str) -> ProjectState:
    """Create initial state with defaults"""
    return ProjectState(
        objective=objective,
        clarification_needed=False,
        clarifications=[],
        research_queries=[],
        research_memory=[],
        research_synthesis="",
        plan_options=[],
        selected_plan=None,
        execution_steps=[],
        current_step=0,
        file_system_state={},
        created_files=[],
        logs=[],
        completed_steps=[],
        errors=[],
        start_time=None,
        end_time=None,
        total_tokens_used=0
    )
