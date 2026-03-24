from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class SkillRequirement(BaseModel):
    name: str = Field(
        ...,
        description="Skill or technology required for the job (e.g., Python, SQL, React)"
    )
    level: Optional[str] = Field(
        None,
        description="Expected proficiency level: beginner | intermediate | strong"
    )


class ResponsibilityItem(BaseModel):
    description: str = Field(
        ...,
        description="Key responsibility or task expected from the candidate"
    )


class RequirementItem(BaseModel):
    description: str = Field(
        ...,
        description="Qualification or requirement such as education, availability, etc."
    )


class ConstraintItem(BaseModel):
    type: str = Field(
        ...,
        description="Constraint type such as location, duration, eligibility"
    )
    value: str = Field(
        ...,
        description="Constraint value (e.g., 'Pune only', '6 months', 'Fresher')"
    )



class JobDescriptionExtract(BaseModel):
    job_title: Optional[str] = Field(
        None,
        description="Job role/title (e.g., AI/ML Intern, Web Developer)"
    )

    company_name: Optional[str] = Field(
        None,
        description="Company offering the job"
    )

    location: Optional[str] = Field(
        None,
        description="Job location if specified"
    )

    employment_type: Optional[str] = Field(
        None,
        description="Type of job: internship, full-time, contract"
    )

    duration_months: Optional[int] = Field(
        None,
        description="Duration of role in months (for internships/contracts)"
    )

    is_fresher_allowed: Optional[bool] = Field(
        None,
        description="Whether freshers are eligible for this role"
    )

    skills_required: Optional[List[SkillRequirement]] = Field(
        None,
        description="List of required skills and expected levels"
    )

    tools_technologies: Optional[List[str]] = Field(
        None,
        description="Specific tools/frameworks mentioned (e.g., Pandas, WordPress)"
    )

    responsibilities: Optional[List[ResponsibilityItem]] = Field(
        None,
        description="Key job responsibilities"
    )

    requirements: Optional[List[RequirementItem]] = Field(
        None,
        description="General requirements like availability, qualifications"
    )

    constraints: Optional[List[ConstraintItem]] = Field(
        None,
        description="Special constraints like location restriction, duration, etc."
    )



class Skill(BaseModel):
    name: str = Field(..., description="Skill name e.g. Python, Docker")
    category: Optional[str] = Field(
        None, description="Category: Backend | ML | DevOps | Frontend | Other"
    )


class ExperienceItem(BaseModel):
    job_title: str = Field(
        ...,
        description="Role title of the candidate. Example: 'Backend Intern', 'Software Engineer'"
    )

    experience_type: Optional[Literal['internship', 'full_time', 'contract', 'freelance']] = Field(
        None,
        description="Type of experience: internship, full_time, contract, or freelance"
    )

    technologies: Optional[List[str]] = Field(
        default_factory=list,
        description="Technologies, tools, or frameworks used in this role"
    )

    responsibilities: Optional[List[str]] = Field(
        default_factory=list,
        description="Key responsibilities, tasks, or learnings in concise bullet points"
    )

class ProjectItem(BaseModel):
    name: str = Field(..., description="Project name")
    technologies: List[str] = Field(
        default_factory=list,
        description="Technologies used in this project ,hence learned in the project"
    )
  


class CertificationItem(BaseModel):
    name: str = Field(..., description="Certification name")
    
    topics_covered: List[str] = Field(
        default_factory=list,
        description="Key topics or skills the certification covers"
    )






class ResumeExtract(BaseModel):


    candidate_name:Optional[str]

    
    job_title: Optional[str] = Field(
    None,
    description=(
        "Primary job title or role of the candidate. "
        "Examples: 'AI Engineer', 'Data Scientist', "
        "'Construction Project Manager', 'Healthcare Representative'. "
        "Should reflect the most recent or current role."
       )
    )

    
    

   

   
    skills: List[Skill] = Field(
        default_factory=list,
        description="Skills explicitly listed by the candidate"
    )
    experience: List[ExperienceItem] = Field(
        default_factory=list,
        description=(
            "Each role as a separate entry. "
            "No company name needed — focus on what was done and learned."
        )
    )
    projects: List[ProjectItem] = Field(
        default_factory=list,
        description="Projects with technologies used and what was built"
    )
    certifications: Optional[List[CertificationItem]] = Field(
        None,
        description="Certifications with topics they cover. None if not present."
    )
   


    is_fresher: bool = Field(
    ...,
    description=(
        "Set to True if the candidate lacks full-time professional employment. "
        "Academic projects, certifications, and internships are considered "
        "part of the learning phase and do not qualify a candidate as 'non-fresher' hence is_."
    )
)



