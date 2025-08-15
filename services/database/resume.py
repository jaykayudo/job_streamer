from storage.core.models import Resume
from typing import List
from storage.core.engine import session
from conf.settings import SETTINGS

import os


class ResumeService:
    @classmethod
    def get_resumes(cls) -> List[Resume]:
        """
        Get all resumes from the database
        """
        return session.query(Resume).all()

    @classmethod
    def create_resume(cls, name: str, file_path: str) -> Resume:
        """
        Create a resume in the database
        """
        full_fill_path = os.path.join(SETTINGS.RESUMES_DIR, file_path)
        resume = Resume(name=name, file_path=full_fill_path)
        resume.save()
        session.refresh(resume)
        return resume

    @classmethod
    def get_resume(cls, name: str) -> Resume | None:
        """
        Get a resume from the database
        """
        return session.get(Resume, {"name": name})

    @classmethod
    def delete_resume(cls, name: str) -> None:
        """
        Delete a resume from the database
        """
        resume = session.get(Resume, {"name": name})
        if resume:
            resume.delete()
