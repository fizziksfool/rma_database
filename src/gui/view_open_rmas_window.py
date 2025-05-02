# view_open_rmas_window.py

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QTableWidget,
    QVBoxLayout,
)

from src.models import view_open_rmas


class ViewOpenRMAsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.create_gui()
        self.load_data()

    def create_gui(self) -> None:
        self.setWindowTitle('Open RMAs')

        layout = QVBoxLayout()

        self.label = QLabel('Open RMAs:')
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)

        layout.addWidget(self.label)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self) -> None:
        try:
            view_open_rmas(self.table)
            self.adjust_table_and_window_size()
        except Exception as e:
            QMessageBox.critical(
                self, 'Database Error', f'Failed to load open RMAs:\n{e}'
            )

    def adjust_table_and_window_size(self) -> None:
        """
        Adjusts the size of the dialog window to fit the contents of the table.

        This method calculates the total width of all visible columns in the table,
        accounts for the width of the vertical scrollbar and layout padding, and resizes
        the window accordingly. It also adjusts the height based on the number of visible
        rows and the header height, ensuring the table content is fully visible without
        clipping or excessive space.

        Note:
            This adjustment is typically called after populating the table with data
            and calling resizeColumnsToContents().
        """
        header = self.table.horizontalHeader()
        headers_width = sum(header.sectionSize(i) for i in range(header.count()))

        index_width = self.table.verticalHeader().width()

        scrollbar_width = (
            self.table.verticalScrollBar().isVisible()
            * self.table.verticalScrollBar().sizeHint().width()
        )

        padding = 20

        full_width = index_width + headers_width + scrollbar_width + padding
        full_height = self.table.verticalHeader().length() + header.height() + 100

        self.resize(full_width, full_height)
