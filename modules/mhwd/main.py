#!/usr/bin/env python
import subprocess
import sys

from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QFontMetrics, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QSplitter,
    QStyle,
    QTableView,
    QVBoxLayout,
    QWidget,
)


def get_status(all=True, installeds=None) -> list:
    returns = []
    if not installeds:
        installeds = []
    try:
        result = subprocess.run(
            f"/usr/bin/mhwd -l{'a' if all else 'i'}",
            capture_output=True,
            text=True,
            shell=True,
            check=True,
        )
        data = result.stdout.splitlines()[4:]
    except subprocess.CalledProcessError as e:
        print(f"ERROR ! mhwd : {e}", file=sys.stderr)
        data = ""

    for y, line in enumerate(data):
        """['network-slmodem', '2023.03.23', 'false', 'PCI']"""
        parts = line.split()
        if len(parts) == 4:
            parts[2] = True if parts[2] == "true" else False
            if all:
                parts.append(True if parts[0] in installeds else False)
            returns.append(parts)
    return sorted(returns, key=lambda m: m[0])


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        palette = QApplication.palette()
        self.color_txt = palette.color(QPalette.ColorRole.Text)
        self.color_h = palette.color(QPalette.ColorRole.Link)

    def data(self, index, role: Qt.ItemDataRole):
        status = self._data[index.row()][2]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 2:
                return "✔️" if self._data[index.row()][col] else "❌"
            if col == 4:
                return "✔️" if self._data[index.row()][col] else ""
            return self._data[index.row()][col]

        if role == Qt.ItemDataRole.ToolTipRole:
            if col == 2:
                return "free driver" if status else ""
            return self._data[index.row()][0]

        if role == Qt.ItemDataRole.ForegroundRole and status:
            return self.color_h

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        HEADERS = ("material", "version", "free", "type", "installed")
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(HEADERS[section])

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0]) if self._data else 0


class MaterialWidget(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.model = None
        self.table = QTableView()
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Vertical)
        widget = QWidget()
        layout_widget = QVBoxLayout()
        widget.setLayout(layout_widget)

        layout_main = QVBoxLayout()
        label = QLabel("Installed PCI configs", parent=self, margin=10)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter or Qt.AlignmentFlag.AlignTop)
        layout_main.addWidget(label, stretch=0)

        installeds = get_status(False)
        installeds_widget = self.collect(installeds)

        layout_widget.addLayout(installeds_widget, stretch=0)
        """
        btn = QPushButton("Update mirror list", flat=True)
        btn.setEnabled(not self.status)  # can update only if first is False
        layout_widget.addWidget(btn)
        """

        materials = get_status(True, [x[0] for x in installeds])

        self.model = TableModel(materials)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

        splitter.addWidget(widget)
        splitter.addWidget(self.table)
        layout_main.addWidget(splitter)

        self.setWindowTitle("mhwd")
        self.setLayout(layout_main)

    def collect(self, installeds) -> QGridLayout:
        """mhwd infos"""
        layout = QGridLayout()
        layout.setContentsMargins(20, 0, 20, 50)
        metrics = QFontMetrics(QApplication.font())
        line_height = metrics.height() + 2

        for y, material in enumerate(installeds):
            """['network-slmodem', '2023.03.23', 'false', 'PCI']"""

            label = QLabel(material[0], parent=self, margin=5)
            layout.addWidget(label, y, 0)

            label = QLabel(material[1], parent=self, margin=5)
            layout.addWidget(label, y, 1)

            icon = (
                QStyle.StandardPixmap.SP_DialogApplyButton
                if material[2]
                else QStyle.StandardPixmap.SP_DialogCancelButton
            )
            ico = self.style().standardIcon(icon).pixmap(line_height, line_height)
            label = QLabel(str(material[2]), parent=self, margin=5, pixmap=ico)
            layout.addWidget(label, y, 2)

            label = QLabel(material[3], parent=self, margin=5)
            layout.addWidget(label, y, 3)

        return layout


def main():
    app = QApplication([])
    win = MaterialWidget(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
