from pydantic import BaseModel
from enum import Enum
from typing import Callable, TypeAlias


class SelectionType(Enum):
    """
    Represent the type of selection for a field to the client
    """

    SINGLE = "single"
    MULTIPLE = "multiple"


class WorkStyle(Enum):
    """
    Represent the work style of a job
    """

    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class ClientType(Enum):
    CMD = "cmd"
    WEB = "web"


Reader: TypeAlias = Callable[[str], str]


class SalaryRange(BaseModel):
    """
    Represent a salary range
    """

    min: int
    max: int
