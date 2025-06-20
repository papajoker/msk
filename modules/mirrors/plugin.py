import subprocess
import sys
from enum import Enum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from .._plugin.base import PluginBase

sys.path.pop(0)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QStyle, QVBoxLayout, QWidget


class MirrorsWidget(QWidget):
    class Branch(Enum):
        STABLE = 0
        TESTING = 1
        UNSTABLE = 2
        NONE = 99

    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.status = None
        self.branch = self.get_branch()

        layout_main = QVBoxLayout()
        label = QLabel(f"Local mirror status for <b>{self.branch.name}</b> branch", parent=self, margin=20)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter or Qt.AlignmentFlag.AlignTop)
        layout_main.addWidget(label, stretch=1)

        layout_main.addLayout(self._set(), stretch=0)
        btn = QPushButton("Update mirror list", flat=True)
        btn.setEnabled(not self.status)  # can update only if first is False
        layout_main.addWidget(btn)

        self.setWindowTitle(f"Local mirror status for {self.branch.name} branch")
        self.setLayout(layout_main)

    @classmethod
    def get_branch(cls) -> Branch:
        result = subprocess.run(
            "/usr/bin/pacman-conf -r core",
            capture_output=True,
            text=True,
            shell=True,
            check=False,
        )
        for line in result.stdout.splitlines():
            if not line.startswith("Server"):
                continue
            for branch in (b for b in cls.Branch if b != cls.Branch.NONE):
                if f"/{branch.name.lower()}/" in line:
                    return branch
        return cls.Branch.NONE  # ???

    def _set(self) -> QGridLayout:
        """pacman-mirrors infos"""
        layout = QGridLayout()
        layout.setContentsMargins(20, 0, 20, 50)
        try:
            result = subprocess.run(
                "/usr/bin/pacman-mirrors",
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )
            data = result.stdout.splitlines()[2:]
        except subprocess.CalledProcessError as e:
            data = f"pacman-mirrors: {e}"

        metrics = QFontMetrics(QApplication.font())
        line_height = metrics.height() + 2

        for y, line in enumerate(data):
            parts = line.split()
            # print("->", parts)
            label = QLabel(parts[7], parent=self, margin=5)
            layout.addWidget(label, y, 0)

            ok = parts[3] == "OK"
            if self.status is None:  # chech only the first
                self.status = ok
            icon = QStyle.StandardPixmap.SP_DialogApplyButton if ok else QStyle.StandardPixmap.SP_DialogCancelButton
            ico = self.style().standardIcon(icon).pixmap(line_height, line_height)
            label = QLabel(str(ok), parent=self, margin=5, pixmap=ico)
            label.setToolTip(parts[3])
            layout.addWidget(label, y, 1)

            label = QLabel(parts[6], parent=self, margin=5)
            layout.addWidget(label, y, 2)

        return layout


class Plugin(PluginBase):
    NAME = "Mirrors manjaro"
    ORDER = 100  # 10 by 10, order in main app

    @staticmethod
    def i_enable() -> bool:
        return Path("/usr/bin/pacman-mirrors").exists()

    @staticmethod
    def get_class():
        # return class and not instance
        return MirrorsWidget
