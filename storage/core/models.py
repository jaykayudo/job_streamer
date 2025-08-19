from sqlalchemy import Column, String, ForeignKey, Table, DateTime
from storage.core.engine import BaseModel
from sqlalchemy.orm import relationship, Mapped
from typing import List

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


class Resume(BaseModel):
    __tablename__ = "resumes"
    name = Column(String(255), nullable=False, unique=True)
    path = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Resume {self.name}>"


class Bio(BaseModel):
    __tablename__ = "bios"
    name = Column(String(255), nullable=False)
    bio = Column(String(255), nullable=False)
    projects = relationship("Project", back_populates="bio")
    work_experiences = relationship("WorkExperience", back_populates="bio")

    def __repr__(self):
        return f"<Bio {self.name}>"


class Category(BaseModel):
    __tablename__ = "categories"
    name = Column(String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class SavedPreference(BaseModel):
    __tablename__ = "saved_preferences"
    name = Column(String(255), nullable=False)
    module_name = Column(String(255), nullable=False)
    preferences: Mapped[List[Category]] = relationship(
        "Category", secondary=category_preferences
    )

    def __repr__(self):
        return f"<SavedPreference {self.name}>"


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
