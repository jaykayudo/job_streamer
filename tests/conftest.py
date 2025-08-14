import pytest
from sqlalchemy import create_engine
from storage.core.engine import BaseModel, sessionmaker

@pytest.fixture(scope="session")
def engine():
    """Create a temporary database engine for testing."""
    # SQLite in-memory for speed; replace with PostgreSQL if needed
    return create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture(scope="session")
def tables(engine):
    """Create all tables once for the session."""
    BaseModel.metadata.create_all(engine)
    yield
    BaseModel.metadata.drop_all(engine)


@pytest.fixture()
def db_session(engine, tables):
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()