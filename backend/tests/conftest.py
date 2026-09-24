import pytest
from app.core.database import Base, engine, SessionLocal
from app.seed.seed_data import seed_database_if_empty

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Session-wide fixture that guarantees tables and baseline demo seed data
    are created before any test runs.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()
    yield
