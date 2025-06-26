from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget


class HelloMain(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle("Manjaro Hello")
        layout = QGridLayout()
        self.setLayout(layout)

        icon = QIcon(str(Path(__file__).parent.parent / "assets/manjaro.svg")).pixmap(72, 72)
        label = QLabel(margin=10, alignment=Qt.Alignment.AlignCenter)
        label.setPixmap(icon)
        layout.addWidget(label, 0, 0, 1, 3)

        y = 1
        label = QLabel("...", parent=self, margin=5, alignment=Qt.Alignment.AlignCenter)
        layout.addWidget(label, y, 0)

        label = QLabel("...", parent=self, margin=5, alignment=Qt.Alignment.AlignCenter)
        layout.addWidget(label, y, 1)

        label = QLabel("...", parent=self, margin=5, alignment=Qt.Alignment.AlignCenter)
        layout.addWidget(label, y, 2)
