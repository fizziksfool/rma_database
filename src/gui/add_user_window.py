from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.models import add_user


class AddUserWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()

    def create_gui(self) -> None:
        self.setFixedSize(300, 100)
        self.setWindowTitle('Add New User')

        # Create form elements
        self.name_label = QLabel('User Name:')
        self.name_input = QLineEdit()
        self.add_button = QPushButton('Add User')
        self.add_button.clicked.connect(self.add_new_user)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.name_label)
        h_layout.addWidget(self.name_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.add_button)

        self.setLayout(main_layout)

    def add_new_user(self) -> None:
        user_name = self.name_input.text()

        if add_user(user_name):
            self.accept()
        else:
            add_user_failed_message(self)


def add_user_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add user. Invalid entry or user already exists.'
    QMessageBox.critical(parent, title, message)
