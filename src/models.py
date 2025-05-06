from collections.abc import Callable
from operator import attrgetter
from typing import Any, Literal

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
    Qt,
)

from .database import RMA

RMA_ATTR_ACCESSORS: dict[str, Callable[[RMA], Any]] = {
    # header text: RMA table attribute
    'RMA #': attrgetter('rma_number'),
    'Issued By': attrgetter('issued_by.name'),
    'Customer': attrgetter('customer.name'),
    'Product': attrgetter('part_number.product.name'),
    'Part #': attrgetter('part_number.number'),
    'Serial #': attrgetter('serial_number'),
    'Warranty': lambda rma: 'Yes' if rma.is_warranty else 'No',
    'Reason for Return': attrgetter('reason_for_return'),
    'Status': attrgetter('status'),
    'Date Issued': attrgetter('issued_on'),
    'Last Updated': attrgetter('last_updated'),
    'Cust. PO #': attrgetter('customer_po_number'),
    'WO #': attrgetter('work_order'),
    'Inspection Notes': attrgetter('incoming_inspection_notes'),
    'Resolution': attrgetter('resolution_notes'),
    'Date Returned': attrgetter('shipped_back_on'),
}


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
        self.headers: list[str] = [
            'RMA #',
            'Customer',
            'Product',
            'Part #',
            'Serial #',
            'Reason for Return',
            'Warranty',
            'Status',
        ]

        self.accessors: list[Callable] = [
            RMA_ATTR_ACCESSORS[header] for header in self.headers
        ]

    def rowCount(self, parent=None) -> int:
        return len(self.rmas)

    def columnCount(self, parent=None) -> int:
        return len(self.headers)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> None | Any | Literal['Yes', 'No']:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        rma: RMA = self.rmas[index.row()]
        col: int = index.column()

        try:
            accessor = self.accessors[col]
            return accessor(rma)
        except (IndexError, AttributeError):
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
        self.warranty_filter = ''
        self.status_filter = ''

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

    def set_warranty_filter(self, warranty: str) -> None:
        if warranty == 'Any':
            self.warranty_filter = ''
        else:
            self.warranty_filter = warranty
        self.invalidateFilter()

    def set_status_filter(self, status: str) -> None:
        if status == 'All':
            self.status_filter = ''
        else:
            self.status_filter = status
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

        # Warranty filter (column 5)
        if self.warranty_filter:
            warranty_index = model.index(source_row, 5, source_parent)
            if warranty_index.data() != self.warranty_filter:
                return False

            # Status filter (column 6)
            if self.status_filter:
                status_index = model.index(source_row, 6, source_parent)
                if status_index.data() != self.status_filter:
                    return False

        return True
