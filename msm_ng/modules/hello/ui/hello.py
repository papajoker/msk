import re
from pathlib import Path
from textwrap import dedent

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMenu,
    QToolButton,
    QWidget,
)


class HelloMain(QWidget):
    SIZE_ICO = 44

    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle("Manjaro " + QApplication.translate("NAME", "Hello"))
        self.setMinimumWidth(400)
        layout = QGridLayout()
        self.setLayout(layout)

        icon = QIcon(str(Path(__file__).parent.parent / "assets/manjaro.svg")).pixmap(
            72, 72
        )
        label = QLabel(margin=10, alignment=Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(icon)
        layout.addWidget(label, 0, 0, 1, 3)

        txt = dedent(
            """
            <b>Thank you for joining our community! </b>
            <p> &nbsp; &nbsp;
            We, the Manjaro Developers, hope that you will enjoy using Manjaro as much as we enjoy building it. The links below will help you get started with your new operating system. So enjoy the experience, and don't hesitate to send us your feedback.
            </p>
            """
        )
        label = QLabel(
            txt,
            textFormat=Qt.TextFormat.AutoText,
            wordWrap=True,
            margin=5,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        layout.addWidget(label, 1, 0, 1, 3)

        y = 2
        btn = QToolButton(
            parent=self,
            icon=self.get_icon("text-x-readme", self.SIZE_ICO),
            iconSize=QSize(self.SIZE_ICO, self.SIZE_ICO),
            text=self.tr("Documentation"),
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
        )
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setMinimumWidth(160)
        # btn.setIconSize(QSize(32, 32))
        menu = QMenu(btn)
        menu.addAction(self.get_icon("text-x-readme"), "readme")
        menu.addAction(self.get_icon("gnome-cd"), "release info")
        menu.addAction(self.get_icon("wikipedia"), "Wiki")
        btn.setMenu(menu)
        layout.addWidget(btn, y, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QToolButton(
            parent=self,
            text=self.tr("Support"),
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
            icon=self.get_icon("forum", self.SIZE_ICO),
            iconSize=QSize(self.SIZE_ICO, self.SIZE_ICO),
        )
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setMinimumWidth(160)
        # btn.setIconSize(QSize(32, 32))
        if menu := QMenu(self):
            action = menu.addAction(self.get_icon("forum"), "Forum")
            action.setIconVisibleInMenu(True)
            menu.addAction(self.get_icon("donate"), "Donate")
            btn.setMenu(menu)
        layout.addWidget(btn, y, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QToolButton(
            parent=self,
            text=self.tr("Project"),
            icon=self.get_icon("applications-development", self.SIZE_ICO),
            iconSize=QSize(self.SIZE_ICO, self.SIZE_ICO),
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
        )
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setMinimumWidth(160)
        # btn.setIconSize(QSize(32, 32))
        if menu := QMenu(self):
            action = menu.addAction(self.get_icon("fingerprint-gui"), "get involved")
            action.setIconVisibleInMenu(True)
            menu.addAction(self.get_icon("applications-development"), "Development")
            menu.addAction(self.get_icon("lists"), "Mailings lists")
            btn.setMenu(menu)
        layout.addWidget(btn, y, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        y = 3
        label = QLabel(
            "...", parent=self, margin=5, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(label, y, 0)

        label = QLabel(
            "...", parent=self, margin=5, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(label, y, 1)

        label = QLabel(
            "...", parent=self, margin=5, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(label, y, 2)

    def get_icon(self, name: str, size: int = 22) -> QPixmap:
        """Get an icon from the assets directory."""
        return QIcon(
            str(Path(__file__).parent.parent / "assets" / f"{name}.svg")
        ).pixmap(size, size)
        ico = self.icon_from_svg(name, size)
        return ico.pixmap(size, size)

    def icon_from_svg(self, file_name: str, size: int = 48) -> QIcon:
        """Create an icon from an SVG file."""
        svg_path = Path(__file__).parent.parent / "assets" / f"{file_name}.svg"
        if not svg_path.exists():
            raise FileNotFoundError(f"SVG file {svg_path} does not exist.")

        content = svg_path.read_text(encoding="utf-8")
        if not content:
            raise ValueError(f"SVG file {svg_path} is empty.")
        # content = content.replace("style X", "style y") ?

        width = 24
        match = re.search(r'width="(\d+)"\s+height="(\d+)"', content)
        if match:
            width = float(match.groups()[0])
        match = re.search(r'viewBox="0 0 (\d+(\.\d+)?) (\d+(\.\d+)?)"', content)
        if match:
            width = float(match.groups()[0])
        r, w = width / 2, width / 8

        # palette = QApplication.palette()
        # color = palette.color(QPalette.ColorRole.Highlight).name()
        color = "#35bf5c"
        content = content.replace(
            "</svg>",
            f'<circle cx="{r}" cy="{r}" r="{r - w + 1}" stroke="{color}" stroke-width="{w}" fill="none"/></svg>',
        )
        print(file_name)
        print()
        print(content)

        renderer = QSvgRenderer(content.encode("utf-8"))
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)
