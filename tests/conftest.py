import pytest
from storage.core.engine import BaseModel, sessionmaker
from storage.core.engine import engine as main_engine


@pytest.fixture(scope="function")
def engine():
    """Create a temporary database engine for testing."""
    # SQLite in-memory for speed; replace with PostgreSQL if needed
    # TODO: figure out how to mock the session for the test
    return main_engine  # remove this when we figure out how to mock the session properly for the test


@pytest.fixture(scope="function")
def tables(engine):
    """Create all tables once for the session."""
    BaseModel.metadata.create_all(engine)
    yield
    BaseModel.metadata.drop_all(engine)


@pytest.fixture()
def db_session(engine, tables, monkeypatch):
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    # TODO: figure out how to mock the session properly for the test
    monkeypatch.setattr("storage.core.engine.session", session)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
