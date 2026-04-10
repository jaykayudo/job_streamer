from sqlalchemy import Boolean, Column, String, ForeignKey, Table, DateTime, Text
from storage.core.engine import BaseModel
from sqlalchemy.orm import relationship, Mapped
from typing import List, Dict, Any

category_preferences = Table(
    "category_preferences",
    BaseModel.metadata,
    Column("category_id", String, ForeignKey("categories.id"), primary_key=True),
    Column(
        "saved_preference_id",
        String,
        ForeignKey("saved_preferences.id"),
        primary_key=True,
    ),
)


class Application(BaseModel):
    __tablename__ = "applications"
    platform = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(String(255), nullable=False)
    job_url = Column(String(255), nullable=False)
    job_location = Column(String(255), nullable=False)
    job_salary = Column(String(255), nullable=True)
    job_company = Column(String(255), nullable=True)
    job_company_url = Column(String(255), nullable=True)
    application_detail_file_path = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Application {self.job_title}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "job_title": self.job_title,
            "platform": self.platform,
            "job_description": self.job_description,
            "job_url": self.job_url,
            "job_location": self.job_location,
            "job_salary": self.job_salary,
            "job_company": self.job_company,
            "job_company_url": self.job_company_url,
            "application_detail_file_path": self.application_detail_file_path,
        }


class Resume(BaseModel):
    __tablename__ = "resumes"
    name = Column(String(255), nullable=False, unique=True)
    path = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Resume {self.name}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "name": self.name,
            "path": self.path,
        }


class Bio(BaseModel):
    __tablename__ = "bios"
    name = Column(String(255), nullable=False)
    bio = Column(String(255), nullable=False)
    projects = relationship("Project", back_populates="bio")
    work_experiences = relationship("WorkExperience", back_populates="bio")

    def __repr__(self):
        return f"<Bio {self.name}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "name": self.name,
            "bio": self.bio,
            # "projects": [project.json_dump() for project in self.projects], # removing all this due to recursive dump
            # "work_experiences": [
            #     work_experience.json_dump() for work_experience in self.work_experiences
            # ],
        }


class Category(BaseModel):
    __tablename__ = "categories"
    name = Column(String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<Category {self.name}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "name": self.name,
        }


class SavedPreference(BaseModel):
    __tablename__ = "saved_preferences"
    name = Column(String(255), nullable=False)
    module_name = Column(String(255), nullable=False)
    preferences: Mapped[List[Category]] = relationship(
        "Category", secondary=category_preferences
    )

    def __repr__(self):
        return f"<SavedPreference {self.name}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "name": self.name,
            "module_name": self.module_name,
            "preferences": [category.json_dump() for category in self.preferences],
        }


class Project(BaseModel):
    __tablename__ = "projects"
    bio_id = Column(String(36), ForeignKey("bios.id"), nullable=False)
    bio: Mapped[Bio] = relationship("Bio", back_populates="projects")
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    tools = Column(String(255), nullable=False)
    impact = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Project {self.name}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "bio": self.bio.json_dump(),
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "impact": self.impact,
        }


class WorkExperience(BaseModel):
    __tablename__ = "work_experiences"
    bio_id = Column(String(36), ForeignKey("bios.id"), nullable=False)
    bio: Mapped[Bio] = relationship("Bio", back_populates="work_experiences")
    company_name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<WorkExperience {self.company_name}>"

    def json_dump(self) -> Dict[str, Any]:
        return {
            **super().json_dump(),
            "bio": self.bio.json_dump(),
            "company_name": self.company_name,
            "role": self.role,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
        }


class JobHunt(BaseModel):
    """
    Persisted record of a job automation run.
    Complex list fields (categories, locations, skills, hiring_types, industries)
    are stored as JSON text since SQLite has no native array type.
    Bio and Resume are stored as foreign keys to their respective tables.
    """
    __tablename__ = "job_hunts"

    platform = Column(String(255), nullable=False)
    bio_id = Column(String(36), ForeignKey("bios.id"), nullable=True)
    bio: Mapped["Bio"] = relationship("Bio")
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    resume: Mapped["Resume"] = relationship("Resume")
    # JSON-serialised lists of automation type objects
    categories = Column(Text, nullable=False, default="[]")
    locations = Column(Text, nullable=False, default="[]")
    skills = Column(Text, nullable=True)
    hiring_types = Column(Text, nullable=True)
    industries = Column(Text, nullable=True)
    # Simple scalar fields
    work_style = Column(String(50), nullable=True)
    salary_min = Column(Text, nullable=True)
    salary_max = Column(Text, nullable=True)
    job_count = Column(Text, nullable=False)
    extra_job_selection_intruction = Column(Text, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<JobHunt {self.platform} completed={self.completed}>"

    def json_dump(self) -> Dict[str, Any]:
        import json as _json

        def _load(value):
            if value is None:
                return None
            try:
                return _json.loads(value)
            except (TypeError, ValueError):
                return value

        return {
            **super().json_dump(),
            "platform": self.platform,
            "bio": self.bio.json_dump() if self.bio else None,
            "resume": self.resume.json_dump() if self.resume else None,
            "categories": _load(self.categories),
            "locations": _load(self.locations),
            "skills": _load(self.skills),
            "hiring_types": _load(self.hiring_types),
            "industries": _load(self.industries),
            "work_style": self.work_style,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "job_count": self.job_count,
            "extra_job_selection_intruction": self.extra_job_selection_intruction,
            "completed": self.completed,
        }
