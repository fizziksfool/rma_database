from PySide6.QtWidgets import QApplication
from qt_material import build_stylesheet

app = QApplication([])

# Build the stylesheet manually
qss = build_stylesheet(theme='dark_lightgreen.xml', invert_secondary=True)

# Save it to a file
if qss is not None:
    with open('theme.qss', 'w') as f:
        f.write(qss)
