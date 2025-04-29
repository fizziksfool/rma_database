"""
Starts the GUI
"""

from database import DB_PATH, RMA, SessionLocal, initialize_database


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


def read_rmas():
    session = SessionLocal()
    rmas = session.query(RMA).all()
    for rma in rmas:
        print(
            f'RMA Number: {rma.rma_number},\n'
            f'Customer: {rma.customer},\n'
            f'Product: {rma.product_description},\n'
            f'Status: {rma.status},\n'
            f'Created At: {rma.created_at}\n'
            f'Last updated at: {rma.updated_at}\n'
        )


def update_status(rma_number: str, new_status: str) -> None:
    session = SessionLocal()
    rma = session.query(RMA).filter_by(rma_number=rma_number).first()

    if not rma:
        print(f'RMA {rma_number} not found.')
        return

    if rma.status == new_status:
        print(f'RMA-{rma_number} status is alread "{new_status}"')
        return

    print(
        f'Updating status for RMA {rma_number} from "{rma.status}" to "{new_status}."'
    )
    rma.status = new_status
    session.commit()
    session.close()


if __name__ == '__main__':
    # Only run database initialization routine if it doesn't already exist.
    if not DB_PATH.is_file():
        initialize_database()
        add_rma(
            rma_number='25001',
            department='Hyperion',
            customer='Cameca',
            product={'H201-bipolar': '18710'},
            serial_number='555',
            is_warranty=False,
            reason_for_return='Refurbishment',
            customer_po_number='CDA123456',
            created_by='Joshua',
        )

    add_rma(
        rma_number='25003',
        department='Hyperion',
        customer='Cameca',
        product={'H201-bipolar': '18710'},
        serial_number='600',
        is_warranty=False,
        reason_for_return='Refurbishment',
        customer_po_number='CDA234568',
        created_by='Joshua',
    )
    read_rmas()
