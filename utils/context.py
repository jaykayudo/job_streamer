from pydantic import BaseModel
from typing import List, Optional
from conf.settings import Modules
from storage.core.models import Bio
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

    platform: Modules
    bio: Bio | str | None = None
    categories: List[Category]
    locations: List[Location]
    skills: Optional[List[Skill]] = None
    hiring_types: Optional[List[HiringType]] = None
    industries: Optional[List[Industry]] = None
    work_style: Optional[WorkStyle] = None
    salary_range: Optional[SalaryRange] = None
    job_count: int
