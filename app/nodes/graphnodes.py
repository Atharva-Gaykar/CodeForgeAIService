from app.state.state import OnboardingState
from langchain_core.messages import SystemMessage, HumanMessage,ToolMessage,AIMessage
from app.prompts.resume_agent_prompt import resume_agent_prompt
from app.prompts.jd_agent_prompt import jd_agent_prompt
from app.prompts.roadmap_planner_agent_prompt import roadmap_planner_agent_prompt
from app.agents.agents import resume_agent,jd_agent,roadmap_planner_agent,gap_analysis_agent
from app.prompts.gap_analysis_agent_prompt import gap_analysis_agent_prompt
from app.schemas.pydanticschema import ResumeExtract,JobDescriptionExtract,SkillGapAnalysis
import json
from app.tools.tools import *
from langchain_community.document_loaders import PyMuPDFLoader
from langgraph.prebuilt import ToolNode ,tools_condition

def input_node(state: OnboardingState):

    file_path = state.get("file_path") 

    if not file_path:
        return {"extraction_error": "Missing file_path in state"}

    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()

        
        resume_text = "\n".join([doc.page_content for doc in docs])

        return {
            "resume_text": resume_text,
            "extraction_error": None
        }

    except Exception as e:
        return {
            "extraction_error": f"Failed to load resume: {str(e)}"
        }
    

def extractResumeDataNode(state: OnboardingState):
    
    resume_text = state["resume_text"]

    messages = [
        SystemMessage(content=resume_agent_prompt),
        HumanMessage(content=f"<resume_text>{resume_text}</resume_text>")
    ]

    
    result = resume_agent.invoke(messages)

    return {"resume_data": result["parsed"]}


def extractJDDataNode(state: OnboardingState):
    # 1. Safety Check: Is the text even in the state?
    jd_text = state.get("job_description", "")
    
    if not jd_text or len(jd_text.strip()) < 5:
        print("DEBUGGER ERROR: job_description text is MISSING from state!")
        return {"JobDescriptionExtract_data": JobDescriptionExtract()}

    print(f"DEBUGGER: Sending {len(jd_text)} characters to JD Agent...")

    messages = [
        SystemMessage(content=jd_agent_prompt),
        HumanMessage(content=f"EXTRACT FROM THIS TEXT:\n\n{jd_text}")
    ]

    try:
        # 2. Invoke the agent
        result = jd_agent.invoke(messages)
        
        # 3. Handle the 'parsed' key (ensure your chain is configured correctly)
        # If result is already the Pydantic object, use it directly.
        # If result is a dict with 'parsed', use result['parsed'].
        parsed_data = result.get("parsed") if isinstance(result, dict) else result

        # 4. Critical Check: Did it actually find anything?
        if parsed_data.job_title is None and parsed_data.tools_technologies is None:
            print("DEBUGGER WARNING: LLM returned empty schema! Checking prompt...")
        else:
            print(f"DEBUGGER SUCCESS: Extracted {parsed_data.job_title}")

        return {"JobDescriptionExtract_data": parsed_data}
        
    except Exception as e:
        print(f"DEBUGGER CRITICAL: Invoke failed: {str(e)}")
        return {"JobDescriptionExtract_data": JobDescriptionExtract()}
    



def skill_gap_node(state: OnboardingState):
    
    resume_data = state["resume_data"] 
    candidate_name = state["candidate_name"]
    
    # To remove noise and reduce size  of the prompt.
    lean_resume_dict = resume_data.model_dump(
       exclude_none=True # Bonus: Automatically drops any fields that are None/null!
    )

    raw_jd = state["JobDescriptionExtract_data"]
    
    # Strip the HR noise and text bloat
    lean_jd_dict = raw_jd.model_dump(
       exclude_none=True # Drops any null fields
    )
    
    lean_resume_json = json.dumps(lean_resume_dict, indent=2)


    lean_jd_json = json.dumps(lean_jd_dict, indent=2)

    messages = [
        SystemMessage(content=gap_analysis_agent_prompt),
        HumanMessage(content=f"Users Resume:UserName:<candidate_name>{candidate_name}</candidate_name> Resume:<lean_resume_json>{lean_resume_json}</lean_resume_json> Job Description:<lean_jd_json>{lean_jd_json}</lean_jd_json>"),
        
    ]

    
    result = gap_analysis_agent.invoke(messages)

    return {"skill_gap_analysis_data": result["parsed"]}




def finalize_state_node(state: OnboardingState):
    """
    Final node that extracts structured data from the message scratchpad
    and populates the main state keys. No global variables needed!
    """
    final_roadmap = None
    mermaid_code = None

    # We search the messages in reverse to find the LATEST tool calls
    for msg in reversed(state["messages"]):
        # Check if the message has tool calls (this will be an AIMessage)
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                
                # 1. Extract the Roadmap JSON
                if tool_call["name"] == "submit_final_roadmap":
                    final_roadmap = tool_call["args"]
                
                # 2. Extract the Mermaid String
                elif tool_call["name"] == "submit_mermaid_visualization":
                    mermaid_code = tool_call["args"].get("mermaid_code")

        # Once we have both, we can stop searching
        if final_roadmap and mermaid_code:
            break

    
    
    return {
        "final_roadmap": final_roadmap,
        "mermaid_code": mermaid_code
    }



tool_node = ToolNode(roadmap_planner_agent_tools)
