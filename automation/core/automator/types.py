from enum import Enum
from pydantic import BaseModel
from typing import Optional
from conf.settings import Modules


class ElementType(str, Enum):
    INPUT = "input"
    SELECT = "select"
    BUTTON = "button"
    LINK = "link"
    DIV = "div"
    FILE = "file"


class Job(BaseModel):
    id: Optional[str] = None
    title: str
    url: str
    location: Optional[str] = None
    module: Modules


class JobDetails(BaseModel):
    job: Job
    description: str
    pay_range: Optional[str] = None
    company: Optional[str] = None
    company_description: Optional[str] = None
    posted_date: Optional[str] = None


class JobFilter(BaseModel):
    id: Optional[str] = None
    name: str


class JobApplicationDetails(BaseModel):
    title: str
    unique_selector: str  # xpath, css, etc. for finding the element
    extra_description: Optional[str] = None
    element_type: ElementType


class JobApplicationDetailsAnswer(BaseModel):
    application_details: JobApplicationDetails
    value: str
