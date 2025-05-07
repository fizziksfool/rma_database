from PySide6.QtWidgets import QDialog


class ViewRMARecordsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('RMA Records')
        self.set_window_size()

    def set_window_size(self) -> None:
        aspect_ratio: dict[str, int] = {'width': 16, 'height': 9}
        scaling_factor: int = 80
        window_width: int = aspect_ratio['width'] * scaling_factor
        window_height: int = aspect_ratio['height'] * scaling_factor
        self.setFixedSize(window_width, window_height)
