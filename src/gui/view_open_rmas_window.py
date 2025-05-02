from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QTableView,
    QVBoxLayout,
)
from sqlalchemy.orm import joinedload

from src.database import RMA, PartNumber, SessionLocal
from src.models import OpenRMAsSortFilterProxyModel, OpenRMAsTableModel


class ViewOpenRMAsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('View Open RMAs')
        self.table_view = QTableView(self)

        self.filter_customer_cbb = QComboBox(self)
        self.filter_customer_cbb.setStyleSheet('color: lightgreen;')
        self.filter_customer_cbb.currentTextChanged.connect(self.apply_customer_filter)

        self.filter_product_cbb = QComboBox(self)
        self.filter_product_cbb.setStyleSheet('color: lightgreen;')
        self.filter_product_cbb.currentTextChanged.connect(self.apply_product_filter)

        filter_labels_layout = QVBoxLayout()
        filter_boxes_layout = QVBoxLayout()
        filters_layout = QHBoxLayout()

        filter_labels_layout.addWidget(QLabel('Filter by Customer:'))
        filter_labels_layout.addWidget(QLabel('Filter by Product:'))
        filter_boxes_layout.addWidget(self.filter_customer_cbb)
        filter_boxes_layout.addWidget(self.filter_product_cbb)

        filters_layout.addLayout(filter_labels_layout)
        filters_layout.addLayout(filter_boxes_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(filters_layout)
        main_layout.addWidget(self.table_view)

        self.setLayout(main_layout)

        self.load_data()

    def load_data(self) -> None:
        with SessionLocal() as session:
            open_rmas = (
                session.query(RMA)
                .options(
                    joinedload(RMA.part_number).joinedload(PartNumber.product),
                    joinedload(RMA.customer),
                )
                .filter(RMA.status != 'Closed')
                .order_by(RMA.rma_number)
                .all()
            )

        products = sorted({rma.part_number.product.name for rma in open_rmas})
        customers = sorted({rma.customer.name for rma in open_rmas})

        self.filter_customer_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_customer_cbb.clear()
        self.filter_customer_cbb.addItem('All Customers')
        self.filter_customer_cbb.addItems(customers)
        self.filter_customer_cbb.blockSignals(False)

        self.filter_product_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_product_cbb.clear()
        self.filter_product_cbb.addItem('All Products')
        self.filter_product_cbb.addItems(products)
        self.filter_product_cbb.blockSignals(False)

        self.model = OpenRMAsTableModel(open_rmas)
        self.proxy_model = OpenRMAsSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)  # RMA number ascending

        for col, header in enumerate(self.model.headers):
            if header == 'Reason For Return':
                self.table_view.setColumnWidth(col, 200)
            else:
                self.table_view.setColumnWidth(col, 130)

        self.adjust_window_size()

    def apply_customer_filter(self, customer: str) -> None:
        self.proxy_model.set_customer_filter(customer)

    def apply_product_filter(self, product: str) -> None:
        self.proxy_model.set_product_filter(product)

    def adjust_window_size(self) -> None:
        """
        Adjusts the size of the dialog window to fit the contents of the table.

        This method calculates the total width of all visible columns in the table,
        accounts for the width of the vertical scrollbar and layout padding, and resizes
        the window accordingly. It also adjusts the height based on the number of visible
        rows and the header height, ensuring the table content is fully visible without
        clipping or excessive space.

        Note:
            This adjustment is typically called after populating the table with data
            and calling resizeColumnsToContents().
        """
        header = self.table_view.horizontalHeader()
        headers_width = sum(header.sectionSize(i) for i in range(header.count()))

        index_width = self.table_view.verticalHeader().width()

        scrollbar_width = (
            self.table_view.verticalScrollBar().isVisible()
            * self.table_view.verticalScrollBar().sizeHint().width()
        )

        padding = 20

        full_width = index_width + headers_width + scrollbar_width + padding
        full_height = self.table_view.verticalHeader().length() + header.height() + 100

        self.resize(full_width, full_height)
