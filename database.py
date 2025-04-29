"""
Handles DB connection, table definitions, and session setup
"""

import datetime
from pathlib import Path

from sqlalchemy import Engine, Text, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker

# === File location ===
DB_PATH: Path = Path(r'X/rma_database/rma.db')
DATABASE_URL: str = f'sqlite:///{DB_PATH.as_posix()}'

# === SQLAlchemy setup ===
engine: Engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# === Table model ===
class RMA(Base):
    __tablename__ = 'rmas'

    rma_number: Mapped[str] = mapped_column(primary_key=True)
    department: Mapped[str] = mapped_column()
    customer: Mapped[str] = mapped_column()
    product_description: Mapped[str] = mapped_column()
    product_number: Mapped[str] = mapped_column()
    serial_number: Mapped[str] = mapped_column()
    is_warranty: Mapped[bool] = mapped_column()
    reason_for_return: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(default='Issued')
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    work_order: Mapped[str] = mapped_column(nullable=True)
    customer_po_number: Mapped[str] = mapped_column(nullable=True)
    incoming_inspection_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    shipped_back_on: Mapped[datetime.datetime] = mapped_column(nullable=True)


# === Initialization function ===
def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
