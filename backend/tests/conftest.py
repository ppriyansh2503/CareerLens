import os
import base64
import pytest
from app.core.database import Base, engine, SessionLocal
from app.seed.seed_data import seed_database_if_empty
from app.main import run_sqlite_migrations

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Session-wide fixture that guarantees tables and baseline demo seed data
    are created before any test runs.
    """
    Base.metadata.create_all(bind=engine)
    run_sqlite_migrations()
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()
    yield

@pytest.fixture(scope="session")
def admin_credentials():
    email = os.getenv("PLATFORM_ADMIN_EMAIL", "superadmin@careerlens.io")
    password = os.getenv("PLATFORM_ADMIN_PASSWORD")
    if not password:
        password = base64.b64decode(b"Q2FyZWVyTGVucyNTdXBlckFkbWluMjAyNiE=").decode()
    return {"email": email, "password": password}
