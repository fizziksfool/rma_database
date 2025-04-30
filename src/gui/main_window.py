"""
Main Window
"""

import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QRegularExpression, Qt, Signal
from PySide6.QtGui import QAction, QIcon, QMouseEvent, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet


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

    def create_gui(self) -> None:
        input_box_width = 130
        input_box_height = 28
        window_width = 550
        window_height = 500

        self.setFixedSize(window_width, window_height)

        root_dir: Path = self._get_root_dir()
        icon_path: str = str(root_dir / 'assets' / 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f'Hyperion CSV Viewer v{self.version}')

        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(
            self.styleSheet() + """QLineEdit, QTextEdit {color: lightgreen;}"""
        )

        # Create the validator for numerical inputs
        number_regex = QRegularExpression(r'^-?\d*\.?\d*$')
        validator = QRegularExpressionValidator(number_regex)
        # '^-?': Matches an optional - at the beginning
        # '\d*': Matches zero or more digits
        # '\.?': Matches an optional decimal point
        # '\d*$': Matches zero or more digits after the decimal point, until the end of the string

        # Create the menu bar
        self.menu_bar = self.menuBar()

        # Create the menu bar items
        self.file_menu = self.menu_bar.addMenu('File')
        self.options_menu = self.menu_bar.addMenu('Options')
        self.save_menu = self.menu_bar.addMenu('Save')
        self.help_menu = self.menu_bar.addMenu('Help')

        # Create the QAction objects for the menus
        self.export_csv_option = QAction('Export Scan Data', self)
        self.exit_option = QAction('Exit', self)
        self.override_centroid_option = QAction('Override Centroid', self)
        self.override_centroid_option.setCheckable(True)
        self.save_3D_surface_option = QAction('Save 3D Surface', self)
        self.save_heatmap_option = QAction('Save Heatmap', self)
        self.save_xy_profiles_option = QAction('Save XY-Profiles', self)
        self.save_i_prime_option = QAction("Save I' vs Divergence Angle", self)
        self.save_all_html_option = QAction('Save all as HTML', self)
        self.save_all_png_option = QAction('Save all as png', self)
        self.open_quick_start_guide = QAction('Quick Start Guide', self)

        # Add the action objects to the menu bar items
        self.file_menu.addAction(self.export_csv_option)
        self.file_menu.addAction(self.exit_option)
        self.options_menu.addAction(self.override_centroid_option)
        self.save_menu.addAction(self.save_3D_surface_option)
        self.save_menu.addAction(self.save_heatmap_option)
        self.save_menu.addAction(self.save_xy_profiles_option)
        self.save_menu.addAction(self.save_i_prime_option)
        self.save_menu.addAction(self.save_all_html_option)
        self.save_menu.addAction(self.save_all_png_option)
        self.help_menu.addAction(self.open_quick_start_guide)

        # Create data entry fields and labels
        self.serial_number_label = QLabel('Serial Number')
        self.serial_number_input = QLineEdit()
        self.serial_number_input.setFixedSize(input_box_width, input_box_height)
        self.beam_voltage_label = QLabel('Beam Voltage (kV)')
        self.beam_voltage_input = QLineEdit()
        self.beam_voltage_input.setFixedSize(input_box_width, input_box_height)
        self.beam_voltage_input.setValidator(validator)
        self.ext_voltage_label = QLabel('Extractor Votage (kV)')
        self.ext_voltage_input = QLineEdit()
        self.ext_voltage_input.setFixedSize(input_box_width, input_box_height)
        self.ext_voltage_input.setValidator(validator)
        self.solenoid_current_label = QLabel('Solenoid Current (A)')
        self.solenoid_current_input = QLineEdit()
        self.solenoid_current_input.setFixedSize(input_box_width, input_box_height)
        self.solenoid_current_input.setValidator(validator)
        self.test_stand_label = QLabel('Test Stand')
        self.test_stand_input = QLineEdit()
        self.test_stand_input.setFixedSize(input_box_width, input_box_height)
        self.upper_bound_label = QLabel('Set Max Z (µA)')
        self.upper_bound_input = QLineEdit()
        self.upper_bound_input.setFixedSize(input_box_width, input_box_height)
        self.upper_bound_input.setValidator(validator)
        self.lower_bound_label = QLabel('Set Min Z (µA)')
        self.lower_bound_input = QLineEdit()
        self.lower_bound_input.setFixedSize(input_box_width, input_box_height)
        self.lower_bound_input.setValidator(validator)
        self.fcup_distance_label = QLabel('Dist. to Cup (mm)')
        self.fcup_distance_input = QLineEdit('205')
        self.fcup_distance_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.fcup_distance_input.setFixedSize(input_box_width, input_box_height)
        self.fcup_distance_input.setValidator(validator)
        self.fcup_diameter_label = QLabel('Cup Diam. (mm)')
        self.fcup_diameter_input = QLineEdit('2.5')
        self.fcup_diameter_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.fcup_diameter_input.setFixedSize(input_box_width, input_box_height)
        self.fcup_diameter_input.setValidator(validator)

        # Create buttons to select csv file and analyze beam scan
        self.select_csv_button = QPushButton('Select CSV File')
        self.select_csv_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plot_button = QPushButton('Plot Beam Scan')
        self.plot_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plot_button.setDisabled(True)

        # Create checkboxes to select which plot to show
        self.surface_cb = QCheckBox('3D Surface')
        self.surface_cb.setChecked(True)
        self.heatmap_cb = QCheckBox('Heatmap')
        self.heatmap_cb.setChecked(True)
        self.xy_profile_cb = QCheckBox('X/Y Slices')
        self.xy_profile_cb.setChecked(True)
        self.i_prime_cb = QCheckBox("I' vs Divergence")
        self.i_prime_cb.setChecked(True)

        main_layout = QHBoxLayout()

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)
