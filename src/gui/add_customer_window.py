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


class AddCustomerWindow(QDialog):
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
        self.resize(300, 100)

        root_dir: Path = self._get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle('Add New Customer')

        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(
            self.styleSheet() + """QLineEdit, QTextEdit {color: lightgreen;}"""
        )

        # Create form elements
        self.name_label = QLabel('Customer Name:')
        self.name_input = QLineEdit()
        self.add_button = QPushButton('Add Customer')
        self.add_button.clicked.connect(self.add_customer)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.name_label)
        h_layout.addWidget(self.name_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.add_button)

        self.setLayout(main_layout)

    def add_customer(self) -> None:
        # Get customer name from input
        customer_name = self.name_input.text()

        # Call your function to add the customer (make sure it’s imported)
        from src.models import add_customer

        if add_customer(customer_name):
            self.accept()
        else:
            add_customer_failed_message(self)


def add_customer_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add customer. Invalid entry or customer already exists.'
    QMessageBox.critical(parent, title, message)
