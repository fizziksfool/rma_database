from typing import Any

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QCursor, QMouseEvent, QTextDocument
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGridLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import joinedload

from ..database import RMA, PartNumber, SessionLocal
from ..models import OpenRMAsSortFilterProxyModel, OpenRMAsTableModel
from ..pdf import PDF
from .custom_dropdown_style import combo_style
from .error_messages import open_pdf_failed_message


class ViewOpenRMAsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('View Open RMAs')
        self.table_view = QTableView(self)
        self.table_view.setWordWrap(True)
        self.table_view.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.table_view.setItemDelegate(WordWrapDelegate(self.table_view))

        self.print_button = QPushButton('Print to PDF', self)
        self.print_button.clicked.connect(self._handle_print_button_pressed)
        self.print_button.setCursor(Qt.CursorShape.PointingHandCursor)

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
        selection_list = [
            'Issued',
            'Received',
            'In Process',
            'Complete',
        ]
        self.filter_status_dd = MultiSelectDropdown(items=selection_list, parent=self)
        self.filter_status_dd.selectionChanged.connect(self.apply_status_filter)

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
        self.filters_layout.addWidget(self.filter_status_dd, 1, 3)

        self.filters_layout.addWidget(
            self.print_button, 0, 4, 2, 1, Qt.AlignmentFlag.AlignVCenter
        )

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.filters_layout)
        main_layout.addWidget(self.table_view)

        self.setLayout(main_layout)

        self.load_data()
        self.filter_status_dd.emit_selection_changed()
        self.adjust_window_size()

    def load_data(self) -> None:
        with SessionLocal() as session:
            open_rmas = (
                session.query(RMA)
                .options(
                    joinedload(RMA.part_number).joinedload(PartNumber.product),
                    joinedload(RMA.customer),
                    joinedload(RMA.issued_by),
                )
                .filter(RMA.status != 'Closed')
                .all()
            )

        products: list[str] = sorted(
            {rma.part_number.product.name for rma in open_rmas}
        )
        customers: list[str] = sorted({rma.customer.name for rma in open_rmas})
        warranties: list[str] = sorted(
            {'Yes' if rma.is_warranty else 'No' for rma in open_rmas}
        )
        # statuses: list[str] = sorted({rma.status for rma in open_rmas})

        self.filter_customer_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_customer_cbb.clear()
        self.filter_customer_cbb.addItem('No Filter')
        self.filter_customer_cbb.addItems(customers)
        self.filter_customer_cbb.blockSignals(False)

        self.filter_product_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_product_cbb.clear()
        self.filter_product_cbb.addItem('No Filter')
        self.filter_product_cbb.addItems(products)
        self.filter_product_cbb.blockSignals(False)

        self.filter_warranty_cbb.blockSignals(True)  # prevent premature filtering
        self.filter_warranty_cbb.clear()
        self.filter_warranty_cbb.addItem('No Filter')
        self.filter_warranty_cbb.addItems(warranties)
        self.filter_warranty_cbb.blockSignals(False)

        # self.filter_status_dd.blockSignals(True)  # prevent premature filtering
        # self.filter_status_dd.clear()
        # self.filter_status_dd.addDefaultItem('Select All')
        # self.filter_status_dd.addItems(statuses)
        # self.filter_status_dd.blockSignals(False)

        self.model = OpenRMAsTableModel(open_rmas)

        self.proxy_model = OpenRMAsSortFilterProxyModel()
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

    def apply_status_filter(self, selected_statuses: list[str]) -> None:
        filtered_statuses = [
            status for status in selected_statuses if status != 'Select All'
        ]
        self.proxy_model.set_status_filter(filtered_statuses)
        self.table_view.resizeRowsToContents()

    def _handle_print_button_pressed(self) -> None:
        pdf = PDF(self.table_view)
        try:
            pdf.open()
        except Exception as e:
            open_pdf_failed_message(self, e)

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
            and calling self.adjust_column_widths().
        """
        header = self.table_view.horizontalHeader()
        headers_width = sum(header.sectionSize(i) for i in range(header.count()))
        index_width = self.table_view.verticalHeader().width()
        scrollbar_width = (
            self.table_view.verticalScrollBar().isVisible()
            * self.table_view.verticalScrollBar().sizeHint().width()
        )
        horizontal_padding = 100  # check this line on work monitor

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
        full_width = index_width + headers_width + scrollbar_width + horizontal_padding

        max_width = 1900
        max_height = 1000

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


class MultiSelectDropdown(QWidget):
    selectionChanged = Signal(list)

    def __init__(self, items: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.selected_items: list[str] = []
        self.items = items
        self.dropdown_visible = False

        self.button = QToolButton(self)
        self.button.setObjectName('statusFilterButton')
        self.button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.button.clicked.connect(self.toggle_dropdown)

        self.dropdown = ClickableListWidget(self)
        self.dropdown.setObjectName('clickableList')
        self.dropdown.setWindowFlags(Qt.WindowType.Popup)
        self.dropdown.setFixedSize(210, 213)
        self.dropdown.checkedItemsChanged.connect(self.emit_selection_changed)
        self.dropdown.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.button.setStyleSheet(combo_style)
        self.dropdown.setStyleSheet(combo_style)

        select_all = QListWidgetItem('Select All')
        select_all.setFlags(select_all.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        select_all.setCheckState(Qt.CheckState.Checked)
        self.dropdown.addItem(select_all)
        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.dropdown.addItem(item)
            self.update_selection(item)

        self.dropdown.itemChanged.connect(self.update_selection)

        # Global event filter for click-outside behavior
        QTimer.singleShot(0, self.register_event_filter)

    def toggle_dropdown(self) -> None:
        if not self.dropdown_visible:
            point = self.button.mapToGlobal(QPoint(0, self.button.height()))
            self.dropdown.move(point)
            self.dropdown.setMinimumWidth(self.button.width())
            self.dropdown.show()
            self.dropdown_visible = True
        else:
            self.dropdown.hide()
            self.dropdown_visible = False

    def update_selection(self, item: QListWidgetItem) -> None:
        selected: list[str] = []
        for i in range(self.dropdown.count()):
            list_item = self.dropdown.item(i)
            if (
                list_item.checkState() == Qt.CheckState.Checked
                and list_item.text() != 'Select All'
            ):
                selected.append(list_item.text())

        self.selected_items = selected

        # check if all options are selected
        if all(item in self.selected_items for item in self.items):
            self.button.setText('No Filter')
        else:
            self.button.setText('Filtered')

    def get_selected_items(self) -> list[Any]:
        return self.selected_items

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if self.dropdown_visible and event.type() == QEvent.Type.MouseButtonPress:
            global_pos = QCursor.pos()
            if not self.dropdown.geometry().contains(
                global_pos
            ) and not self.geometry().contains(self.mapFromGlobal(global_pos)):
                self.dropdown.hide()
                self.dropdown_visible = False
        return super().eventFilter(obj, event)

    def register_event_filter(self) -> None:
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

    def emit_selection_changed(self) -> None:
        selected: list[str] = self.get_selected_items()
        self.selectionChanged.emit(selected)


class ClickableListWidget(QListWidget):
    checkedItemsChanged = Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.position().toPoint())
        if item is not None:
            new_state = (
                Qt.CheckState.Unchecked
                if item.checkState() == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            item.setCheckState(new_state)

            if item.text() == 'Select All':
                self.set_all_items_checked(new_state == Qt.CheckState.Checked)
            else:
                self.update_select_all_check_state()

            self.emit_checked_items()

        super().mousePressEvent(event)

    def set_all_items_checked(self, checked: bool) -> None:
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for i in range(self.count()):
            item = self.item(i)
            item.setCheckState(state)

    def update_select_all_check_state(self) -> None:
        # Assume "Select All" is always item 0
        all_checked = all(
            self.item(i).checkState() == Qt.CheckState.Checked
            for i in range(1, self.count())
        )
        select_all_item = self.item(0)
        select_all_item.setCheckState(
            Qt.CheckState.Checked if all_checked else Qt.CheckState.Unchecked
        )

    def emit_checked_items(self) -> None:
        checked_items = [
            self.item(i).text()
            for i in range(1, self.count())  # skip "Select All"
            if self.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.checkedItemsChanged.emit(checked_items)
