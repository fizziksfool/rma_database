from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSize, Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QLabel,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
)
from sqlalchemy.orm import joinedload

from ..database import RMA, PartNumber, SessionLocal
from ..models import AllRMAsSortFilterProxyModel, AllRMAsTableModel


class ViewRMATable(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowTitle('RMA Table')
        self.table_view = QTableView(self)
        self.table_view.setWordWrap(True)
        self.table_view.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.table_view.setItemDelegate(WordWrapDelegate(self.table_view))

        self.filter_customer_label = QLabel('Filter by Customer:')
        self.filter_customer_cbb = QComboBox(self)
        self.filter_customer_cbb.setStyleSheet('color: lightgreen;')
        self.filter_customer_cbb.currentTextChanged.connect(self.apply_customer_filter)

        self.filter_product_label = QLabel('Filter by Product:')
        self.filter_product_cbb = QComboBox(self)
        self.filter_product_cbb.setStyleSheet('color: lightgreen;')
        self.filter_product_cbb.currentTextChanged.connect(self.apply_product_filter)

        self.filter_warranty_label = QLabel('Filter by Warranty:')
        self.filter_warranty_cbb = QComboBox(self)
        self.filter_warranty_cbb.setStyleSheet('color: lightgreen;')
        self.filter_warranty_cbb.currentTextChanged.connect(self.apply_warranty_filter)

        self.filter_status_label = QLabel('Filter by Status:')
        self.filter_status_cbb = QComboBox(self)
        self.filter_status_cbb.setStyleSheet('color: lightgreen;')
        self.filter_status_cbb.currentTextChanged.connect(self.apply_status_filter)

        self.filters_layout = QGridLayout()
        self.filters_layout.addWidget(
            self.filter_customer_label, 0, 0, Qt.AlignmentFlag.AlignRight
        )
        self.filters_layout.addWidget(self.filter_customer_cbb, 0, 1)
        self.filters_layout.addWidget(
            self.filter_product_label, 1, 0, Qt.AlignmentFlag.AlignRight
        )
        self.filters_layout.addWidget(self.filter_product_cbb, 1, 1)
        self.filters_layout.addWidget(
            self.filter_warranty_label, 0, 2, Qt.AlignmentFlag.AlignRight
        )
        self.filters_layout.addWidget(self.filter_warranty_cbb, 0, 3)
        self.filters_layout.addWidget(
            self.filter_status_label, 1, 2, Qt.AlignmentFlag.AlignRight
        )
        self.filters_layout.addWidget(self.filter_status_cbb, 1, 3)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.filters_layout)
        main_layout.addWidget(self.table_view)

        self.setLayout(main_layout)

        self.load_data()

    def load_data(self) -> None:
        with SessionLocal() as session:
            all_rmas = (
                session.query(RMA)
                .options(
                    joinedload(RMA.part_number).joinedload(PartNumber.product),
                    joinedload(RMA.customer),
                    joinedload(RMA.issued_by),
                )
                .all()
            )

        products = sorted({rma.part_number.product.name for rma in all_rmas})
        customers = sorted({rma.customer.name for rma in all_rmas})
        warranties = sorted({'Yes' if rma.is_warranty else 'No' for rma in all_rmas})
        statuses = sorted({rma.status for rma in all_rmas})

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

        self.filter_warranty_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_warranty_cbb.clear()
        self.filter_warranty_cbb.addItem('Any')
        self.filter_warranty_cbb.addItems(warranties)
        self.filter_warranty_cbb.blockSignals(False)

        self.filter_status_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_status_cbb.clear()
        self.filter_status_cbb.addItem('All')
        self.filter_status_cbb.addItems(statuses)
        self.filter_status_cbb.blockSignals(False)

        self.model = AllRMAsTableModel(all_rmas)
        self.proxy_model = AllRMAsSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)  # sort by ascending RMA#

        self.adjust_column_widths()
        self.table_view.resizeRowsToContents()
        self.adjust_window_size()

    def apply_customer_filter(self, customer: str) -> None:
        self.proxy_model.set_customer_filter(customer)
        self.table_view.resizeRowsToContents()

    def apply_product_filter(self, product: str) -> None:
        self.proxy_model.set_product_filter(product)
        self.table_view.resizeRowsToContents()

    def apply_warranty_filter(self, warranty: str) -> None:
        self.proxy_model.set_warranty_filter(warranty)
        self.table_view.resizeRowsToContents()

    def apply_status_filter(self, status: str) -> None:
        self.proxy_model.set_status_filter(status)
        self.table_view.resizeRowsToContents()

    def adjust_column_widths(self) -> None:
        self.table_view.resizeColumnsToContents()
        extra_padding = 15
        max_column_width = 163
        for col in range(self.model.columnCount()):
            current_width = self.table_view.columnWidth(col)
            col_width = min(current_width, max_column_width)
            self.table_view.setColumnWidth(col, col_width + extra_padding)

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
            and calling self.adjust_column_size().
        """
        # Calculate width elements in window
        header = self.table_view.horizontalHeader()
        headers_width = sum(header.sectionSize(i) for i in range(header.count()))
        index_width = self.table_view.verticalHeader().width()
        scrollbar_width = (
            self.table_view.verticalScrollBar().isVisible()
            * self.table_view.verticalScrollBar().sizeHint().width()
        )
        horizontal_padding = 20

        full_width = index_width + headers_width + scrollbar_width + horizontal_padding

        # Calculate height of elements in window
        row_count = self.table_view.model().rowCount()
        row_height = self.table_view.verticalHeader().defaultSectionSize()
        header_height = header.height()
        filter_customer_height = self.filter_customer_cbb.sizeHint().height()
        filter_product_height = self.filter_product_cbb.sizeHint().height()
        filter_label_height = 2 * QLabel().sizeHint().height()
        filters_height = (
            filter_customer_height + filter_product_height + filter_label_height + 10
        )  # +spacing
        vertical_padding = 60  # Additional padding for margins, layout spacing, etc.

        full_height = (
            filters_height + (row_height * row_count) + header_height + vertical_padding
        )

        max_width = 1800
        max_height = 800

        final_width = min(full_width, max_width)
        final_height = min(full_height, max_height)

        self.resize(final_width, final_height)


class WordWrapDelegate(QStyledItemDelegate):
    def __init__(self, table_view: QTableView, parent=None) -> None:
        super().__init__(parent)
        self.table_view = table_view

    def initStyleOption(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        super().initStyleOption(option, index)

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        doc = QTextDocument()
        doc.setPlainText(index.data())

        column_width = self.table_view.columnWidth(index.column())
        doc.setTextWidth(column_width)

        return QSize(int(doc.idealWidth()), int(doc.size().height() + 10))
