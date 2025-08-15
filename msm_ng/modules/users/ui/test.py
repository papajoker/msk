from pathlib import Path

from PySide6.QtCore import Qt, QLocale, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget
from .widgets import RoundIconLabel, QApplication


class UserMain(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        tr = QApplication.translate("title", "Manage users")
        self.setWindowTitle(tr)
        layout = QGridLayout()
        self.setLayout(layout)

        wheels = []
        with open("/etc/group") as f:
            """
            wheel:x:998:one,two
            """
            for line in f:
                if not line.startswith("wheel"):
                    continue
                if users := line.split(":")[-1].rstrip():
                    wheels = users.split(",")
                    break

        users = []
        with open("/etc/passwd") as f:
            """
            ['one', 'x', '1000', '984', 'One User', '/home/one', '/usr/bin/fish\n']
            ['two', 'x', '1001', '984', 'two User', '/home/two', '/usr/bin/bash\n']
            """
            for line in f:
                if "/home/" not in line:
                    continue
                parts = line.split(":", maxsplit=6)
                users.append(
                    (
                        parts[0],
                        parts[2],
                        parts[4],
                        parts[6].rstrip().split("/")[-1],
                        parts[0] in wheels,
                    )
                )

        for y, user in enumerate(users):
            label = QLabel()
            icon = None
            path = Path(f"/var/lib/AccountsService/icons/{user[0]}")
            if path.exists():
                icon = QIcon(str(path)).pixmap(48, 48)
            else:
                path = Path(f"/home/{user[1]}/.face")
                try:
                    if path.exists():
                        icon = QIcon(str(path)).pixmap(48, 48)
                except PermissionError:
                    pass

            if not icon or icon.isNull():
                icon = QIcon.fromTheme("user-unknown").pixmap(48, 48)
            icon = RoundIconLabel(self, path)  # TODO if not image ?
            layout.addWidget(icon, y, 0)

            label = QLabel(
                f"{user[0]}<br>{user[2]}",
                parent=self,
                margin=10,
                alignment=Qt.Alignment.AlignCenter,
            )

            layout.addWidget(label, y, 1)

            label = QLabel(f"{user[1]}", parent=self, margin=10)
            layout.addWidget(label, y, 2)

            label = QLabel(f"{user[3]}", parent=self, margin=10)
            layout.addWidget(label, y, 3)

            if user[4]:
                tr = self.tr("Admin")
                label = QLabel(f"<b>{tr}</b>", parent=self, margin=10)
                layout.addWidget(label, y, 4)