class SkillRequirement(BaseModel):
    name: str = Field(
        ...,
        description="Skill or technology required for the job (e.g., Python, SQL, React)"
    )
    level: Optional[str] = Field(
        None,
        description="Expected proficiency level: beginner | intermediate | strong"
    )


class ResponsibilityItem(BaseModel):
    description: str = Field(
        ...,
        description="Key responsibility or task expected from the candidate"
    )


class RequirementItem(BaseModel):
    description: str = Field(
        ...,
        description="Qualification or requirement such as education, availability, etc."
    )





class JobDescriptionExtract(BaseModel):
    job_title: Optional[str] = Field(
        None,
        description="Job role/title (e.g., AI/ML Intern, Web Developer)"
    )

    is_fresher_allowed: Optional[bool] = Field(
        None,
        description="Whether freshers are eligible for this role"
    )

    skills_required: Optional[List[SkillRequirement]] = Field(
        None,
        description="List of required skills and expected levels"
    )

    tools_technologies: Optional[List[str]] = Field(
        None,
        description="Specific tools/frameworks mentioned (e.g., Pandas, WordPress)"
    )

    responsibilities: Optional[List[ResponsibilityItem]] = Field(
        None,
        description="Key job responsibilities"
    )

    requirements: Optional[List[RequirementItem]] = Field(
        None,
        description="General requirements like availability, qualifications"
    )




class SkillGap(BaseModel):
    skill_name: str = Field(
        ..., 
        description="The specific technology or tool missing or requiring an upgrade (e.g., 'PostgreSQL')"
    )
    
    gap_type: Literal["missing_foundation", "needs_advanced_upgrade"] = Field(
        ...,
        description=(
            "missing_foundation: Candidate has no recorded experience in this core requirement. "
            "needs_advanced_upgrade: Candidate knows the basics but needs role-specific advanced training."
        )
    )
    
    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="How critical this skill is for the target job role."
    )
    
    reasoning: str = Field(
        ...,
        description=(
            "The 'Reasoning Trace'. This MUST be provided for every skill gap identified. "
            "Explain exactly WHY this gap was flagged based on the resume vs JD comparison. "
            "Example: 'JD requires FastAPI; candidate has Python experience but no record of using FastAPI framework.'"
        )
    )
    
    target_competency: str = Field(
        ...,
        description="The specific outcome the candidate needs to reach (e.g., 'Build asynchronous database endpoints')"
    )

class SkillGapAnalysis(BaseModel):
    job_title: str = Field(..., description="The target role from the JD")
    candidate_name: Optional[str] = Field(None, description="Extracted name from resume")
    
    analyzed_gaps: List[SkillGap] = Field(
        default_factory=list,
        description="List of specific technical gaps found between Resume and JD"
    )
    
    is_fresher_adaptation_needed: bool = Field(
        default=False,
        description="True if foundational corporate/soft-skill modules should be added to the path."
    )
    
    executive_summary: str = Field(
        ...,
        description="A 2-3 sentence overview of the candidate's readiness and the primary focus of the onboarding."
    )



# Schema for learning_roadmap tool
class RoadmapStep(BaseModel):
    course_id: str
    title: str
    reasoning: str = Field(..., description="Why this specific course was chosen for this user tell in short 10-15 words strictly")
    is_foundation: bool
    sequence_order: int = Field(..., description="The order in which the course should be taken")

class LearningRoadmap(BaseModel):
    candidate_name: str
    target_role: str
    roadmap: List[RoadmapStep]
    onboarding_summary: str




# Schema for search_courses tool

class SearchCourse(BaseModel):
    query:str=Field(..., description="The skill to find with  semantic terms (e.g., 'FastAPI', 'PostgreSQL', 'Docker','Enterprise VMS Strategy','Utilization Management')")