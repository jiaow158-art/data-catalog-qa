import os
import sys
import pytest

# Allow import of app from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import *  # noqa: F401, F403 - register all models

# Override DATABASE_URL before importing config
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.core.config import settings  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    e = create_engine("sqlite:///./test.db", echo=False)
    Base.metadata.create_all(bind=e)
    yield e
    Base.metadata.drop_all(bind=e)


@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
