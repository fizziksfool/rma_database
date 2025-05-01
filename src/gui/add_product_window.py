from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class AddProductWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.installEventFilter(self)
        self.create_gui()

    def create_gui(self) -> None:
        self.setFixedSize(300, 150)
        self.setWindowTitle('Add New Product')

        self.desc_label = QLabel('Product Description:')
        self.desc_input = QLineEdit()

        self.number_label = QLabel('Part Number:')
        self.number_input = QLineEdit()

        self.add_button = QPushButton('Add Product')
        self.add_button.clicked.connect(self.add_product)

        v_label_layout = QVBoxLayout()
        v_label_layout.addWidget(self.desc_label)
        v_label_layout.addWidget(self.number_label)

        v_input_layout = QVBoxLayout()
        v_input_layout.addWidget(self.desc_input)
        v_input_layout.addWidget(self.number_input)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_label_layout)
        h_layout.addLayout(v_input_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.add_button)

        self.setLayout(main_layout)

    def add_product(self) -> None:
        # Get customer name from input
        product_desc = self.desc_input.text()
        product_num = self.number_input.text()

        # Call your function to add the customer (make sure it’s imported)
        from src.models import add_product

        if add_product(product_desc, product_num):
            self.accept()
        else:
            add_product_failed_message(self)


def add_product_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add product description and number. Invalid entry or product and number already exists.'
    QMessageBox.critical(parent, title, message)
