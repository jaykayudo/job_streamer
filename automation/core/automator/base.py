from abc import ABC, abstractmethod
from typing import List, Optional
from automation.core.automator.types import (
    Job,
    JobApplicationDetailsAnswer,
    JobDetails,
    JobFilter,
    JobApplicationDetails,
    HiringType,
    Industry,
    Skill,
    Location,
    Category,
)
from utils.types import Reader, SelectionType


class BaseAutomator(ABC):
    @abstractmethod
    def login(self, reader: Reader):
        """
        Login to the platform
        """
        pass

    @abstractmethod
    def logout(self):
        """
        Logout from the platform
        """
        pass

    @abstractmethod
    def get_categories(self) -> tuple[List[Category], SelectionType]:
        """
        Get the job categories of the platform
        """
        pass

    @abstractmethod
    def get_locations(self) -> tuple[List[Location], SelectionType]:
        """
        Get the locations of the platform
        """
        pass

    @abstractmethod
    def get_skills(self) -> tuple[List[Skill], SelectionType] | None:
        """
        Get the skills of the platform
        """
        pass

    @abstractmethod
    def get_hiring_types(self) -> tuple[List[HiringType], SelectionType] | None:
        """
        Get the hiring types of the platform
        """
        pass

    @abstractmethod
    def get_industries(self) -> tuple[List[Industry], SelectionType] | None:
        """
        Get the industries of the platform
        """
        pass

    @abstractmethod
    def get_jobs(
        self, count: Optional[int] = None, filters: Optional[List[JobFilter]] = None
    ) -> List[Job]:
        """
        Get jobs from the platform
        """
        pass

    @abstractmethod
    def get_job_details(self, job: Job) -> JobDetails:
        """
        Get the details of a job
        """
        pass

    @abstractmethod
    def get_job_application_details(
        self, job: JobDetails
    ) -> List[JobApplicationDetails]:
        """
        Get the application details of a job
        """
        pass

    def apply_filters(self, filters: List[JobFilter]) -> List[Job]:
        """
        Apply filters to the jobs
        """
        pass

    @abstractmethod
    def search_jobs(self, query: str) -> List[Job]:
        """
        Search for jobs on the platform
        """
        pass

    @abstractmethod
    def apply_job(
        self, job: JobDetails, application_details: List[JobApplicationDetailsAnswer]
    ) -> bool:
        """
        Apply to a job
        """
        pass
