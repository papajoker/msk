from pathlib import Path
import re
import sys
from PySide6.QtCore import Qt, QProcess, QSize
from PySide6.QtGui import QIcon, QFontDatabase, QAction, QKeySequence
from PySide6.QtWidgets import (
    QListView,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from controler.pacman import PacmanWorker
from controler.eol import EolWorker, EolManager
from model.kernel import Kernel, Kernels, IconMaker
from model.store import KernelModel, KernelModelFilter, DifferenceKernelModel
from ui.widgets import ListView, CustomToolBar
from ui.main import Window

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
