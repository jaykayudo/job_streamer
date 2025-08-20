from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List, Optional
from conf.settings import Modules
from storage.core.models import Bio, Resume
from automation.core.automator.types import (
    Category,
    Location,
    Skill,
    HiringType,
    Industry,
)
from utils.types import SalaryRange, WorkStyle


class AutomationRequestContext(BaseModel):
    """
    Represent the context of a job automation request
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    platform: Modules
    bio: Bio | str | None = None
    categories: List[Category]
    locations: List[Location]
    resume: Resume
    skills: Optional[List[Skill]] = None
    hiring_types: Optional[List[HiringType]] = None
    industries: Optional[List[Industry]] = None
    work_style: Optional[WorkStyle] = None
    salary_range: Optional[SalaryRange] = None
    job_count: int
    extra_job_selection_intruction: Optional[str] = None

    @field_serializer("bio")
    def serialize_bio(self, bio: Bio | str | None, _info) -> str:
        if isinstance(bio, Bio):
            return bio.json_dump()
        return bio

    @field_serializer("resume")
    def serialize_resume(self, resume: Resume, _info) -> str:
        return resume.json_dump()
