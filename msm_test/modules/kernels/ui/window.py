from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow

from .main import Window

LOCAL_FILE = Path(__file__).parent / "kernels.csv"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manjaro System Kernels")
        self.setMinimumSize(400, 335)
        self.resize(780, 550)

        icon = QIcon.fromTheme(QIcon.ThemeIcon.SoftwareUpdateAvailable)
        self.setWindowIcon(icon)

        widget = Window(self)
        self.setCentralWidget(widget)
