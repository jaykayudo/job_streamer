from enum import Enum
from pydantic import BaseModel
from typing import Literal, Optional

from conf.settings import Modules


SELECTOR_TYPE = Literal["xpath", "css", "id", "class", "name", "tag", "attribute"]


class BaseModelWithUniqueId(BaseModel):
    """
    Represent a model with a unique id
    """

    id: Optional[str] = None
    unique_selector: str  # xpath, css, etc. for finding the element
    selector_type: SELECTOR_TYPE


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


class JobApplicationDetails(BaseModelWithUniqueId):
    """
    Represent the details of a job application form field
    """

    title: str
    extra_description: Optional[str] = None
    element_type: InputElementType

    def __str__(self):
        return self.title


class JobApplicationDetailsAnswer(BaseModelWithUniqueId):
    """
    Represent the answer to a job application form field
    """

    application_details: JobApplicationDetails
    value: str

    def __str__(self):
        return self.application_details.title


class HiringType(BaseModelWithUniqueId):
    """
    Represent a hiring type
    """

    id: Optional[str] = None
    name: str

    def __str__(self):
        return self.name


class Industry(BaseModelWithUniqueId):
    """
    Represent an industry
    """

    id: Optional[str] = None
    name: str

    def __str__(self):
        return self.name


class Skill(BaseModelWithUniqueId):
    """
    Represent a skill
    """

    id: Optional[str] = None
    name: str

    def __str__(self):
        return self.name


class Location(BaseModelWithUniqueId):
    """
    Represent a location
    """

    id: Optional[str] = None
    name: str

    def __str__(self):
        return self.name


class Category(BaseModelWithUniqueId):
    """
    Represent a category
    """

    id: Optional[str] = None
    name: str

    def __str__(self):
        return self.name
