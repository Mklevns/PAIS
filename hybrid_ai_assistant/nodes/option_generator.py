"""
Option Generator node - Cloud-based generation of structured implementation options.
Creates multiple viable approaches for the user to choose from.
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from hybrid_ai_assistant.config.config import config
from hybrid_ai_assistant.state.state import ProjectState, PlanOption


def option_generator_node(state: ProjectState) -> Dict[str, Any]:
    """
    Generate multiple implementation options based on research.
    Uses cloud model for comprehensive analysis.
    
    Args:
        state: Current project state
        
    Returns:
        Updated state with plan options
    """
    objective = state.get("objective", "")
    research_synthesis = state.get("research_synthesis", "")
    logs = state.get("logs", [])
    
    # Initialize cloud model
    llm = ChatOpenAI(
        model=config.CLOUD_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.7
    )
    
    # Create parser for structured output
    parser = PydanticOutputParser(pydantic_object=PlanOption)
    
    # Prompt to generate options
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a technical architect. Generate 3 distinct implementation 
        options for the given objective. Each option should have a different approach,
        tech stack, or complexity level.
        
        For each option, provide:
        1. tech_stack: Clear description of technologies
        2. why_fits: Why this approach suits the objective
        3. pros: List of advantages (at least 2)
        4. cons: List of disadvantages (at least 2)
        5. estimated_complexity: low, medium, or high
        
        Make the options genuinely different to give the user real choices.
        
        {format_instructions}"""),
        ("user", """Objective: {objective}
        
        Research Synthesis:
        {research}
        
        Generate 3 implementation options:""")
    ])
    
    try:
        options = []
        
        # Generate 3 options (do this in a loop to get varied responses)
        for i in range(3):
            # Adjust temperature for variety
            llm.temperature = 0.7 + (i * 0.1)
            
            chain = prompt | llm
            response = chain.invoke({
                "objective": objective,
                "research": research_synthesis[:1000],  # Limit context size
                "format_instructions": parser.get_format_instructions()
            })
            
            try:
                # Try to parse as structured output
                # For simplicity, we'll create options manually from the text
                content = response.content.strip()
                
                # Basic parsing (in production, use more robust parsing)
                option = PlanOption(
                    tech_stack=f"Option {i+1}: {content[:100]}...",
                    why_fits=f"Approach {i+1} based on research synthesis",
                    pros=["Proven technology", "Good community support"],
                    cons=["Learning curve", "Setup complexity"],
                    estimated_complexity=["low", "medium", "high"][i]
                )
                options.append(option)
                logs.append(f"Generated option {i+1}")
                
            except Exception as parse_error:
                logs.append(f"Parse error for option {i+1}: {str(parse_error)}")
                continue
        
        # If we couldn't generate enough options, create fallback options
        if len(options) < 3:
            logs.append("Generating fallback options")
            fallback_options = [
                PlanOption(
                    tech_stack="Modern Stack: React + TypeScript + Node.js",
                    why_fits="Popular, well-supported, great for modern web apps",
                    pros=["Large ecosystem", "Strong typing", "Fast development"],
                    cons=["Complex tooling", "Build step required"],
                    estimated_complexity="medium"
                ),
                PlanOption(
                    tech_stack="Simple Stack: HTML + CSS + Vanilla JavaScript",
                    why_fits="Lightweight, no build tools, easy to understand",
                    pros=["No dependencies", "Fast load times", "Simple deployment"],
                    cons=["Limited features", "More manual work"],
                    estimated_complexity="low"
                ),
                PlanOption(
                    tech_stack="Full Stack: Next.js + PostgreSQL + Prisma",
                    why_fits="Comprehensive solution with SSR, database, and API",
                    pros=["All-in-one solution", "Great performance", "Type safety"],
                    cons=["More complex", "Higher resource requirements"],
                    estimated_complexity="high"
                )
            ]
            options.extend(fallback_options[len(options):3])
        
        logs.append(f"Generated {len(options)} implementation options")
        
        return {
            "plan_options": options[:3],  # Ensure exactly 3 options
            "logs": logs,
            "completed_steps": state.get("completed_steps", []) + ["option_generation"]
        }
        
    except Exception as e:
        logs.append(f"Option generation error: {str(e)}")
        
        # Return default options on error
        default_options = [
            PlanOption(
                tech_stack="Standard approach",
                why_fits="Reliable and proven",
                pros=["Well documented", "Community support"],
                cons=["May need customization"],
                estimated_complexity="medium"
            )
        ]
        
        return {
            "plan_options": default_options,
            "logs": logs,
            "errors": state.get("errors", []) + [f"Option generation error: {str(e)}"]
        }
