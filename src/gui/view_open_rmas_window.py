from PySide6.QtWidgets import QDialog, QTableView, QVBoxLayout
from sqlalchemy.orm import joinedload

from src.database import RMA, PartNumber, SessionLocal
from src.models import OpenRMAsTableModel


class ViewOpenRMAsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('View Open RMAs')

        layout = QVBoxLayout(self)
        self.table_view = QTableView(self)
        layout.addWidget(self.table_view)

        self.load_data()

    def load_data(self) -> None:
        with SessionLocal() as session:
            open_rmas = (
                session.query(RMA)
                .options(
                    joinedload(RMA.part_number).joinedload(PartNumber.product),
                    joinedload(RMA.customer),
                )
                .filter(RMA.status != 'Closed')
                .order_by(RMA.rma_number)
                .all()
            )

        self.model = OpenRMAsTableModel(open_rmas)
        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)

        for col, header in enumerate(self.model.headers):
            if header == 'Reason For Return':
                self.table_view.setColumnWidth(col, 200)
            else:
                self.table_view.setColumnWidth(col, 130)

        self.adjust_window_size()

    def adjust_window_size(self) -> None:
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
        header = self.table_view.horizontalHeader()
        headers_width = sum(header.sectionSize(i) for i in range(header.count()))

        index_width = self.table_view.verticalHeader().width()

        scrollbar_width = (
            self.table_view.verticalScrollBar().isVisible()
            * self.table_view.verticalScrollBar().sizeHint().width()
        )

        padding = 20

        full_width = index_width + headers_width + scrollbar_width + padding
        full_height = self.table_view.verticalHeader().length() + header.height() + 100

        self.resize(full_width, full_height)
