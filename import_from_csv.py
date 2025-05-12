import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from src.database import (
    RMA,
    Customer,
    PartNumber,
    Product,
    SessionLocal,
    User,
    initialize_database,
)

CSV_PATH = Path('//opdata2/Company/PRODUCTION FOLDER/RMA/HyperionRMAs.csv')

DATE_FMT = '%m/%d/%Y'


def parse_date(value) -> datetime | None:
    try:
        return datetime.strptime(value, DATE_FMT)
    except (ValueError, TypeError):
        return None


def parse_bool(value: str) -> bool:
    return value.strip().upper() == 'TRUE'


def get_or_create(session: Session, model, **kwargs) -> Any:
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()  # Assigns ID
    return instance


def import_csv() -> None:
    initialize_database()  # Ensure tables are created

    with (
        SessionLocal() as session,
        open(CSV_PATH, newline='', encoding='utf-8-sig') as file,
    ):
        reader = csv.DictReader(file)

        for row in reader:
            row = {k.strip(): v for k, v in row.items()}
            # Fetch or create related objects
            user = get_or_create(session, User, name=row['Issued by'])
            customer = get_or_create(session, Customer, name=row['Customer'])
            product = get_or_create(session, Product, name=row['ProductDescription'])
            part_number = get_or_create(
                session, PartNumber, number=row['Product Number'], product=product
            )

            # Create RMA entry
            rma = RMA(
                rma_number=row['RMA'],
                issued_by=user,
                customer=customer,
                part_number=part_number,
                serial_number=row['Product Serial Number'],
                is_warranty=parse_bool(row['Warranty']),
                reason_for_return=row['Description of Problem'],
                status='Closed' if parse_bool(row['RMA Closed']) else 'Issued',
                issued_on=parse_date(row['Date RMA Issued']),
                shipped_back_on=parse_date(
                    row['Date Product Shipped back to Customer']
                ),
                customer_po_number=row['Customer PO number'] or None,
                work_order=row['Work Order Number'] or None,
                incoming_inspection_notes=row['Inspection/Refurb Notes'] or None,
                resolution_notes=row['Resolution'] or None,
            )

            session.add(rma)

        session.commit()
        print('Import complete.')


if __name__ == '__main__':
    import_csv()
