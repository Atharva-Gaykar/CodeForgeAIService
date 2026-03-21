from langchain_core.tools import tool
from typing import Optional
from app.utils.vectordatabase import retriever
from app.schemas.pydanticschema import LearningRoadmap
import json
from typing import Dict, List,Any
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

@tool
def search_courses(query: str, level: str, category: str):
    """
    Search the course catalog for relevant modules based on a skill query, 
    difficulty level, and technical category.
    
    Args:
        query: The semantic search term (e.g., 'FastAPI', 'PostgreSQL', 'Docker').
        level: The difficulty level required ('beginner', 'intermediate', or 'strong').
        category: The technical domain ('Backend', 'Frontend', 'DevOps', 'Cybersecurity', 'Database', 'ML').
    """
    
    # Using the hybrid search logic you perfected
    # The '$and' ensures the agent gets EXACTLY what fits the candidate's level
    results = retriever.invoke(
        query, 
        filter={
            "$and": [
                {"level": level},
                {"category": category}
            ]
        }
    )

    if not results:
        return f"No {level} level courses found in the {category} category for '{query}'."

    # Format the output so the Agent can read the metadata easily
    formatted_output = []
    for doc in results:
        course_info = (
            f"ID: {doc.metadata.get('course_id')}\n"
            f"Title: {doc.metadata.get('title')}\n"
            f"Description: {doc.page_content}\n"
            f"Prerequisites: {doc.metadata.get('prerequisites')}\n"
            f"Duration: {doc.metadata.get('duration')} hours\n"
            "---"
        )
        formatted_output.append(course_info)

    return "\n".join(formatted_output)



@tool(args_schema=LearningRoadmap)
def submit_final_roadmap(candidate_name, target_role, roadmap, onboarding_summary):
    """
    STRICTLY call this tool to submit the final structured learning roadmap.
    This saves the data to the global system and the graph state.
    """
    
    result = {
        "candidate_name": candidate_name,
        "target_role": target_role,
        "onboarding_summary": onboarding_summary,
        "roadmap": [
            step.model_dump() if hasattr(step, "model_dump") else step 
            for step in roadmap
        ]
    }
    
    
    
    # Return to LangGraph (will be stored in state via a post-processing node)
    return result


@tool
def submit_mermaid_visualization(mermaid_code: str):
    """
    STRICTLY call this tool to save the Mermaid.js visualization of the roadmap.
    """
    # 1. Tell Python to use the variable from the outer scope
    
    
    # 2. Now this assignment updates the global variable
    mermaid_roadmap_code = mermaid_code
    
    return "Mermaid visualization stored successfully."





class CourseLookup:
    def __init__(self, catalog_path: str = "course_catalog.json"):
        self.catalog_path = catalog_path
        self.courses_map = {}
        self._load_catalog()

    def _load_catalog(self):
        """Loads the catalog into a dictionary for O(1) lookup speed."""
        try:
            with open(self.catalog_path, 'r') as f:
                catalog = json.load(f)
                # Key the dictionary by course_id for instant retrieval
                self.courses_map = {course['course_id']: course for course in catalog}
        except FileNotFoundError:
            print(f"Error: {self.catalog_path} not found.")
        except json.JSONDecodeError:
            print(f"Error: Failed to decode {self.catalog_path}.")

    def get_course_details(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full details of a course by its ID."""
        return self.courses_map.get(course_id)

DATA_PATH = BASE_DIR / "Catalog.json"

if DATA_PATH.exists():
    lookup_service = CourseLookup(DATA_PATH)

else:
    raise FileNotFoundError(f"Catalog file not found: {DATA_PATH}")

     


@tool
def get_course_by_id(course_id: str) -> str:
    """
    Retrieves full details for a specific course using its unique course_id.
    Use this tool when you find a prerequisite ID in another course and 
    need to fetch its title, description, and duration to add to the roadmap.
    """
    details = lookup_service.get_course_details(course_id)
    if not details:
        return f"Error: Course with ID {course_id} not found in catalog."
    
    # Return a clean string for the agent to process
    return json.dumps(details, indent=2)


roadmap_planner_agent_tools=[search_courses, get_course_by_id,submit_final_roadmap,submit_mermaid_visualization]
