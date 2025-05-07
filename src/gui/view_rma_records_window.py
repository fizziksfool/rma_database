from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ViewRMARecordsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('RMA Records')
        self.set_window_size()
        self.create_gui()

    def set_window_size(self) -> None:
        aspect_ratio: dict[str, int] = {'width': 16, 'height': 9}
        scaling_factor: int = 80
        window_width: int = aspect_ratio['width'] * scaling_factor
        window_height: int = aspect_ratio['height'] * scaling_factor
        self.setFixedSize(window_width, window_height)

    def create_gui(self) -> None:
        self.rma_num_label = QLabel('RMA Record #')
        self.rma_num_display = QLabel()
        self.rma_num_display.setStyleSheet('color: lightgreen;')
        self.search_by_serial_num = QPushButton('Search by S/N')
        self.search_by_rma_num = QPushButton('Search by RMA #')
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
        self.reason_for_return_label = QLabel('Reason for Return')
        self.reason_for_return_input = QTextEdit()
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
        self.inspection_notes_input = QTextEdit()
        self.customer_po_num_label = QLabel('Cust. PO #')
        self.customer_po_num_input = QLineEdit()
        self.work_order_label = QLabel('WO #')
        self.work_order_input = QLineEdit()
        self.resolution_label = QLabel('Resolution')
        self.resolution_input = QTextEdit()
        self.shipped_back_date_label = QLabel('Shipped Back On')
        self.shipped_back_date_display = QDateEdit()
        self.shipped_back_date_display.setCalendarPopup(True)
        self.shipped_back_date_display.setStyleSheet('color: lightgreen;')
        self.issued_by_label = QLabel('Issued By')
        self.issued_by_display = QLabel()
        self.issued_by_display.setStyleSheet('color: lightgreen;')
        self.last_updated_label = QLabel('Last Updated')
        self.last_updated_display = QLabel()
        self.last_updated_display.setStyleSheet('color: lightgreen;')
        self.prev_button = QPushButton('\u23ea')  # '⏪︎'
        self.next_button = QPushButton('\u23e9')  # '⏩︎'
        self.go_to_first = QPushButton('\u23ee')  # '⏮︎'
        self.go_to_last = QPushButton('\u23ed')  # '⏭︎'

        main_layout = QVBoxLayout(self)

        self.setLayout(main_layout)
