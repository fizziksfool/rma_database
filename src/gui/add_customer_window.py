from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.models import add_customer


class AddCustomerWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.installEventFilter(self)
        self.create_gui()

    def create_gui(self) -> None:
        self.setFixedSize(300, 100)
        self.setWindowTitle('Add New Customer')

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
        customer_name = self.name_input.text()

        if add_customer(customer_name):
            self.accept()
        else:
            add_customer_failed_message(self)


def add_customer_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add customer. Invalid entry or customer already exists.'
    QMessageBox.critical(parent, title, message)
