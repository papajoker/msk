import json
import subprocess
import sys
from enum import Enum
from pathlib import Path
from urllib import request

sys.path.insert(0, str(Path(__file__).parent))
from .._plugin.base import PluginBase

sys.path.pop(0)
from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt
from PySide6.QtGui import QColor, QFontMetrics
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QStyle,
    QTableView,
    QVBoxLayout,
    QWidget,
)

URL = "https://repo.manjaro.org/status.json"
'''
    _json_type = """
    [
        {
            "branches": [1,1,0],
            "country": "Australia",
            "last_sync": "06:49",
            "protocols": ["https","http"],
            "url": "https://mirror.aarnet.edu.au/pub/manjaro/"
        },
        ...
    ]
    """
'''


def get_online_status(url=URL, branch: int = 0):
    try:
        with request.urlopen(url, timeout=6) as response:
            content = response.read().decode("utf-8")
            if not content:
                return []
            for mirror in json.loads(content):
                yield (
                    mirror["url"].split("/")[2],
                    mirror["country"],
                    "9999:00" if isinstance(mirror["last_sync"], int) else mirror["last_sync"],
                    mirror["branches"][branch],
                )
    except Exception as err:
        print(f"ERROR, {url} not donloaded", err, file=sys.stderr)
        raise
    return []


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role: Qt.ItemDataRole):
        status = self._data[index.row()][3]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 3:
                return "✔️" if status == 1 else "❌"
            return self._data[index.row()][col]

        if role == Qt.ItemDataRole.ToolTipRole and col == 2:
            return self._data[index.row()][2] if self._data[index.row()][2] != "9999:00" else "none"

        if role == Qt.ItemDataRole.ForegroundRole and status != 1:
            return QColor("#d00")

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        HEADERS = ("url", "country", "last sync", "status")
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(HEADERS[section])
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0]) if self._data else 0


class MirrorsWidget(QWidget):
    class Branch(Enum):
        STABLE = 0
        TESTING = 1
        UNSTABLE = 2
        NONE = 99

    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.model = None
        self.status = None
        self.branch = self.get_branch()
        self.table = QTableView()
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Vertical)
        widget = QWidget()
        layout_widget = QVBoxLayout()
        widget.setLayout(layout_widget)

        layout_main = QVBoxLayout()
        label = QLabel(f"Local mirror status for <b>{self.branch.name}</b> branch", parent=self, margin=10)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter or Qt.AlignmentFlag.AlignTop)
        layout_main.addWidget(label, stretch=0)

        layout_widget.addLayout(self._set(), stretch=0)
        btn = QPushButton("Update mirror list", flat=True)
        btn.setEnabled(not self.status)  # can update only if first is False
        layout_widget.addWidget(btn)

        self.proxyModel = QSortFilterProxyModel()  # TODO make a custum sortProxy
        self.model = TableModel(list(get_online_status(URL, self.branch.value)))
        self.proxyModel.setSourceModel(self.model)
        self.table.setModel(self.proxyModel)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        # layout_main.addWidget(self.table)

        splitter.addWidget(widget)
        splitter.addWidget(self.table)
        layout_main.addWidget(splitter)

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
