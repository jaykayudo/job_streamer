from typing import Annotated, Dict, List, Optional, TypedDict, Union, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from automation.core.automator.types import (
    Category,
    Location,
    Skill,
    HiringType,
    Industry,
    JobApplicationDetails,
    JobApplicationDetailsAnswer,
    JobDetails,
)
from storage.core.models import Application, Resume, Bio, SavedPreference
from conf.settings import Modules
from pydantic import BaseModel

from utils.types import WorkStyle, SalaryRange


class AgentState(TypedDict):
    """
    A dictionary representing the state of an agent.
    """
    platform: Modules
    messages: Annotated[Sequence[BaseMessage], add_messages]
    resume_object: Resume
    bio_object: Bio
    preferences_object: SavedPreference
    categories: List[Category]
    job_details: List[JobDetails]
    # Maps job URL -> list of application form questions (populated by questions retrieval node)
    job_application_details: Optional[Dict[str, List[JobApplicationDetails]]]
    # Maps job URL -> list of LLM-generated answers (populated by questions answering node)
    job_application_answers: Optional[Dict[str, List[JobApplicationDetailsAnswer]]]
    # URLs of jobs successfully applied to (populated by application node)
    applied_jobs: Optional[List[str]]
    location: Optional[Location]
    skills: Optional[List[Skill]]
    hiring_types: Optional[List[HiringType]]
    industries: Optional[List[Industry]]
    work_style: Optional[WorkStyle]
    salary_range: Optional[SalaryRange]
    job_count: int
    extra_job_selection_intruction: Optional[str]
    

class Configuration(BaseModel):
    """
    A class representing the configuration of the appli.
    """
    job_hunt_id: str
    platform: Modules
    bio_id: Optional[str] = None
    resume_id: Optional[str] = None
    preferences_id: Optional[str] = None


class FullConfiguration(TypedDict):
    """
    A class representing the full configuration of the application, with all the objects.
    """
    resume_object: Optional[Resume] = None
    bio_object: Optional[Bio] = None
    preferences_object: Optional[SavedPreference] = None