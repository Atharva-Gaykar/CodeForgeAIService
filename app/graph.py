from app.state.state import OnboardingState
from app.nodes.graphnodes import *
from langgraph.prebuilt import ToolNode ,tools_condition
from app.agents.agents import roadmap_planner_agent
from langgraph.graph import StateGraph,END,START

builder = StateGraph(OnboardingState)

# Define Nodes
# Define Nodes
builder.add_node("input_node", input_node)
builder.add_node("resume_data_extraction", extractResumeDataNode)
builder.add_node("jd_data_extraction", extractJDDataNode)
builder.add_node("skill_gap_analysis", skill_gap_node)

# The ReAct Agent Node
builder.add_node("roadmap_planning_agent", roadmap_planner_agent)

# The Tool Execution Node (Required for the loop)
builder.add_node("tools", ToolNode(roadmap_planner_agent_tools))

builder.add_node("finalize_state", finalize_state_node)

# 5. Define Edges and Workflow
builder.add_edge(START, "input_node")
builder.add_edge("input_node", "resume_data_extraction")
builder.add_edge("input_node", "jd_data_extraction")

# Join Parallel Extractions
builder.add_edge("resume_data_extraction", "skill_gap_analysis")
builder.add_edge("jd_data_extraction", "skill_gap_analysis")

# Start the Planning Phase
builder.add_edge("skill_gap_analysis", "roadmap_planning_agent")

# Agentic ReAct Loop
builder.add_conditional_edges(
    "roadmap_planning_agent",
    tools_condition, # Built-in: routes to "tools" if the model calls a tool
    {
        "tools": "tools",
        END: "finalize_state" # Routes to finalize if the model gives a final answer
    }
)

# Loop back to agent after tool execution
builder.add_edge("tools", "roadmap_planning_agent")

# 6. Compile
graph = builder.compile()