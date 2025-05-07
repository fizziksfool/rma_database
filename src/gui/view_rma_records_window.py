from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QGridLayout,
    QHBoxLayout,
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
        aspect_ratio: dict[str, int] = {'width': 4, 'height': 3}
        scaling_factor: int = 170
        window_width: int = aspect_ratio['width'] * scaling_factor
        window_height: int = aspect_ratio['height'] * scaling_factor
        self.setFixedSize(window_width, window_height)

    def create_gui(self) -> None:
        TEXT_BOX_HEIGHT = 36

        self.rma_num_label = QLabel('RMA Record #')
        self.rma_num_display = QLabel('#####')
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
        self.reason_for_return_text = QTextEdit()
        self.reason_for_return_text.setFixedHeight(TEXT_BOX_HEIGHT)
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
        self.inspection_notes_text.setFixedHeight(TEXT_BOX_HEIGHT)
        self.customer_po_num_label = QLabel('Cust. PO #')
        self.customer_po_num_input = QLineEdit()
        self.work_order_label = QLabel('WO #')
        self.work_order_input = QLineEdit()
        self.resolution_label = QLabel('Resolution')
        self.resolution_input = QTextEdit()
        self.resolution_input.setFixedHeight(TEXT_BOX_HEIGHT)
        self.shipped_back_date_label = QLabel('Shipped Back On')
        self.shipped_back_date_input = QLineEdit()
        self.shipped_back_date_input.setStyleSheet('color: lightgreen;')
        self.issued_by_label = QLabel('Issued By')
        self.issued_by_display = QLabel()
        self.issued_by_display.setStyleSheet('color: lightgreen;')
        self.last_updated_label = QLabel('Last Updated')
        self.last_updated_display = QLabel()
        self.last_updated_display.setStyleSheet('color: lightgreen;')
        self.prev_button = QPushButton('\u23ea')  # ⏪︎, \u23ea
        self.next_button = QPushButton('\u23e9')  # ⏩︎, \u23e9
        self.go_to_first = QPushButton('\u23ee')  # ⏮︎, \u23ee
        self.go_to_last = QPushButton('\u23ed')  # ⏭︎, \u23ed
        self.save_button = QPushButton('Save')

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.rma_num_label)
        top_layout.addWidget(self.rma_num_display)
        top_layout.addWidget(self.search_by_serial_num)
        top_layout.addWidget(self.search_by_rma_num)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.customer_label, 0, 0)
        grid_layout.addWidget(self.part_num_label, 1, 0)
        grid_layout.addWidget(self.product_label, 2, 0)
        grid_layout.addWidget(self.serial_num_label, 3, 0)
        grid_layout.addWidget(self.reason_for_return_label, 4, 0)
        grid_layout.addWidget(self.date_issued_label, 5, 0)
        grid_layout.addWidget(self.issued_by_label, 6, 0)
        grid_layout.addWidget(self.warranty_label, 7, 0)

        grid_layout.addWidget(self.customer_display, 0, 1)
        grid_layout.addWidget(self.part_num_display, 1, 1)
        grid_layout.addWidget(self.product_display, 2, 1)
        grid_layout.addWidget(self.serial_num_display, 3, 1)
        grid_layout.addWidget(self.reason_for_return_text, 4, 1)
        grid_layout.addWidget(self.date_issued_display, 5, 1)
        grid_layout.addWidget(self.issued_by_display, 6, 1)
        grid_layout.addWidget(self.warranty_cb, 7, 1)

        grid_layout.addWidget(QLabel('      '), 0, 2)  # empty widget for spacing

        grid_layout.addWidget(self.status_label, 0, 3)
        grid_layout.addWidget(self.customer_po_num_label, 1, 3)
        grid_layout.addWidget(self.work_order_label, 2, 3)
        grid_layout.addWidget(self.inspection_notes_label, 3, 3)
        grid_layout.addWidget(self.resolution_label, 4, 3)
        grid_layout.addWidget(self.last_updated_label, 5, 3)
        grid_layout.addWidget(self.shipped_back_date_label, 6, 3)

        grid_layout.addWidget(self.status_ccb, 0, 4)
        grid_layout.addWidget(self.customer_po_num_input, 1, 4)
        grid_layout.addWidget(self.work_order_input, 2, 4)
        grid_layout.addWidget(self.inspection_notes_text, 3, 4)
        grid_layout.addWidget(self.resolution_input, 4, 4)
        grid_layout.addWidget(self.last_updated_display, 5, 4)
        grid_layout.addWidget(self.shipped_back_date_input, 6, 4)

        sub1_bottom_layout = QHBoxLayout()
        sub1_bottom_layout.addWidget(self.save_button)

        sub2_bottom_layout = QHBoxLayout()
        sub2_bottom_layout.addWidget(self.go_to_first)
        sub2_bottom_layout.addWidget(self.prev_button)
        sub2_bottom_layout.addWidget(self.next_button)
        sub2_bottom_layout.addWidget(self.go_to_last)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(QLabel())  # empty widget for spacing
        bottom_layout.addLayout(sub1_bottom_layout)
        bottom_layout.addWidget(QLabel())  # emtpy widget for spacing
        bottom_layout.addLayout(sub2_bottom_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
