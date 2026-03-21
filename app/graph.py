from app.state.state import OnboardingState
from app.nodes.graphnodes import *
from langgraph.prebuilt import ToolNode ,tools_condition
from langgraph.graph import StateGraph,END,START

builder = StateGraph(OnboardingState)

# Define Nodes
builder.add_node("input_node", input_node)
builder.add_node("resume_data_extraction", extractResumeDataNode)
builder.add_node("jd_data_extraction", extractJDDataNode)
builder.add_node("skill_gap_analysis", skill_gap_node)
builder.add_node("roadmap_planning_agent", roadmap_planning_node)
builder.add_node("tools", tool_node) # Named 'tools' for tools_condition compatibility
builder.add_node("finalize_state", finalize_state_node)

# Define Entry Point and initial Extraction Parallelism
builder.set_entry_point("input_node")
builder.add_edge("input_node", "resume_data_extraction")
builder.add_edge("input_node", "jd_data_extraction")

# Join Extractions into Gap Analysis
builder.add_edge("resume_data_extraction", "skill_gap_analysis")
builder.add_edge("jd_data_extraction", "skill_gap_analysis")

# Transition from Analysis to Planning Agent
builder.add_edge("skill_gap_analysis", "roadmap_planning_agent")

# Agentic ReAct Loop (Planning Agent <-> Tools)
builder.add_conditional_edges(
    "roadmap_planning_agent",
    tools_condition,
    {
        "tools": "tools",            
        "__end__": "finalize_state"  # tools_condition returns '__end__' when no tools are called
    }
)

builder.add_edge("tools", "roadmap_planning_agent")
builder.add_edge("finalize_state", END)

graph = builder.compile()