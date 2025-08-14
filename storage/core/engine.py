from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from conf.settings import Settings
from datetime import datetime
import uuid

SETTINGS = Settings()


# Create database engine
engine = create_engine(SETTINGS.DATABASE_URL, echo=True)

# Create a Session factory
SessionLocal = sessionmaker(bind=engine)

# Create a session
session = SessionLocal()


def generate_uuid():
    return str(uuid.uuid4())

# Base class for all models
class BaseModel(DeclarativeBase):
    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()
        return obj

    @classmethod
    def get_or_create(cls, **kwargs):
        obj = session.query(cls).filter_by(**kwargs).one_or_none()
        return obj if obj else cls.create(**kwargs)

    def save(self):
        session.add(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()





