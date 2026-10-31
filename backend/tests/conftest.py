import os
import shutil
import tempfile
from dotenv import load_dotenv, dotenv_values
import pytest

# Load environment variables from .env
load_dotenv("backend/.env")
load_dotenv(".env")

# Configure isolated test environment variables BEFORE importing application modules
TEST_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "careerlens_test.db"))
TEST_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "careerlens_test_uploads")

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"
os.environ["UPLOAD_DIR"] = TEST_UPLOAD_DIR
os.environ["ENVIRONMENT"] = "development"

# Ensure test upload directories exist
os.makedirs(os.path.join(TEST_UPLOAD_DIR, "resumes"), exist_ok=True)
os.makedirs(os.path.join(TEST_UPLOAD_DIR, "certificates"), exist_ok=True)

from app.core.database import Base, engine, SessionLocal
from app.seed.seed_data import seed_database_if_empty
from app.main import run_sqlite_migrations

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Session-wide fixture that guarantees tables and baseline demo seed data
    are created inside an isolated test database, and safely cleaned up upon completion.
    """
    Base.metadata.create_all(bind=engine)
    run_sqlite_migrations()
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()

    yield

    # Teardown: close engine connections and remove isolated test database and upload directory
    engine.dispose()
    for f in [TEST_DB_FILE, f"{TEST_DB_FILE}-wal", f"{TEST_DB_FILE}-shm"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass
    if os.path.exists(TEST_UPLOAD_DIR):
        shutil.rmtree(TEST_UPLOAD_DIR, ignore_errors=True)

@pytest.fixture(scope="session")
def admin_credentials():
    # Dynamically load admin credentials from local .env files without hardcoding
    env_vals = {}
    for p in ["backend/.env", ".env"]:
        if os.path.exists(p):
            env_vals = dotenv_values(p)
            if env_vals.get("PLATFORM_ADMIN_PASSWORD"):
                break

    email = os.getenv("PLATFORM_ADMIN_EMAIL") or env_vals.get("PLATFORM_ADMIN_EMAIL", "superadmin@careerlens.io")
    password = os.getenv("PLATFORM_ADMIN_PASSWORD") or env_vals.get("PLATFORM_ADMIN_PASSWORD", "")
    return {"email": email, "password": password}
