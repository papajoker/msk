from pathlib import Path
from textwrap import dedent

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QGridLayout, QLabel, QMenu, QToolButton, QWidget


class HelloMain(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle("Manjaro Hello")
        self.setMinimumWidth(400)
        layout = QGridLayout()
        self.setLayout(layout)

        icon = QIcon(str(Path(__file__).parent.parent / "assets/manjaro.svg")).pixmap(72, 72)
        label = QLabel(margin=10, alignment=Qt.Alignment.AlignCenter)
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
            alignment=Qt.Alignment.AlignLeft,
        )
        layout.addWidget(label, 1, 0, 1, 3)

        y = 2
        btn = QToolButton(
            parent=self,
            icon=self.get_icon("text-x-readme", 32),
            iconSize=QSize(32, 32),
            text="Documentation",
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
        layout.addWidget(btn, y, 0, alignment=Qt.Alignment.AlignCenter)

        btn = QToolButton(
            parent=self,
            text="Support",
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
            icon=self.get_icon("forum", 32),
            iconSize=QSize(32, 32),
        )
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setMinimumWidth(160)
        # btn.setIconSize(QSize(32, 32))
        if menu := QMenu(self):
            action = menu.addAction(self.get_icon("forum"), "Forum")
            action.setIconVisibleInMenu(True)
            menu.addAction(self.get_icon("application-certificate"), "Donate")
            btn.setMenu(menu)
        layout.addWidget(btn, y, 1, alignment=Qt.Alignment.AlignCenter)

        btn = QToolButton(
            parent=self,
            text="Project",
            icon=self.get_icon("applications-development", 32),
            iconSize=QSize(32, 32),
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
        layout.addWidget(btn, y, 2, alignment=Qt.Alignment.AlignCenter)

        y = 3
        label = QLabel("...", parent=self, margin=5, alignment=Qt.Alignment.AlignCenter)
        layout.addWidget(label, y, 0)

        label = QLabel("...", parent=self, margin=5, alignment=Qt.Alignment.AlignCenter)
        layout.addWidget(label, y, 1)

        label = QLabel("...", parent=self, margin=5, alignment=Qt.Alignment.AlignCenter)
        layout.addWidget(label, y, 2)

    def get_icon(self, name: str, size: int = 22) -> QPixmap:
        """Get an icon from the assets directory."""
        return QIcon(str(Path(__file__).parent.parent / "assets" / f"{name}.svg")).pixmap(size, size)
