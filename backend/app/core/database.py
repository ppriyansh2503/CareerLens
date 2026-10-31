import os
import sys
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Test Isolation Safety Guard
if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
    db_url = settings.DATABASE_URL.lower()
    is_test_db = ("test" in db_url or db_url.endswith("_test.db") or db_url == "sqlite:///:memory:")
    assert is_test_db, (
        f"CRITICAL TEST ISOLATION FAILURE: Automated test execution attempted against non-test database: {settings.DATABASE_URL}. "
        f"Tests must execute strictly against an isolated test database (e.g. careerlens_test.db or :memory:)."
    )

# SQLite connection args
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Enable SQLite WAL Mode (Write-Ahead Logging) and Foreign Keys for concurrency and reliability
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
