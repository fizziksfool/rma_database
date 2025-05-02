from datetime import datetime
from typing import Any, Literal

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
    Qt,
)
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from src.database import (
    RMA,
    Customer,
    PartNumber,
    Product,
    SessionLocal,
    User,
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


def generate_rma_number() -> str:
    year_prefix = datetime.now().strftime('%y')
    base = int(year_prefix) * 1000

    with SessionLocal() as session:
        latest = (
            session.query(func.max(RMA.rma_number))
            .filter(RMA.rma_number.like(f'{year_prefix}%'))
            .scalar()
        )

        if latest:
            return str(int(latest) + 1)
        else:
            return str(base + 1)


def add_rma(
    rma_number: str,
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


class OpenRMAsTableModel(QAbstractTableModel):
    """
    A Qt table model for displaying open RMAs in a QTableView.

    This model is used to interface a list of RMA SQLAlchemy objects with a Qt view.
    It defines the structure of the table including the number of rows and columns,
    how each cell's data should be displayed, and the headers for the table.

    Attributes:
        rmas (list[RMA]): A list of RMA objects representing open RMAs.
        headers (list[str]): A list of strings used as the column headers in the view.

    Methods:
        rowCount(): Returns the number of rows (open RMAs) in the model.
        columnCount(): Returns the number of columns in the model (RMA fields).
        data(): Returns the display data for a given cell based on the index and role.
        headerData(): Returns the header label for a given row or column.
    """

    def __init__(self, rmas: list[RMA], parent=None) -> None:
        super().__init__(parent)
        self.rmas = rmas
        self.headers = [
            'RMA #',
            'Customer',
            'Product',
            'Part #',
            'Reason For Return',
            'Warranty',
            'Status',
        ]

    def rowCount(self, parent=None) -> int:
        return len(self.rmas)

    def columnCount(self, parent=None) -> int:
        return len(self.headers)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> None | Any | Literal['Yes'] | Literal['No']:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        rma = self.rmas[index.row()]
        col = index.column()

        if col == 0:
            return rma.rma_number
        elif col == 1:
            return rma.customer.name
        elif col == 2:
            return rma.part_number.product.name
        elif col == 3:
            return rma.part_number.number
        elif col == 4:
            return rma.reason_for_return
        elif col == 5:
            return 'Yes' if rma.is_warranty else 'No'
        elif col == 6:
            return rma.status

        return None

    def headerData(
        self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> None | list[str] | str:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        else:
            return str(section + 1)


class OpenRMAsSortFilterProxyModel(QSortFilterProxyModel):
    """
    A proxy model for sorting and filtering open RMA entries in a QTableView.

    This model extends QSortFilterProxyModel to enable multi-column filtering of
    RMA data displayed in a table view. It currently supports filtering by
    product name and customer name, while still allowing column-based sorting.

    Attributes:
        product_filter (str): The currently selected product name to filter by.
                              An empty string disables product filtering.
        customer_filter (str): The currently selected customer name to filter by.
                               An empty string disables customer filtering.

    Methods:
        set_product_filter(product_name: str):
            Sets the product filter. Pass 'All Products' to clear the filter.

        set_customer_filter(customer_name: str):
            Sets the customer filter. Pass 'All Customers' to clear the filter.

        filterAcceptsRow(source_row: int, source_parent):
            Returns True if the row matches the active product and customer filters;
            otherwise returns False.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.customer_filter = ''
        self.product_filter = ''

    def set_customer_filter(self, customer_name: str) -> None:
        if customer_name == 'All Customers':
            self.customer_filter = ''
        else:
            self.customer_filter = customer_name
        self.invalidateFilter()

    def set_product_filter(self, product_name: str) -> None:
        if product_name == 'All Products':
            self.product_filter = ''
        else:
            self.product_filter = product_name
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        model = self.sourceModel()

        # Customer filter (column 1)
        if self.customer_filter:
            customer_index = model.index(source_row, 1, source_parent)
            if customer_index.data() != self.customer_filter:
                return False

        # Product filter (column 2)
        if self.product_filter:
            product_index = model.index(source_row, 2, source_parent)
            if product_index.data() != self.product_filter:
                return False

        return True
