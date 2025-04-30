"""
Handles DB connection, table definitions, and session setup
"""

from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# === File location ===
DB_PATH: Path = Path(r'X/rma_database/rma.db')
DATABASE_URL: str = f'sqlite:///{DB_PATH.as_posix()}'

# === SQLAlchemy setup ===
engine: Engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# === Initialization function ===
def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
