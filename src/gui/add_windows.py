from collections import defaultdict
from datetime import datetime

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from sqlalchemy import func

from ..api import (
    add_customer,
    add_part_number,
    add_product,
    add_rma,
    add_user,
)
from ..database import RMA, Customer, PartNumber, Product, SessionLocal, User
from .error_messages import (
    add_customer_failed_message,
    add_part_number_failed_message,
    add_product_failed_message,
    add_rma_failed_message,
    add_user_failed_message,
)


class AddCustomerWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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


class AddProductWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()

    def create_gui(self) -> None:
        self.setFixedSize(300, 150)
        self.setWindowTitle('Add New Product')

        self.desc_label = QLabel('Product:')
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
        product_desc = self.desc_input.text()
        product_num = self.number_input.text()

        if add_product(product_desc, product_num):
            self.accept()
        else:
            add_product_failed_message(self)


class AddRMAWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.part_numbers_by_product = defaultdict(list)
        generated_rma_number: str = self.generate_rma_number()
        self.create_gui(generated_rma_number)
        self.load_combobox_data()
        self.update_part_numbers()

    def generate_rma_number(self) -> str:
        year_prefix = datetime.now().strftime('%y')
        base = int(year_prefix) * 1000

        with SessionLocal() as session:
            latest = (
                session.query(func.max(RMA.rma_number))
                .filter(RMA.rma_number.like(f'{year_prefix}%'))
                .scalar()
            )

            if latest:
                return str(int(latest) + 1)
            else:
                return str(base + 1)

    def create_gui(self, generated_rma_number: str) -> None:
        self.setFixedSize(400, 500)
        self.setWindowTitle('New RMA Entry')

        self.rma_number_label = QLabel('RMA #:')
        self.customer_label = QLabel('Customer:')
        self.product_label = QLabel('Product:')
        self.part_number_label = QLabel('Part #:')
        self.user_label = QLabel('Issued by:')
        self.serial_number_label = QLabel('Serial #:')
        self.reason_label = QLabel('Reason for Return:')
        self.customer_po_label = QLabel('Customer PO #:')
        self.warranty_label = QLabel('Warranty')

        self.customer_cbb = QComboBox()
        self.customer_cbb.setStyleSheet('color: lightgreen;')
        self.product_cbb = QComboBox()
        self.product_cbb.setStyleSheet('color: lightgreen;')
        self.product_cbb.currentIndexChanged.connect(self.update_part_numbers)
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
            self.customers = session.query(Customer).all()
            self.products = session.query(Product).all()
            self.users = session.query(User).all()
            part_numbers = session.query(PartNumber).all()

        for cust in self.customers:
            self.customer_cbb.addItem(cust.name, cust.id)

        for prod in self.products:
            self.product_cbb.addItem(prod.name, prod.id)

        for user in self.users:
            self.user_cbb.addItem(user.name, user.id)

        for num in part_numbers:
            self.part_numbers_by_product[num.product_id].append(num)

    def update_part_numbers(self) -> None:
        selected_product_id = self.product_cbb.currentData()
        self.part_number_cbb.clear()

        if selected_product_id is not None:
            matching_parts = self.part_numbers_by_product.get(selected_product_id, [])
            for part in matching_parts:
                self.part_number_cbb.addItem(part.number, part.id)

    def add_new_rma(self) -> None:
        rma_number = self.rma_number_input.text()
        customer_id = self.customer_cbb.currentData()
        part_number_id = self.part_number_cbb.currentData()
        serial_number = self.serial_number_input.text()
        reason_for_return = self.reason_input.text()
        issued_by_id = self.user_cbb.currentData()
        is_warranty = self.warranty_cb.isChecked()
        customer_po_number = self.customer_po_input.text()

        if not customer_po_number:
            customer_po_number = None

        if add_rma(
            rma_number=rma_number,
            customer_id=customer_id,
            part_number_id=part_number_id,
            serial_number=serial_number,
            reason_for_return=reason_for_return,
            issued_by_id=issued_by_id,
            is_warranty=is_warranty,
            customer_po_number=customer_po_number,
        ):
            self.accept()
        else:
            add_rma_failed_message(self)


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
