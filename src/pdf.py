import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Literal

from fpdf import FPDF
from fpdf.enums import TableCellFillMode
from fpdf.fonts import FontFace
from PySide6.QtCore import QAbstractItemModel, Qt
from PySide6.QtWidgets import QTableView

MARGIN = 20.3  # mm
COL_WIDTHS = (
    17,  # RMA #
    24,  # Customer
    20,  # Product
    16,  # Part #
    19,  # Serial #
    41,  # Reason for Return
    22,  # Warranty
    17,  # Status
)
DATA_ALIGNMENT = ('C', 'C', 'C', 'C', 'C', 'L', 'C', 'C')


class PDF(FPDF):
    instance_number = 1

    def __init__(
        self,
        table: QTableView,
        orientation: Literal['landscape'] = 'landscape',
        unit: Literal['mm'] = 'mm',
        format: Literal['Letter'] = 'Letter',
    ) -> None:
        super().__init__(orientation, unit, format)
        self.set_margin(MARGIN)  # set all margin to the same value
        self.model: QAbstractItemModel = table.model()
        if self.model is None:
            raise ValueError('Table model is None')
        self.add_page()
        self._draw_title_bar()
        self._draw_table_header()
        self._draw_data_table()

    def _draw_title_bar(self) -> None:
        self.set_y(self.t_margin / 2)  # center the cursor within the header height
        root_dir: Path = Path(__file__).resolve().parents[1]
        logo_path: str = str(root_dir / 'assets' / 'op_logo.png')
        if Path(logo_path).exists():
            self.image(
                logo_path,
                x=self.r_margin / 2,
                y=self.t_margin / 2,
                w=40,
                keep_aspect_ratio=True,
            )
        self.set_font(family='Helvetica', style='B', size=24)
        self.cell(text='Open RMAs', align='C', center=True)

    def _draw_table_header(self) -> None:
        # Set fort for header rows
        self.set_font(family='Helvetica', style='B', size=14)
        self.set_x(self.l_margin)
        self.set_y(self.t_margin + 10)
        headers = (
            [
                str(
                    self.model.headerData(
                        col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
                    )
                )
                for col in range(self.model.columnCount())
            ],
        )
        headings_style = FontFace(emphasis='BOLD', color=0, fill_color=(50, 168, 82))
        with self.table(
            col_widths=COL_WIDTHS, text_align='C', headings_style=headings_style
        ) as table:
            for data_row in headers:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

    def _draw_data_table(self) -> None:
        font_size = 10
        self.set_font(family='Helvetica', size=font_size)
        x_start = self.l_margin
        y_start = self.get_y()
        self.set_xy(x_start, y_start)
        with self.table(
            borders_layout='ALL',
            col_widths=COL_WIDTHS,
            text_align=DATA_ALIGNMENT,
            first_row_as_headings=False,
            cell_fill_color=(194, 194, 194),
            cell_fill_mode=TableCellFillMode.ROWS,
            line_height=5,
        ) as table:
            for row in range(self.model.rowCount()):
                pdf_row = table.row()
                for col in range(self.model.columnCount()):
                    index = self.model.index(row, col)
                    datum = self.model.data(index, Qt.ItemDataRole.DisplayRole)
                    if datum is None:
                        datum = ''
                    if isinstance(datum, int):
                        datum = str(datum)
                    if isinstance(datum, datetime):
                        datum = datum.strftime('%Y-%m-%d')
                    pdf_row.cell(datum)

    def footer(self) -> None:
        self.set_y(-self.b_margin / 2)  # center the cursor within the footer height
        self.set_x(self.w - (self.r_margin / 2))
        self.set_font(family='Helvetica', style='I', size=8)
        self.cell(text=f'{self.page_no()}', align='C')

    def open(self) -> None:
        temp_dir = tempfile.gettempdir()
        pdf_path = Path(temp_dir) / f'open_rmas{self.__class__.instance_number}.pdf'

        self.output(str(pdf_path))

        # Open the PDF file using the default PDF viewer
        subprocess.run(
            ['start', '', str(pdf_path)],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.increment_instance_number()

    @classmethod
    def increment_instance_number(cls) -> None:
        cls.instance_number += 1
