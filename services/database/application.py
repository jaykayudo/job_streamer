from storage.core.models import Application
from storage.core.engine import session
from typing import List, Optional
from conf.settings import Modules, SETTINGS

import os


class ApplicationService:
    @classmethod
    def get_applications(cls, platform: Optional[Modules] = None) -> List[Application]:
        """
        Get all applications from the database

        Args:
            platform (Optional[Modules], optional): The platform to filter by. Defaults to None.

        Returns:
            List[Application]: The applications
        """
        query = session.query(Application)
        if platform:
            print("platform", platform)
            query = query.filter_by(platform=platform)
        return query.all()

    @classmethod
    def get_application_by_id(cls, application_id: str) -> Optional[Application]:
        """
        Get an application from the database by id
        """
        return session.query(Application).filter_by(id=application_id).first()

    @classmethod
    def create_application(
        cls,
        platform: Modules,
        job_title: str,
        job_description: str,
        job_url: str,
        job_location: str,
        application_detail_file_path: str,
        job_salary: Optional[str] = None,
        job_company: Optional[str] = None,
        job_company_url: Optional[str] = None,
    ) -> Application:
        """
        Create an job application in the database
        """
        full_fill_path = os.path.join(SETTINGS.FILES_DIR, application_detail_file_path)
        application = Application(
            platform=platform,
            job_title=job_title,
            job_description=job_description,
            job_url=job_url,
            job_location=job_location,
            application_detail_file_path=full_fill_path,
            job_salary=job_salary,
            job_company=job_company,
            job_company_url=job_company_url,
        )
        application.save()
        return application
