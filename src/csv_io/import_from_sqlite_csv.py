import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from ..database import (
    RMA,
    Customer,
    PartNumber,
    Product,
    SessionLocal,
    User,
    initialize_database,
)

DB_PATH = Path('./X/rma_database/rma.db')
IMPORT_FILE = Path('//opdata2/Company/PRODUCTION FOLDER/RMA/HyperionRMAs2.csv')


def parse_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
    except ValueError:
        return None


def parse_bool(val: str) -> bool:
    return val.lower() in ('true', '1', 'yes') if isinstance(val, str) else bool(val)


def get_or_create(session: Session, model, **kwargs) -> Any:
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
    return instance


def import_rmas_from_csv():
    session = SessionLocal()

    with IMPORT_FILE.open('r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Resolve related records
            user = get_or_create(session, User, name=row['issued_by'])
            customer = get_or_create(session, Customer, name=row['customer'])
            product = get_or_create(session, Product, name=row['product'])
            part_number = get_or_create(
                session, PartNumber, number=row['part_number'], product=product
            )

            # Check for existing RMA to prevent duplicates
            existing = (
                session.query(RMA).filter_by(rma_number=row['rma_number']).first()
            )
            if existing:
                print(f'Skipping existing RMA {row["rma_number"]}')
                continue

            rma = RMA(
                rma_number=row['rma_number'],
                issued_by=user,
                customer=customer,
                part_number=part_number,
                serial_number=row['serial_number'],
                is_warranty=parse_bool(row['is_warranty']),
                reason_for_return=row['reason_for_return'],
                status=row['status'],
                issued_on=parse_date(row['issued_on']),
                last_updated=parse_date(row['last_updated']),
                customer_po_number=row['customer_po_number'] or None,
                work_order=row['work_order'] or None,
                incoming_inspection_notes=row['incoming_inspection_notes'] or None,
                resolution_notes=row['resolution_notes'] or None,
                shipped_back_on=parse_date(row['shipped_back_on']),
            )

            session.add(rma)

        session.commit()
        print(f'Import complete from {IMPORT_FILE}')

    session.close()


if __name__ == '__main__':
    if not DB_PATH.exists():
        initialize_database()
    import_rmas_from_csv()
