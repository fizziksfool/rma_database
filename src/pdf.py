import os
import tempfile
from pathlib import Path

from fpdf import FPDF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView


def generate_pdf(table_view: QTableView, pdf_path: Path) -> Path | None:
    model = table_view.model()
    if model is None:
        return

    pdf = FPDF(orientation='L', unit='mm', format='Letter')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    column_count = model.columnCount()
    row_count = model.rowCount()

    # Step 1: Calculate usable width
    available_width = pdf.w - pdf.l_margin - pdf.r_margin

    # Step 2: Set header font and measure widths
    pdf.set_font('Arial', size=12, style='B')
    headers = [
        str(
            model.headerData(
                col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            )
        )
        for col in range(column_count)
    ]
    raw_widths = [pdf.get_string_width(h) + 4 for h in headers]
    total_raw_width = sum(raw_widths)
    scale = available_width / total_raw_width
    col_widths = [w * scale for w in raw_widths]  # locked widths

    # Step 3: Draw header row
    y_start = pdf.get_y()
    pdf.set_x(pdf.l_margin)
    for i in range(column_count):
        pdf.cell(col_widths[i], 10, headers[i], border=1, align='C')
    pdf.ln()

    # Step 4: Set font for data rows
    pdf.set_font('Arial', size=10)

    # Step 5: Draw data rows with wrapping
    PADDING_LEFT = 1.5
    PADDING_TOP = 1
    LINE_HEIGHT = 5
    bottom_margin = 10
    page_height = pdf.h - bottom_margin

    for row in range(row_count):
        x_start = pdf.l_margin
        y_start = pdf.get_y()

        cell_texts = []
        line_counts = []

        # Get content and number of lines per cell
        for col in range(column_count):
            index = model.index(row, col)
            data = str(model.data(index, Qt.ItemDataRole.DisplayRole)) or ''
            text_width = col_widths[col] - 2 * PADDING_LEFT
            lines = pdf.multi_cell(
                text_width, LINE_HEIGHT, data, border=0, align='L', split_only=True
            )
            cell_texts.append(data)
            line_counts.append(len(lines))

        max_lines = max(line_counts)
        row_height = max_lines * LINE_HEIGHT + 2 * PADDING_TOP

        # Check for page break
        if y_start + row_height > page_height:
            pdf.add_page()
            y_start = pdf.get_y()

        # Draw the full row
        for col in range(column_count):
            pdf.set_xy(x_start, y_start)
            # Draw the cell border
            pdf.cell(col_widths[col], row_height, '', border=1)

            # Draw the text inside the cell
            pdf.set_xy(x_start + PADDING_LEFT, y_start + PADDING_TOP)
            pdf.multi_cell(
                col_widths[col] - 2 * PADDING_LEFT,
                LINE_HEIGHT,
                cell_texts[col],
                border=0,
                align='L',
            )
            x_start += col_widths[col]

        # Move to the next row position
        pdf.set_y(y_start + row_height)

    # Save file
    pdf.output(str(pdf_path))


def print_pdf(table_view: QTableView) -> None:
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / 'open_rmas.pdf'
    try:
        generate_pdf(table_view, pdf_path)
        os.startfile(pdf_path)
    except Exception as e:
        print(f'Error generating PDF: {e}')
