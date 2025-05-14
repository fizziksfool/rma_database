from PySide6.QtWidgets import QMessageBox


def add_customer_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add customer. Invalid entry or customer already exists.'
    QMessageBox.critical(parent, title, message)


def add_part_number_failed_message(parent) -> None:
    title = 'Error'
    message = (
        'Failed to add product number. Invalid entry or product number already exists.'
    )
    QMessageBox.critical(parent, title, message)


def add_product_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add product and number. Invalid entry or product and number already exists.'
    QMessageBox.critical(parent, title, message)


def add_rma_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add new RMA.'
    QMessageBox.critical(parent, title, message)


def add_user_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to add user. Invalid entry or user already exists.'
    QMessageBox.critical(parent, title, message)


def overwrite_record_failed_message(parent) -> None:
    title = 'Error'
    message = 'Failed to overwrite RMA record.'
    QMessageBox.critical(parent, title, message)


def open_pdf_viewer_failed_message(parent, error) -> None:
    title = 'Error'
    message = f'Failed to open printable RMA table.\n\n{str(error)}'
    QMessageBox.critical(parent, title, message)
