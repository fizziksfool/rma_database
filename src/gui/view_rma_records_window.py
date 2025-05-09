from datetime import datetime

from PySide6.QtCore import QDate, QRegularExpression, Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..api import (
    get_newest_rma_num,
    get_oldest_rma_num,
    get_rma_by_rma_num,
    get_rma_by_sn,
    overwrite_rma_record,
)
from ..database import RMA
from .error_messages import overwrite_record_failed_message


class ViewRMARecordsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('RMA Records')
        self.set_window_size()
        self.create_gui()
        rma: RMA | None = None
        last_rma: str | None = get_newest_rma_num()
        if last_rma is not None:
            rma = get_rma_by_rma_num(last_rma)
        if rma is not None:
            self.load_rma_data(rma)

    def _handle_save_button_pressed(self) -> None:
        rma_number = self.rma_num_display.text()
        self.save_changes(rma_number)

    def _handle_search_by_sn_button_pressed(self) -> None:
        sn_search_window = SNSearchWindow(self)
        sn_search_window.searched_rma.connect(self._process_search_input)
        sn_search_window.exec()

    def _handle_search_by_rma_button_pressed(self) -> None:
        rma_search_window = RMASearchWindow(self)
        rma_search_window.searched_rma.connect(self._process_search_input)
        rma_search_window.exec()

    def _process_search_input(self, rma: RMA) -> None:
        self.load_rma_data(rma)

    def _handle_go_to_first_button_pressed(self) -> None:
        self.get_first_rma()

    def _handle_prev_button_pressed(self) -> None:
        current_rma_number = self.rma_num_display.text()
        self.get_prev_rma(current_rma_number)

    def _handle_next_button_pressed(self) -> None:
        current_rma_number = self.rma_num_display.text()
        self.get_next_rma(current_rma_number)

    def _handle_go_to_last_button_pressed(self) -> None:
        self.get_last_rma()

    def set_window_size(self) -> None:
        aspect_ratio: dict[str, int] = {'width': 4, 'height': 3}
        scaling_factor: int = 170
        window_width: int = aspect_ratio['width'] * scaling_factor
        window_height: int = aspect_ratio['height'] * scaling_factor
        self.setFixedSize(window_width, window_height)

    def create_gui(self) -> None:
        self.rma_num_label = QLabel('RMA Record #')
        self.rma_num_label.setStyleSheet('font-size: 20pt;')
        self.rma_num_display = QLabel()
        self.rma_num_display.setStyleSheet('color: lightgreen; font-size: 20pt;')
        self.search_by_serial_num_button = QPushButton('Search by S/N')
        self.search_by_rma_num_button = QPushButton('Search by RMA #')
        self.customer_label = QLabel('Customer')
        self.customer_display = QLabel()
        self.customer_display.setStyleSheet('color: lightgreen;')
        self.part_num_label = QLabel('Part Number')
        self.part_num_display = QLabel()
        self.part_num_display.setStyleSheet('color: lightgreen;')
        self.product_label = QLabel('Product')
        self.product_display = QLabel()
        self.product_display.setStyleSheet('color: lightgreen;')
        self.serial_num_label = QLabel('Serial Number')
        self.serial_num_display = QLabel()
        self.serial_num_display.setStyleSheet('color: lightgreen;')
        self.reason_for_return_label = QLabel('Returned For')
        self.reason_for_return_text = QTextEdit()
        self.reason_for_return_text.setFixedHeight(36)
        self.date_issued_label = QLabel('Date Issued')
        self.date_issued_display = QLabel()
        self.date_issued_display.setStyleSheet('color: lightgreen;')
        self.warranty_label = QLabel('Warranty')
        self.warranty_cb = QCheckBox()
        self.status_label = QLabel('Status')
        self.status_ccb = QComboBox()
        self.status_ccb.addItems(
            ['Issued', 'Received', 'In Process', 'Complete', 'Closed']
        )
        self.status_ccb.setStyleSheet('color: lightgreen;')
        self.inspection_notes_label = QLabel('Inspection Notes')
        self.inspection_notes_text = QTextEdit()
        self.customer_po_num_label = QLabel('Cust. PO #')
        self.customer_po_num_input = QLineEdit()
        self.work_order_label = QLabel('WO #')
        self.work_order_input = QLineEdit()
        self.resolution_label = QLabel('Resolution')
        self.resolution_input = QTextEdit()
        self.shipped_back_date_label = QLabel('Shipped Back On')
        self.shipped_back_date_input = DateLineEdit()
        self.shipped_back_date_input.setPlaceholderText('Select a date...')
        self.shipped_back_date_input.setStyleSheet('color: lightgreen;')
        self.issued_by_label = QLabel('Issued By')
        self.issued_by_display = QLabel()
        self.issued_by_display.setStyleSheet('color: lightgreen;')
        self.last_updated_label = QLabel('Last Updated')
        self.last_updated_display = QLabel()
        self.last_updated_display.setStyleSheet('color: lightgreen;')
        self.prev_button = QPushButton('\u23ea')  # ⏪︎, \u23ea
        self.next_button = QPushButton('\u23e9')  # ⏩︎, \u23e9
        self.go_to_first_button = QPushButton('\u23ee')  # ⏮︎, \u23ee
        self.go_to_last_button = QPushButton('\u23ed')  # ⏭︎, \u23ed
        self.save_button = QPushButton('Save')

        self.save_button.clicked.connect(self._handle_save_button_pressed)
        self.search_by_serial_num_button.clicked.connect(
            self._handle_search_by_sn_button_pressed
        )
        self.search_by_rma_num_button.clicked.connect(
            self._handle_search_by_rma_button_pressed
        )
        self.prev_button.clicked.connect(self._handle_prev_button_pressed)
        self.next_button.clicked.connect(self._handle_next_button_pressed)
        self.go_to_first_button.clicked.connect(self._handle_go_to_first_button_pressed)
        self.go_to_last_button.clicked.connect(self._handle_go_to_last_button_pressed)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.rma_num_label)
        top_layout.addWidget(self.rma_num_display, Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(self.search_by_serial_num_button)
        top_layout.addWidget(self.search_by_rma_num_button)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.customer_label, 0, 0)
        grid_layout.addWidget(self.part_num_label, 1, 0)
        grid_layout.addWidget(self.product_label, 2, 0, Qt.AlignmentFlag.AlignTop)
        grid_layout.addWidget(self.serial_num_label, 3, 0)
        grid_layout.addWidget(self.reason_for_return_label, 4, 0)
        grid_layout.addWidget(self.date_issued_label, 5, 0)
        grid_layout.addWidget(self.issued_by_label, 6, 0)
        grid_layout.addWidget(self.warranty_label, 7, 0)
        grid_layout.addWidget(self.status_label, 8, 0)

        grid_layout.addWidget(self.customer_display, 0, 1)
        grid_layout.addWidget(self.part_num_display, 1, 1)
        grid_layout.addWidget(self.product_display, 2, 1)
        grid_layout.addWidget(self.serial_num_display, 3, 1)
        grid_layout.addWidget(self.reason_for_return_text, 4, 1)
        grid_layout.addWidget(self.date_issued_display, 5, 1)
        grid_layout.addWidget(self.issued_by_display, 6, 1)
        grid_layout.addWidget(self.warranty_cb, 7, 1)
        grid_layout.addWidget(self.status_ccb, 8, 1)

        grid_layout.addWidget(QLabel('      '), 0, 2)  # empty widget for spacing

        grid_layout.addWidget(self.customer_po_num_label, 0, 3)
        grid_layout.addWidget(self.work_order_label, 1, 3)
        grid_layout.addWidget(
            self.inspection_notes_label, 2, 3, Qt.AlignmentFlag.AlignTop
        )
        grid_layout.addWidget(self.resolution_label, 5, 3, Qt.AlignmentFlag.AlignTop)
        grid_layout.addWidget(self.last_updated_label, 7, 3)
        grid_layout.addWidget(self.shipped_back_date_label, 8, 3)

        grid_layout.addWidget(self.customer_po_num_input, 0, 4)
        grid_layout.addWidget(self.work_order_input, 1, 4)
        grid_layout.addWidget(self.inspection_notes_text, 2, 4, 3, 1)
        grid_layout.addWidget(self.resolution_input, 5, 4, 2, 1)
        grid_layout.addWidget(self.last_updated_display, 7, 4)
        grid_layout.addWidget(self.shipped_back_date_input, 8, 4)

        nav_buttons_layout = QHBoxLayout()
        nav_buttons_layout.addWidget(self.go_to_first_button)
        nav_buttons_layout.addWidget(self.prev_button)
        nav_buttons_layout.addWidget(self.next_button)
        nav_buttons_layout.addWidget(self.go_to_last_button)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(QLabel())  # empty widget for spacing
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(QLabel())  # emtpy widget for spacing
        bottom_layout.addLayout(nav_buttons_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def load_rma_data(self, rma: RMA) -> None:
        self.rma_num_display.setText(rma.rma_number)
        self.customer_display.setText(rma.customer.name.upper())
        self.part_num_display.setText(rma.part_number.number)
        self.product_display.setText(rma.part_number.product.name.upper())
        self.serial_num_display.setText(rma.serial_number)
        self.reason_for_return_text.setPlainText(rma.reason_for_return)
        self.date_issued_display.setText(rma.issued_on.strftime('%Y-%m-%d'))
        self.issued_by_display.setText(rma.issued_by.name.upper())
        self.warranty_cb.setChecked(rma.is_warranty)
        self.status_ccb.setCurrentText(rma.status)
        self.customer_po_num_input.setText(rma.customer_po_number)
        self.work_order_input.setText(rma.work_order)
        self.inspection_notes_text.setPlainText(rma.incoming_inspection_notes)
        self.resolution_input.setPlainText(rma.resolution_notes)
        self.last_updated_display.setText(rma.last_updated.strftime('%Y-%m-%d'))
        if rma.shipped_back_on:
            self.shipped_back_date_input.setText(
                rma.shipped_back_on.strftime('%Y-%m-%d')
            )
        if rma.status == 'Closed':
            self.shipped_back_date_input.setEnabled(False)

    def save_changes(self, rma_number: str) -> None:
        entries: list[str | datetime | bool] = [
            self.reason_for_return_text.toPlainText(),
            self.warranty_cb.isChecked(),
            self.status_ccb.currentText(),
            self.customer_po_num_input.text(),
            self.work_order_input.text(),
            self.inspection_notes_text.toPlainText(),
            self.resolution_input.toPlainText(),
            datetime.strptime(self.shipped_back_date_input.text(), '%Y-%m-%d'),
        ]

        record_overwritten = overwrite_rma_record(rma_number, entries)

        if record_overwritten is not True:
            overwrite_record_failed_message(self)
            return
        QMessageBox.information(
            self, 'Record Saved', f'RMA-{self.rma_num_display.text()} has been saved.'
        )

    def get_first_rma(self) -> None:
        rma: RMA | None = None
        first_rma: str | None = get_oldest_rma_num()
        if first_rma is not None:
            rma = get_rma_by_rma_num(first_rma)
        if rma is not None:
            self.load_rma_data(rma)

    def get_prev_rma(self, current_rma_num: str) -> None:
        current_num = int(current_rma_num)

        try:
            max_lookback = 1000
            for i, num in enumerate(range(current_num - 1, 0, -1)):
                if i >= max_lookback:
                    break
                rma = get_rma_by_rma_num(str(num))
                if rma is not None:
                    self.load_rma_data(rma)
                    return
        except Exception as e:
            QMessageBox.critical(
                self, 'Error', f'An error occured while searching: {str(e)}'
            )

        QMessageBox.information(
            self, 'No Previous Record', 'This is the first available RMA record.'
        )

    def get_next_rma(self, current_rma_num: str) -> None:
        current_num = int(current_rma_num)

        latest_rma_str = get_newest_rma_num()
        if latest_rma_str is None:
            return
        latest_rma_num = int(latest_rma_str)

        try:
            max_lookup = 100
            for i, num in enumerate(range(current_num + 1, latest_rma_num + 1)):
                if i >= max_lookup:
                    break
                rma = get_rma_by_rma_num(str(num))
                if rma is not None:
                    self.load_rma_data(rma)
                    return
        except Exception as e:
            QMessageBox.critical(
                self, 'Error', f'An error occured while searching: {str(e)}'
            )

        QMessageBox.information(
            self, 'No Next Record', 'This is the last available RMA record.'
        )

    def get_last_rma(self) -> None:
        rma: RMA | None = None
        last_rma: str | None = get_newest_rma_num()
        if last_rma is not None:
            rma = get_rma_by_rma_num(last_rma)
        if rma is not None:
            self.load_rma_data(rma)


class CalendarPopup(QCalendarWidget):
    def __init__(self, parent=None, line_edit: QLineEdit | None = None) -> None:
        super().__init__(parent)
        self.line_edit = line_edit
        self.setWindowFlags(Qt.WindowType.Popup)
        self.clicked.connect(self.on_date_selected)

    def on_date_selected(self, date: QDate) -> None:
        if self.line_edit:
            self.line_edit.setText(date.toString('yyyy-MM-dd'))
        self.hide()


class DateLineEdit(QLineEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.calendar_popup = CalendarPopup(parent=self, line_edit=self)

    def mousePressEvent(self, event) -> None:
        if not self.calendar_popup.isVisible():
            self.show_calendar()

    def show_calendar(self) -> None:
        self.calendar_popup.move(self.mapToGlobal(self.rect().bottomLeft()))
        self.calendar_popup.show()


class SNSearchWindow(QDialog):
    searched_rma = Signal(RMA)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()

    def _handle_search_button_pressed(self) -> None:
        serial_number = self.sn_input.text()
        self.search_by_sn(serial_number)

    def create_gui(self) -> None:
        self.setFixedSize(300, 100)
        self.setWindowTitle('Search RMAs by Serial Number')

        self.sn_label = QLabel('Serial Number')
        self.sn_input = QLineEdit()

        regex = QRegularExpression(r'^[a-zA-Z0-9]*$')
        validator = QRegularExpressionValidator(regex)
        self.sn_input.setValidator(validator)

        self.search_button = QPushButton('Search')

        self.search_button.clicked.connect(self._handle_search_button_pressed)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.sn_label)
        h_layout.addWidget(self.sn_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.search_button)

        self.setLayout(main_layout)

    def search_by_sn(self, serial_number: str) -> None:
        rma: RMA | None = get_rma_by_sn(serial_number, fuzzy=True)
        if rma is not None:
            self.searched_rma.emit(rma)
            self.accept()
        else:
            QMessageBox.warning(
                self, 'No Record Found', f'SN-{serial_number} not found.'
            )


class RMASearchWindow(QDialog):
    searched_rma = Signal(RMA)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()

    def _handle_search_button_pressed(self) -> None:
        rma_number = self.rma_input.text()
        self.search_by_rma(rma_number)

    def create_gui(self) -> None:
        self.setFixedSize(300, 100)
        self.setWindowTitle('Search RMAs by RMA Number')

        self.rma_label = QLabel('RMA Number')
        self.rma_input = QLineEdit()

        regex = QRegularExpression(r'^\d*$')
        validator = QRegularExpressionValidator(regex)
        self.rma_input.setValidator(validator)

        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self._handle_search_button_pressed)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.rma_label)
        h_layout.addWidget(self.rma_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.search_button)

        self.setLayout(main_layout)

    def search_by_rma(self, rma_number: str) -> None:
        rma: RMA | None = get_rma_by_rma_num(rma_number)
        if rma is not None:
            self.searched_rma.emit(rma)
            self.accept()
        else:
            QMessageBox.warning(self, 'No Record Found', f'RMA-{rma_number} not found.')
