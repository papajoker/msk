from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget


class UserMain(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle("Manage users")
        layout = QGridLayout()
        self.setLayout(layout)

        users = []
        with open("/etc/passwd") as f:
            for line in f:
                if "/home/" not in line:
                    continue
                parts = line.split(":", maxsplit=6)
                users.append([f"{parts[0]} ({parts[2]}) {parts[4]}", parts[0]])

        # self.setStyleSheet("background-color: #909;")

        for y, user in enumerate(users):
            label = QLabel(user[0], parent=self, margin=20)
            layout.addWidget(label, y, 1)
            label = QLabel()
            icon = None
            path = Path(f"/var/lib/AccountsService/icons/{user[1]}")
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
            label.setPixmap(icon)
            layout.addWidget(label, y, 0)
