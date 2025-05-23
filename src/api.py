from collections.abc import Callable
from datetime import datetime
from operator import attrgetter
from typing import Any

from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from .database import (
    RMA,
    Customer,
    PartNumber,
    Product,
    SessionLocal,
    User,
)

RMA_ATTR_ACCESSORS: dict[str, Callable[[RMA], Any]] = {
    'Cust. PO #': attrgetter('customer_po_number'),
    'Customer': attrgetter('customer.name'),
    'Date Issued': attrgetter('issued_on'),
    'Date Returned': attrgetter('shipped_back_on'),
    'Inspection Notes': attrgetter('incoming_inspection_notes'),
    'Issued By': attrgetter('issued_by.name'),
    'Last Updated': attrgetter('last_updated'),
    'Part #': attrgetter('part_number.number'),
    'Product': attrgetter('part_number.product.name'),
    'Reason for Return': attrgetter('reason_for_return'),
    'Resolution': attrgetter('resolution_notes'),
    'RMA #': attrgetter('rma_number'),
    'Serial #': attrgetter('serial_number'),
    'Status': attrgetter('status'),
    'Warranty': lambda rma: 'Yes' if rma.is_warranty else 'No',
    'Warranty_io': attrgetter('is_warranty'),
    'WO #': attrgetter('work_order'),
}


def add_customer(customer_name: str) -> bool:
    """
    Adds a customer to the database.

    Returns True if successful, False if customer already exists or input is invalid.
    """
    customer_name = customer_name.strip().lower()

    if not customer_name:
        return False

    with SessionLocal() as session:
        existing = session.query(Customer).filter_by(name=customer_name).first()
        if existing:
            return False

        try:
            new_customer = Customer(name=customer_name)
            session.add(new_customer)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def add_user(user_name: str) -> bool:
    """
    Adds a user to the database.

    Returns True if successful, False if user already exists or input is invalid.
    """
    user_name = user_name.strip().lower()

    if not user_name:
        return False

    with SessionLocal() as session:
        existing = session.query(User).filter_by(name=user_name).first()
        if existing:
            return False

        try:
            new_user = User(name=user_name)
            session.add(new_user)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def add_product(product: str, part_number: str) -> bool:
    prod = product.strip().lower()
    part_num = part_number.strip()

    if not prod or not part_num:
        return False

    with SessionLocal() as session:
        existing_product = session.query(Product).filter_by(name=prod).first()
        existing_part_num = session.query(PartNumber).filter_by(number=part_num).first()
        if existing_product or existing_part_num:
            return False

        try:
            # Add product
            new_prod = Product(name=prod)
            session.add(new_prod)
            session.flush()  # Get new_prod.id before committing

            # Add product number linked to the product
            new_number = PartNumber(number=part_num, product_id=new_prod.id)
            session.add(new_number)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def add_part_number(product_id: int, part_number: str) -> bool:
    part_num = part_number.strip()

    if not part_num:
        return False

    with SessionLocal() as session:
        existing_part_num = session.query(PartNumber).filter_by(number=part_num).first()
        if existing_part_num:
            return False

        try:
            new_number = PartNumber(number=part_num, product_id=product_id)
            session.add(new_number)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def add_rma(
    rma_number: int,
    customer_id: int,
    part_number_id: int,
    serial_number: str,
    reason_for_return: str,
    issued_by_id: int,
    is_warranty: bool,
    customer_po_number: str | None = None,
) -> bool:
    with SessionLocal() as session:
        try:
            new_rma = RMA(
                rma_number=rma_number,
                customer_id=customer_id,
                part_number_id=part_number_id,
                serial_number=serial_number,
                reason_for_return=reason_for_return,
                issued_by_id=issued_by_id,
                is_warranty=is_warranty,
                customer_po_number=customer_po_number,
            )
            session.add(new_rma)
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False


def update_status(rma_number: str, new_status: str) -> bool:
    with SessionLocal() as session:
        rma = session.query(RMA).filter_by(rma_number=rma_number).first()

        if not rma:
            print(f'RMA {rma_number} not found.')
            return False

        if rma.status == new_status:
            print(f'RMA-{rma_number} status is alread "{new_status}"')
            return False

        try:
            rma.status = new_status
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def get_newest_rma_num() -> int | None:
    with SessionLocal() as session:
        return session.execute(
            select(RMA.rma_number).order_by(desc(RMA.issued_on)).limit(1)
        ).scalar_one_or_none()


def get_oldest_rma_num() -> int | None:
    with SessionLocal() as session:
        return session.execute(
            select(RMA.rma_number).order_by(asc(RMA.issued_on)).limit(1)
        ).scalar_one_or_none()


def get_rma_by_rma_num(rma_number: int) -> RMA | None:
    with SessionLocal() as session:
        return (
            session.query(RMA)
            .options(
                joinedload(RMA.part_number).joinedload(PartNumber.product),
                joinedload(RMA.customer),
                joinedload(RMA.issued_by),
            )
            .filter_by(rma_number=rma_number)
            .first()
        )


def get_rma_by_sn(serial_num: str, fuzzy: bool = False) -> RMA | None:
    with SessionLocal() as session:
        if fuzzy:
            return (
                session.query(RMA)
                .options(
                    joinedload(RMA.part_number).joinedload(PartNumber.product),
                    joinedload(RMA.customer),
                    joinedload(RMA.issued_by),
                )
                .filter(RMA.serial_number.like(f'%{serial_num}%'))
                .order_by(RMA.rma_number.desc())
                .first()
            )

        return (
            session.query(RMA)
            .options(
                joinedload(RMA.part_number).joinedload(PartNumber.product),
                joinedload(RMA.customer),
                joinedload(RMA.issued_by),
            )
            .filter_by(serial_number=serial_num)
            .order_by(RMA.rma_number.desc())
            .first()
        )


def overwrite_rma_record(rma_number: str, entries: list[str | bool | None]) -> bool:
    with SessionLocal() as session:
        rma = session.query(RMA).filter_by(rma_number=rma_number).first()

        if not rma:
            return False

        # List of attribute names to overwrite
        attribute_names = [
            'reason_for_return',
            'status',
            'customer_po_number',
            'work_order',
            'incoming_inspection_notes',
            'resolution_notes',
            'shipped_back_on',
            'is_warranty',
        ]

        if len(entries) != len(attribute_names):
            raise ValueError(
                'The number of entries does not match the number of attributes to overwrite.'
            )

        # Set new values
        for attr, value in zip(attribute_names, entries):
            if attr == 'shipped_back_on' and type(value) is str:
                value = datetime.strptime(value, '%Y-%m-%d')
            setattr(rma, attr, value)

        session.commit()
        return True
