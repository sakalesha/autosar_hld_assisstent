from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings

# Create the SQLAlchemy engine.
# If using SQLite (e.g. for local dev), we disable "check_same_thread" to allow FastAPI 
# background tasks and multiple threads to share the connection safely.
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# SessionLocal is a factory for generating new database sessions.
# autocommit=False ensures transactions aren't committed automatically, 
# letting us manually handle commit() and rollback().
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the declarative base class that all ORM models will inherit from.
Base = declarative_base()

def get_db():
    """
    Dependency generator for FastAPI endpoints.
    Provides a per-request database session and ensures it is safely closed
    after the request is complete, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
