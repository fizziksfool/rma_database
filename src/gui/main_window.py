import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet

from .add_windows import (
    AddCustomerWindow,
    AddPartNumberWindow,
    AddProductWindow,
    AddRMAWindow,
    AddUserWindow,
)
from .view_open_rmas_window import ViewOpenRMAsWindow
from .view_rma_records_window import ViewRMARecordsWindow
from .view_rma_table_window import ViewRMATable


class MainWindow(QMainWindow):
    def __init__(self, version: str) -> None:
        super().__init__()
        self.version = version
        self.installEventFilter(self)
        self.create_gui()

    def _get_root_dir(self) -> Path:
        if getattr(sys, 'frozen', False):  # Check if running from the PyInstaller EXE
            return Path(getattr(sys, '_MEIPASS', '.'))
        else:  # Running in a normal Python environment
            return Path(__file__).resolve().parents[2]

    def _handle_exit(self) -> None:
        QApplication.quit()

    def _handle_add_customer(self) -> None:
        add_customer_window = AddCustomerWindow(self)
        add_customer_window.exec()

    def _handle_add_user(self) -> None:
        add_customer_window = AddUserWindow(self)
        add_customer_window.exec()

    def _handle_add_product(self) -> None:
        add_product_window = AddProductWindow(self)
        add_product_window.exec()

    def _handle_add_part_number(self) -> None:
        add_part_number_window = AddPartNumberWindow(self)
        add_part_number_window.exec()

    def _handle_add_new_rma_button(self) -> None:
        add_new_rma_window = AddRMAWindow(self)
        add_new_rma_window.exec()

    def _handle_view_open_rmas_button(self) -> None:
        view_open_rmas_window = ViewOpenRMAsWindow(self)
        view_open_rmas_window.show()

    def _handle_view_rma_table_button(self) -> None:
        view_rma_table_window = ViewRMATable(self)
        view_rma_table_window.show()

    def _handle_view_rma_records_button(self) -> None:
        view_rma_records_window = ViewRMARecordsWindow(self)
        view_rma_records_window.show()

    def create_gui(self) -> None:
        window_width = 550
        window_height = 500

        self.setFixedSize(window_width, window_height)

        root_dir: Path = self._get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f'RMA Database v{self.version}')

        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(
            self.styleSheet() + """QLineEdit, QTextEdit {color: lightgreen;}"""
        )

        # Create the validator for numerical inputs
        # number_regex = QRegularExpression(r'^-?\d*\.?\d*$')
        # validator = QRegularExpressionValidator(number_regex)
        # '^-?': Matches an optional - at the beginning
        # '\d*': Matches zero or more digits
        # '\.?': Matches an optional decimal point
        # '\d*$': Matches zero or more digits after the decimal point, until the end of the string

        # Create the menu bar
        self.menu_bar = self.menuBar()

        # Create the menu bar items
        self.file_menu = self.menu_bar.addMenu('File')
        self.options_menu = self.menu_bar.addMenu('Options')
        self.help_menu = self.menu_bar.addMenu('Help')

        # Create the QAction objects for the menus
        self.exit_option = QAction('Exit', self)
        self.add_customer_option = QAction('Add New Customer', self)
        self.add_product_option = QAction('Add New Product', self)
        self.add_part_number_option = QAction('Add New Part Number to Product', self)
        self.add_user_option = QAction('Add New User', self)
        self.open_quick_start_guide = QAction('Quick Start Guide', self)

        # Add the action objects to the menu bar items
        self.file_menu.addAction(self.exit_option)
        self.options_menu.addAction(self.add_customer_option)
        self.options_menu.addAction(self.add_product_option)
        self.options_menu.addAction(self.add_part_number_option)
        self.options_menu.addAction(self.add_user_option)
        self.help_menu.addAction(self.open_quick_start_guide)

        self.exit_option.triggered.connect(self._handle_exit)
        self.add_customer_option.triggered.connect(self._handle_add_customer)
        self.add_product_option.triggered.connect(self._handle_add_product)
        self.add_part_number_option.triggered.connect(self._handle_add_part_number)
        self.add_user_option.triggered.connect(self._handle_add_user)

        # Create buttons to select csv file and analyze beam scan
        self.add_new_rma_button = QPushButton('Add New RMA')
        self.add_new_rma_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_rma_records_button = QPushButton('View RMA Records')
        self.view_rma_records_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_open_rmas_button = QPushButton('View Open RMAs')
        self.view_open_rmas_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_all_rmas_button = QPushButton('View RMA Table')
        self.view_all_rmas_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.add_new_rma_button.clicked.connect(self._handle_add_new_rma_button)
        self.view_rma_records_button.clicked.connect(
            self._handle_view_rma_records_button
        )
        self.view_open_rmas_button.clicked.connect(self._handle_view_open_rmas_button)
        self.view_all_rmas_button.clicked.connect(self._handle_view_rma_table_button)

        v_button_layout = QVBoxLayout()
        v_button_layout.addWidget(self.add_new_rma_button)
        v_button_layout.addWidget(self.view_rma_records_button)
        v_button_layout.addWidget(self.view_open_rmas_button)
        v_button_layout.addWidget(self.view_all_rmas_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(v_button_layout)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)


if __name__ == '__main__':
    version = '2.0.0'
    app = QApplication([])
    window = MainWindow(version=version)  # Create the main window from main_window.py
    window.show()  # Show the window
    sys.exit(app.exec())
