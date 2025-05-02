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
    configure_mappers,
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


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    rmas: Mapped[list['RMA']] = relationship(back_populates='issued_by')


class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    rmas: Mapped[list['RMA']] = relationship(back_populates='customer')


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    part_numbers: Mapped[list['PartNumber']] = relationship(back_populates='product')


class PartNumber(Base):
    __tablename__ = 'part_numbers'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    product: Mapped['Product'] = relationship(back_populates='part_numbers')
    rmas: Mapped[list['RMA']] = relationship(back_populates='part_number')


class RMA(Base):
    __tablename__ = 'rmas'

    rma_number: Mapped[str] = mapped_column(
        primary_key=True, unique=True, nullable=False
    )

    issued_by_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), index=True)
    part_number_id: Mapped[int] = mapped_column(
        ForeignKey('part_numbers.id'), index=True
    )

    issued_by: Mapped['User'] = relationship(back_populates='rmas')
    customer: Mapped['Customer'] = relationship(back_populates='rmas')
    part_number: Mapped['PartNumber'] = relationship(back_populates='rmas')

    serial_number: Mapped[str] = mapped_column(String(50))
    is_warranty: Mapped[bool] = mapped_column(Boolean)
    reason_for_return: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String, default='Issued')
    issued_on: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), server_default=func.now(), index=True
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    customer_po_number: Mapped[str] = mapped_column(String(50), nullable=True)
    work_order: Mapped[str] = mapped_column(String(50), nullable=True)
    incoming_inspection_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    shipped_back_on: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, index=True
    )


# === Initialization function ===
def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    configure_mappers()
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    initialize_database()
