from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.models import add_department


class AddDepartmentWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()

    def create_gui(self) -> None:
        self.setFixedSize(300, 100)
        self.setWindowTitle('Add New Department')

        # Create form elements
        self.name_label = QLabel('Department:')
        self.name_input = QLineEdit()
        self.add_button = QPushButton('Add Department')
        self.add_button.clicked.connect(self.add_new_department)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.name_label)
        h_layout.addWidget(self.name_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.add_button)

        self.setLayout(main_layout)

    def add_new_department(self) -> None:
        dept_name = self.name_input.text()

        if add_department(dept_name):
            self.accept()
        else:
            add_user_failed_message(self)


def add_user_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add user. Invalid entry or user already exists.'
    QMessageBox.critical(parent, title, message)
