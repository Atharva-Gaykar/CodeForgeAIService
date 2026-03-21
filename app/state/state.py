from typing import Any, Dict, List, Optional, Tuple,TypedDict,Literal
from typing import Annotated, Sequence
import os
from langchain_core.messages import SystemMessage, HumanMessage,ToolMessage,AIMessage
from langchain_core.tools import Tool
from langgraph.graph import StateGraph,END,START
from langgraph.types import interrupt  
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.document_loaders import  PyMuPDFLoader
from pydantic import BaseModel, Field
from typing import List, Optional
from pprint import pprint
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from app.schemas.pydanticschema import ResumeExtract,JobDescriptionExtract,SkillGapAnalysis







class OnboardingState(TypedDict):
    candidate_name: Optional[str]
    resume_text: str  
    file_path: str 
    job_description: str 
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Analysis & Extraction Data
    skill_gap_analysis_data: Optional[SkillGapAnalysis]
    resume_data: Optional[ResumeExtract]   
    extraction_error: Optional[str]         
    JobDescriptionExtract_data: Optional[JobDescriptionExtract]
    
    # --- NEW KEYS FOR OUTPUT ---
    mermaid_code: Optional[str]        # Stores the Mermaid visualization string
    final_roadmap: Optional[Dict]      # Stores the final structured JSON roadmap