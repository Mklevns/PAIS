from typing import TypedDict, List, Annotated, Optional
import operator
from pydantic import BaseModel, Field

class ProjectOption(BaseModel):
    tech_stack: str = Field(description="Main technologies")
    pros: List[str]
    cons: List[str]
    why_fits: str
    complexity: str  # Low/Medium/High

class ProjectState(TypedDict):
    objective: str
    clarification_status: bool
    research_memory: List[dict]  # {query: str, results: List[str]}
    plan_options: List[ProjectOption]
    selected_plan: Optional[ProjectOption]
    execution_steps: List[str]
    completed_steps: Annotated[List[str], operator.add]
    file_system_state: dict  # Tree-like dict of dir structure
    logs: Annotated[List[str], operator.add]
    container_id: Optional[str]  # ADDED: For per-session Docker isolation
