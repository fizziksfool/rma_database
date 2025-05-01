# add_customer_window.py
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from qt_material import apply_stylesheet


class AddProductWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.installEventFilter(self)
        self.create_gui()

    def _get_root_dir(self) -> Path:
        if getattr(sys, 'frozen', False):  # Check if running from the PyInstaller EXE
            return Path(getattr(sys, '_MEIPASS', '.'))
        else:  # Running in a normal Python environment
            return Path(__file__).resolve().parents[2]

    def create_gui(self) -> None:
        self.setFixedSize(300, 150)

        root_dir: Path = self._get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle('Add New Product')

        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(
            self.styleSheet() + """QLineEdit, QTextEdit {color: lightgreen;}"""
        )

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
