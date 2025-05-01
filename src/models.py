"""
RMA dataclasses or SQLAlchemy models
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from src.database import (
    DB_PATH,
    RMA,
    Customer,
    ProductDescription,
    ProductNumber,
    SessionLocal,
    initialize_database,
)


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


def add_product(product_description: str, product_number: str) -> bool:
    product_desc = product_description.strip().lower()
    product_num = product_number.strip()

    if not product_desc or not product_num:
        return False

    with SessionLocal() as session:
        existing_desc = (
            session.query(ProductDescription).filter_by(name=product_desc).first()
        )
        existing_num = (
            session.query(ProductNumber).filter_by(number=product_num).first()
        )
        if existing_desc or existing_num:
            return False

        try:
            # Add product description
            new_desc = ProductDescription(name=product_desc)
            session.add(new_desc)
            session.flush()  # Get new_desc.id before committing

            # Add product number linked to the description
            new_number = ProductNumber(number=product_num, description_id=new_desc.id)
            session.add(new_number)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def add_part_number(description_id: int, product_number: str) -> bool:
    product_num = product_number.strip()

    if not product_num:
        return False

    with SessionLocal() as session:
        existing = session.query(ProductNumber).filter_by(number=product_num).first()
        if existing:
            return False

        try:
            new_number = ProductNumber(
                number=product_num, description_id=description_id
            )
            session.add(new_number)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def view_open_rmas(table: QTableWidget) -> None:
    columns_to_view: list[str] = [
        'RMA #',
        'Customer',
        'Product',
        'Part #',
        'Reason For Return',
        'Status',
    ]

    with SessionLocal() as session:
        open_rmas = (
            session.query(RMA)
            .options(
                joinedload(RMA.product_number).joinedload(ProductNumber.description),
                joinedload(RMA.customer),
            )
            .filter(RMA.status != 'Closed')
            .order_by(RMA.rma_number)
            .all()
        )

        table.setRowCount(len(open_rmas))
        table.setColumnCount(len(columns_to_view))
        table.setHorizontalHeaderLabels(columns_to_view)

        for row, rma in enumerate(open_rmas):
            table.setItem(row, 0, QTableWidgetItem(rma.rma_number))
            table.setItem(row, 1, QTableWidgetItem(rma.customer.name))
            table.setItem(row, 2, QTableWidgetItem(rma.product))
            table.setItem(row, 3, QTableWidgetItem(rma.product_number.number))
            table.setItem(row, 4, QTableWidgetItem(rma.reason_for_return))
            table.setItem(row, 5, QTableWidgetItem(rma.status))

        column_width_default = 130  # pixels
        column_width_wide = 200  # pixels

        for col, header in enumerate(columns_to_view):
            if header == 'Reason For Return':
                table.setColumnWidth(col, column_width_wide)
            else:
                table.setColumnWidth(col, column_width_default)


def add_rma(
    rma_number: str,
    department: str,
    customer: str,
    product: dict[str, str],
    serial_number: str,
    is_warranty: bool,
    reason_for_return: str,
    customer_po_number: str,
    created_by: str,
    notes: str | None = None,
) -> None:
    session = SessionLocal()

    rma = session.query(RMA).filter_by(rma_number=rma_number).first()

    if rma:
        print(f'RMA-{rma_number} already exists.')
        return

    if not product:
        raise ValueError('Product dictionary is empty.')

    product_description, product_number = next(iter(product.items()))

    # Add new RMA
    new_rma = RMA(
        rma_number=rma_number,
        department=department,  # Hyperion, E-Gun, FIBSL
        customer=customer,  # Cameca, JEOL, UCLA, University of Hawaii, etc.
        product_description=product_description,  # H201-positive, H201-bipolar, H200, H100, VRG, HEUv1, HEUv2, HEUv3
        product_number=product_number,  # Should be linked to product description and customer
        serial_number=serial_number,
        is_warranty=is_warranty,
        reason_for_return=reason_for_return,
        customer_po_number=customer_po_number,
        incoming_inspection_notes=notes,
        created_by=created_by,  # Authorized users?
    )
    session.add(new_rma)
    session.commit()
    print(f'RMA-{rma_number} added to database.')
    session.close()


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


if __name__ == '__main__':
    # Only run database initialization routine if it doesn't already exist.
    if not DB_PATH.is_file():
        initialize_database()
