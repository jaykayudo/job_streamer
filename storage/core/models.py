from sqlalchemy import Column, String, ForeignKey, Table
from storage.core.engine import BaseModel
from sqlalchemy.orm import relationship

category_preferences = Table(
    "category_preferences",
    BaseModel.metadata,
    Column("category_id", String, ForeignKey("categories.id"), primary_key=True),
    Column("saved_preference_id", String, ForeignKey("saved_preferences.id"), primary_key=True),
)

class Application(BaseModel):
    __tablename__ = "applications"
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
    
    def __repr__(self):
        return f"<Bio {self.name}>"

class Category(BaseModel):
    __tablename__ = "categories"
    name = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<Category {self.name}>"


class SavedPreference(BaseModel):
    __tablename__ = "saved_preferences"
    name = Column(String(255), nullable=False)
    module_name = Column(String(255), nullable=False)
    preferences = relationship("Category", secondary=category_preferences)
    
    def __repr__(self):
        return f"<SavedPreference {self.name}>"
    

    