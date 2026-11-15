import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ensure .env is loaded from project root
_project_root = Path(__file__).resolve().parents[2]
load_dotenv(_project_root / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://tracecho:tracecho@localhost:5432/tracecho",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
