from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.database import Product, SessionLocal
from src.models import add_part_number


class AddPartNumberWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()

    def create_gui(self) -> None:
        self.setFixedSize(300, 150)
        self.setWindowTitle('Add New Part Number')

        # Create form elements
        self.desc_label = QLabel('Select Product:')
        self.desc_combo = QComboBox()
        self.desc_combo.setStyleSheet('color: lightgreen;')
        self.load_products()
        self.number_label = QLabel('Part Number:')
        self.number_input = QLineEdit()
        self.add_button = QPushButton('Add Part Number')
        self.add_button.clicked.connect(self.add_part_number)

        v_label_layout = QVBoxLayout()
        v_label_layout.addWidget(self.desc_label)
        v_label_layout.addWidget(self.number_label)

        v_input_layout = QVBoxLayout()
        v_input_layout.addWidget(self.desc_combo)
        v_input_layout.addWidget(self.number_input)

        h_layout = QHBoxLayout()
        h_layout.addLayout(v_label_layout)
        h_layout.addLayout(v_input_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.add_button)

        self.setLayout(main_layout)

    def load_products(self) -> None:
        with SessionLocal() as session:
            products = session.query(Product).order_by(Product.name).all()
            for prod in products:
                self.desc_combo.addItem(prod.name, prod.id)

    def add_part_number(self) -> None:
        product_id = self.desc_combo.currentData()
        number = self.number_input.text()

        if add_part_number(product_id, number):
            self.accept()
        else:
            add_part_number_failed_message(self)


def add_part_number_failed_message(parent) -> None:
    title = 'Error'
    message = (
        'Failed to add product number. Invalid entry or product number already exists.'
    )
    QMessageBox.critical(parent, title, message)
