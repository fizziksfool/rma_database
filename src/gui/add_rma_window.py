# new_rma_window.py

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.database import Customer, Department, ProductDescription, ProductNumber, User
from src.models import SessionLocal, add_rma, generate_rma_number


class AddNewRMAWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        generated_rma_number: str = generate_rma_number()
        self.create_gui(generated_rma_number)
        self.load_combobox_data()

    def create_gui(self, generated_rma_number: str) -> None:
        self.setFixedSize(400, 500)
        self.setWindowTitle('New RMA Entry')

        self.rma_number_label = QLabel('RMA #:')
        self.department_label = QLabel('Department:')
        self.customer_label = QLabel('Customer:')
        self.product_label = QLabel('Product:')
        self.part_number_label = QLabel('Part #:')
        self.user_label = QLabel('Issued by:')
        self.serial_number_label = QLabel('Serial #:')
        self.reason_label = QLabel('Reason for Return:')
        self.customer_po_label = QLabel('Customer PO #:')
        self.warranty_label = QLabel('Warranty')

        self.department_cbb = QComboBox()
        self.department_cbb.setStyleSheet('color: lightgreen;')
        self.customer_cbb = QComboBox()
        self.customer_cbb.setStyleSheet('color: lightgreen;')
        self.product_cbb = QComboBox()
        self.product_cbb.setStyleSheet('color: lightgreen;')
        self.part_number_cbb = QComboBox()
        self.part_number_cbb.setStyleSheet('color: lightgreen;')
        self.user_cbb = QComboBox()
        self.user_cbb.setStyleSheet('color: lightgreen;')

        self.serial_number_input = QLineEdit()
        self.reason_input = QLineEdit()
        self.customer_po_input = QLineEdit()
        self.rma_number_input = QLineEdit(generated_rma_number)
        self.rma_number_input.setDisabled(True)

        self.warranty_cb = QCheckBox()

        self.submit_btn = QPushButton('Submit')
        self.submit_btn.clicked.connect(self.add_new_rma)

        v_label_layout = QVBoxLayout()
        v_label_layout.addWidget(self.rma_number_label)
        v_label_layout.addWidget(self.department_label)
        v_label_layout.addWidget(self.customer_label)
        v_label_layout.addWidget(self.product_label)
        v_label_layout.addWidget(self.part_number_label)
        v_label_layout.addWidget(self.user_label)
        v_label_layout.addWidget(self.serial_number_label)
        v_label_layout.addWidget(self.reason_label)
        v_label_layout.addWidget(self.customer_po_label)
        v_label_layout.addWidget(self.warranty_label)

        v_input_layout = QVBoxLayout()
        v_input_layout.addWidget(self.rma_number_input)
        v_input_layout.addWidget(self.department_cbb)
        v_input_layout.addWidget(self.customer_cbb)
        v_input_layout.addWidget(self.product_cbb)
        v_input_layout.addWidget(self.part_number_cbb)
        v_input_layout.addWidget(self.user_cbb)
        v_input_layout.addWidget(self.serial_number_input)
        v_input_layout.addWidget(self.reason_input)
        v_input_layout.addWidget(self.customer_po_input)
        v_input_layout.addWidget(self.warranty_cb)

        h_label_input_layout = QHBoxLayout()
        h_label_input_layout.addLayout(v_label_layout)
        h_label_input_layout.addLayout(v_input_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_label_input_layout)
        main_layout.addWidget(self.submit_btn)

        self.setLayout(main_layout)

    def load_combobox_data(self) -> None:
        with SessionLocal() as session:
            self.departments = session.query(Department).all()
            self.customers = session.query(Customer).all()
            self.products = session.query(ProductDescription).all()
            self.part_numbers = session.query(ProductNumber).all()
            self.users = session.query(User).all()

            for dept in self.departments:
                self.department_cbb.addItem(dept.name, dept.id)

            for cust in self.customers:
                self.customer_cbb.addItem(cust.name, cust.id)

            for prod in self.products:
                self.product_cbb.addItem(prod.name, prod.id)

            for part_num in self.part_numbers:
                self.part_number_cbb.addItem(part_num.number, part_num.id)

            for user in self.users:
                self.user_cbb.addItem(user.name, user.id)

    def add_new_rma(self) -> None:
        rma_number = self.rma_number_input.text()
        department_id = self.department_cbb.currentData()
        customer_id = self.customer_cbb.currentData()
        product_id = self.customer_cbb.currentData()
        product_number_id = self.part_number_cbb.currentData()
        serial_number = self.serial_number_input.text()
        reason_for_return = self.reason_input.text()
        created_by_id = self.user_cbb.currentData()
        is_warranty = self.warranty_cb.isChecked()
        customer_po = self.customer_po_input.text()

        if not customer_po:
            customer_po = None

        if add_rma(
            rma_number=rma_number,
            department_id=department_id,
            customer_id=customer_id,
            product_id=product_id,
            product_number_id=product_number_id,
            serial_number=serial_number,
            reason_for_return=reason_for_return,
            created_by_id=created_by_id,
            is_warranty=is_warranty,
            customer_po=customer_po,
        ):
            self.accept()
        else:
            add_rma_failed_message(self)


def add_rma_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add new RMA.'
    QMessageBox.critical(parent, title, message)
