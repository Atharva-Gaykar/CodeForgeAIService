from langchain_groq import ChatGroq
from app.schemas.pydanticschema import ResumeExtract,JobDescriptionExtract,SkillGapAnalysis
from app.core.config import settings
from app.tools.tools import roadmap_planner_agent_tools
import os

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

resume_agent=ChatGroq(
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0.2,
)


resume_agent=resume_agent.with_structured_output(

    schema=ResumeExtract,
    method="json_schema",
    include_raw=True,
    strict=True
)

jd_agent=ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.2,
)


jd_agent=jd_agent.with_structured_output(

    schema=JobDescriptionExtract,
    method="json_schema",
    include_raw=True,
    strict=True
)


gap_analysis_agent=ChatGroq(
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0.2,
)


gap_analysis_agent=gap_analysis_agent.with_structured_output(
    schema=SkillGapAnalysis,
    method="json_schema",
    include_raw=True,
    strict=True
)



roadmap_planner_agent=ChatGroq(
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0.2,
)

roadmap_planner_agent=roadmap_planner_agent.bind_tools(roadmap_planner_agent_tools)