from storage.core.models import WorkExperience
from typing import List
from storage.core.engine import session


class WorkExperienceService:
    @classmethod
    def create_work_experience(
        cls,
        bio_id: str,
        company_name: str,
        role: str,
        start_date: str,
        end_date: str | None = None,
        description: str | None = None,
    ) -> WorkExperience:
        """
        Create a work experience in the database
        """
        work_experience = WorkExperience(
            bio_id=bio_id,
            company_name=company_name,
            role=role,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )
        work_experience.save()
        return work_experience

    @classmethod
    def get_work_experiences(cls, bio_id: str) -> List[WorkExperience]:
        """
        Get all work experiences from the database
        """
        return session.query(WorkExperience).filter_by(bio_id=bio_id).all()

    @classmethod
    def get_work_experience_by_id(cls, work_experience_id: str) -> WorkExperience | None:
        """
        Get a work experience from the database by id
        """
        return session.query(WorkExperience).filter_by(id=work_experience_id).first()

    @classmethod
    def delete_work_experience(cls, work_experience_id: str) -> None:
        """
        Delete a work experience from the database
        """
        work_experience = (
            session.query(WorkExperience).filter_by(id=work_experience_id).first()
        )
        if work_experience:
            work_experience.delete()

    @classmethod
    def get_all_work_experiences(cls) -> List[WorkExperience]:
        """
        Get all work experiences from the database
        """
        return session.query(WorkExperience).all()
