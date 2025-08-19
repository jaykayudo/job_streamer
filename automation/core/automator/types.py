from enum import Enum
from pydantic import BaseModel
from typing import Optional

from conf.settings import Modules


class InputElementType(str, Enum):
    """
    Represent a html input element type
    """

    TEXT = "text"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    TEXTAREA = "textarea"
    DATE = "date"
    TIME = "time"


class Job(BaseModel):
    """
    Represent a job from the platform
    """

    id: Optional[str] = None
    title: str
    url: str
    location: Optional[str] = None
    platform: Modules

    def __str__(self):
        return self.title


class JobDetails(BaseModel):
    """
    Represent the details of a job
    """

    job: Job
    description: str
    pay_range: Optional[str] = None
    company: Optional[str] = None
    company_description: Optional[str] = None
    posted_date: Optional[str] = None

    def __str__(self):
        return self.job.title


class JobFilter(BaseModel):
    """
    Represent a filter for a job (like a job category)
    """

    id: Optional[str] = None
    name: str

    def __str__(self):
        return self.name


class JobApplicationDetails(BaseModel):
    """
    Represent the details of a job application form field
    """

    title: str
    unique_selector: str  # xpath, css, etc. for finding the element
    extra_description: Optional[str] = None
    element_type: InputElementType

    def __str__(self):
        return self.title


class JobApplicationDetailsAnswer(BaseModel):
    """
    Represent the answer to a job application form field
    """

    application_details: JobApplicationDetails
    value: str

    def __str__(self):
        return self.application_details.title


class HiringType(BaseModel):
    """
    Represent a hiring type
    """

    id: Optional[str] = None
    name: str
    unique_selector: str

    def __str__(self):
        return self.name


class Industry(BaseModel):
    """
    Represent an industry
    """

    id: Optional[str] = None
    name: str
    unique_selector: str

    def __str__(self):
        return self.name


class Skill(BaseModel):
    """
    Represent a skill
    """

    id: Optional[str] = None
    name: str
    unique_selector: str

    def __str__(self):
        return self.name


class Location(BaseModel):
    """
    Represent a location
    """

    id: Optional[str] = None
    name: str
    unique_selector: str

    def __str__(self):
        return self.name


class Category(BaseModel):
    """
    Represent a category
    """

    id: Optional[str] = None
    name: str
    unique_selector: str

    def __str__(self):
        return self.name
