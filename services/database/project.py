from storage.core.models import Project
from typing import List
from storage.core.engine import session


class ProjectService:
    @classmethod
    def create_project(
        cls,
        bio_id: str,
        name: str,
        description: str,
        tools: str,
        impact: str | None = None,
    ) -> Project:
        """
        Create a project in the database
        """
        project = Project(
            bio_id=bio_id,
            name=name,
            description=description,
            tools=tools,
            impact=impact,
        )
        project.save()
        return project

    @classmethod
    def get_projects(cls, bio_id: str) -> List[Project]:
        """
        Get all projects from the database
        """
        return session.query(Project).filter_by(bio_id=bio_id).all()

    @classmethod
    def delete_project(cls, project_id: str) -> None:
        """
        Delete a project from the database
        """
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            project.delete()

    @classmethod
    def get_all_projects(cls) -> List[Project]:
        """
        Get all projects from the database
        """
        return session.query(Project).all()
