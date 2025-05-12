import csv
from pathlib import Path

from ..database import RMA, SessionLocal

EXPORT_FILE = Path('//opdata2/Company/PRODUCTION FOLDER/RMA/HyperionRMAs2.csv')


def export_rmas_to_csv() -> None:
    session = SessionLocal()

    # Define the fieldnames (column headers) for the CSV
    fieldnames = [
        'rma_number',
        'issued_by',
        'customer',
        'part_number',
        'product',
        'serial_number',
        'is_warranty',
        'reason_for_return',
        'status',
        'issued_on',
        'last_updated',
        'customer_po_number',
        'work_order',
        'incoming_inspection_notes',
        'resolution_notes',
        'shipped_back_on',
    ]

    with EXPORT_FILE.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for rma in session.query(RMA).all():
            writer.writerow(
                {
                    'rma_number': rma.rma_number,
                    'issued_by': rma.issued_by.name if rma.issued_by else '',
                    'customer': rma.customer.name if rma.customer else '',
                    'part_number': rma.part_number.number if rma.part_number else '',
                    'product': rma.part_number.product.name if rma.part_number else '',
                    'serial_number': rma.serial_number,
                    'is_warranty': rma.is_warranty,
                    'reason_for_return': rma.reason_for_return,
                    'status': rma.status,
                    'issued_on': rma.issued_on.strftime('%Y-%m-%d')
                    if rma.issued_on
                    else '',
                    'last_updated': rma.last_updated.strftime('%Y-%m-%d')
                    if rma.last_updated
                    else '',
                    'customer_po_number': rma.customer_po_number or '',
                    'work_order': rma.work_order or '',
                    'incoming_inspection_notes': rma.incoming_inspection_notes or '',
                    'resolution_notes': rma.resolution_notes or '',
                    'shipped_back_on': rma.shipped_back_on.strftime('%Y-%m-%d')
                    if rma.shipped_back_on
                    else '',
                }
            )

    session.close()
    print(f'Export completed to {EXPORT_FILE}')


if __name__ == '__main__':
    export_rmas_to_csv()
