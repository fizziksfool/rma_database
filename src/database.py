"""
Handles DB connection, table definitions, and session setup
"""

from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Boolean,
    DateTime,
    Engine,
    ForeignKey,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.sql import func

# === File location ===
DB_PATH: Path = Path(r'X/rma_database/rma.db')
DATABASE_URL: str = f'sqlite:///{DB_PATH.as_posix()}'

# === SQLAlchemy setup ===
engine: Engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    rmas: Mapped[list['RMA']] = relationship(back_populates='customer')


class Department(Base):
    __tablename__ = 'departments'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    rmas: Mapped[list['RMA']] = relationship(back_populates='department')


class ProductDescription(Base):
    __tablename__ = 'product_descriptions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    products: Mapped[list['ProductNumber']] = relationship(back_populates='description')


class ProductNumber(Base):
    __tablename__ = 'product_numbers'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(50), unique=True)
    description_id: Mapped[int] = mapped_column(ForeignKey('product_descriptions.id'))

    description: Mapped['ProductDescription'] = relationship(back_populates='products')
    rmas: Mapped[list['RMA']] = relationship(back_populates='product_number')


class RMA(Base):
    __tablename__ = 'rmas'

    rma_number: Mapped[str] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'))
    product_number_id: Mapped[int] = mapped_column(ForeignKey('product_numbers.id'))

    serial_number: Mapped[str] = mapped_column(String(50))
    is_warranty: Mapped[bool] = mapped_column(Boolean)
    reason_for_return: Mapped[str] = mapped_column(Text)
    work_order: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String, default='Issued')
    created_by: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    customer_po_number: Mapped[str] = mapped_column(String(50))
    incoming_inspection_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    shipped_back_on: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    customer: Mapped['Customer'] = relationship(back_populates='rmas')
    department: Mapped['Department'] = relationship(back_populates='rmas')
    product_number: Mapped['ProductNumber'] = relationship(back_populates='rmas')

    @property
    def product(self) -> str:
        return self.product_number.description.name


# === Initialization function ===
def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    initialize_database()
